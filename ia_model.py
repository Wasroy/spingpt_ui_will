# ia_model.py
import math, re, torch, streamlit as st
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from config import MODEL_PATH

def L(en: str, fr: str) -> str:
    import streamlit as st
    return fr if st.session_state.get("lang","en") == "fr" else en

class PokerModel:
    def __init__(self, hf_token: str):
        q_conf = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH, token=hf_token, use_fast=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            device_map="auto",
            quantization_config=q_conf,
            torch_dtype="auto",
            token=hf_token,
            trust_remote_code=True
        )
        self.model.eval()

        # ==== IDs & grammaire ====
        self.eos_id = self.tokenizer.eos_token_id
        self.space_id = self._tok_id(" ")
        self.dot_id = self._tok_id(".")
        self.digit_ids = {d: self._tok_id(str(d)) for d in range(10)}
        self.head_ids = {s: self._tok_id(s) for s in ["x", "f", "c", "a", "b", "r"]}
        try:
            t = self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
            self.term_id = self.eos_id if (t is None or t == self.tokenizer.unk_token_id) else int(t)
        except Exception:
            self.term_id = self.eos_id

        self.re_prefix = re.compile(r"^(?:[xfc]|[abr](?:\d+)?(?:\.\d*)?)?$")
        self.re_final  = re.compile(r"^(?:[xfc]|a\d+(?:\.\d+)?|b\d+(?:\.\d+)?|r\d+(?:\.\d+)?)$")

    # ---------- utils ----------
    def _tok_id(self, s: str):
        try:
            ids = self.tokenizer.encode(s, add_special_tokens=False)
            return ids[0] if len(ids) == 1 else None
        except Exception:
            return None

    def _encode_prompt(self, prompt: str):
        tpl = [{"role": "user", "content": prompt}]
        return self.tokenizer.apply_chat_template(
            tpl, add_generation_prompt=True, return_tensors="pt"
        ).to(self.model.device)

    @staticmethod
    def _norm_action(text: str) -> str:
        t = text.strip().replace(" ", "")
        return "a" if t.startswith("a") else t

    # ---------- greedy + proba exacte (incl. terminator) ----------
    @torch.no_grad()
    def _generate_action_and_prob(self, prompt: str, max_new_tokens: int = 16):
        ids = self._encode_prompt(prompt)
        txt = ""
        logp_tokens = 0.0
        for _ in range(max_new_tokens):
            out = self.model(input_ids=ids, attention_mask=torch.ones_like(ids))
            probs = F.softmax(out.logits[:, -1, :].float(), dim=-1)[0]

            cand = set(filter(lambda x: x is not None,
                              list(self.head_ids.values()) +
                              list(self.digit_ids.values()) + [self.dot_id]))
            topv, topi = torch.topk(probs, k=min(50, probs.numel()))
            cand |= set(topi.tolist())

            for tid in (self.term_id, self.eos_id, self.space_id):
                if isinstance(tid, int) and tid in cand:
                    cand.remove(tid)

            best_tid, best_p = None, 0.0
            for tid in cand:
                p_tok = float(probs[tid])
                if p_tok <= 0.0:
                    continue
                tstr = self.tokenizer.decode([tid])
                new_txt = (txt + tstr).replace(" ", "")
                if self.re_prefix.match(new_txt) and p_tok > best_p:
                    best_tid, best_p = tid, p_tok

            p_term = float(probs[self.term_id]) if (txt and self.re_final.match(txt)) else 0.0
            if p_term >= best_p and p_term > 0.0 and txt:
                return txt, math.exp(logp_tokens) * p_term

            if best_tid is None:
                break

            ids = torch.cat([ids, torch.tensor([[best_tid]], device=ids.device)], dim=-1)
            logp_tokens += math.log(best_p)
            txt = (txt + self.tokenizer.decode([best_tid])).replace(" ", "")

        if txt and self.re_final.match(txt):
            out_last = self.model(input_ids=ids, attention_mask=torch.ones_like(ids))
            probs_last = F.softmax(out_last.logits[:, -1, :].float(), dim=-1)[0]
            p_term = float(probs_last[self.term_id]) if isinstance(self.term_id, int) else 0.0
            if p_term > 0.0:
                return txt, math.exp(logp_tokens) * p_term
        return "", 0.0

    # ---------- énumération disjointe ----------
    @torch.no_grad()
    def enumerate_actions_ge(self, prompt: str, min_prob: float = 0.05, max_new_tokens: int = 12, tok_topk: int = 20):
        ids0 = self._encode_prompt(prompt)
        log_thr = math.log(min_prob)
        agg = {}
        stack = [(ids0, 0.0, "", 0)]
        while stack:
            ids, logp, txt, depth = stack.pop()
            if depth >= max_new_tokens:
                continue
            out = self.model(input_ids=ids, attention_mask=torch.ones_like(ids))
            probs = F.softmax(out.logits[:, -1, :].float(), dim=-1)[0]

            if txt and self.re_final.match(txt):
                p_term = float(probs[self.term_id]) if isinstance(self.term_id, int) else 0.0
                if p_term > 0.0:
                    p_exact = math.exp(logp) * p_term
                    if p_exact >= min_prob:
                        key = self._norm_action(txt)
                        agg[key] = agg.get(key, 0.0) + p_exact

            must = set(filter(lambda x: x is not None,
                            list(self.head_ids.values()) +
                            list(self.digit_ids.values()) + [self.dot_id]))
            topv, topi = torch.topk(probs, k=min(tok_topk, probs.numel()))
            cand = must | set(topi.tolist())

            for tid in (self.term_id, self.eos_id, self.space_id):
                if isinstance(tid, int) and tid in cand:
                    cand.remove(tid)

            for tid in cand:
                p_tok = float(probs[tid])
                if p_tok <= 0.0:
                    continue
                tstr = self.tokenizer.decode([tid])
                new_txt = (txt + tstr).replace(" ", "")
                if not self.re_prefix.match(new_txt):
                    continue
                new_logp = logp + math.log(p_tok)
                if new_logp < log_thr:
                    continue
                new_ids = torch.cat([ids, torch.tensor([[tid]], device=ids.device)], dim=-1)
                stack.append((new_ids, new_logp, new_txt, depth + 1))

        items = [{"action": k, "p": v} for k, v in agg.items() if v >= min_prob]
        items.sort(key=lambda x: x["p"], reverse=True)
        return items

    @torch.no_grad()
    def act_over_threshold(self, prompt: str, min_select_prob: float = 0.05,
                       max_new_tokens: int = 12, allowed_actions=None, sample=True):
        full_alts = self.enumerate_actions_ge(prompt, min_prob=min_select_prob,
                                          max_new_tokens=max_new_tokens, tok_topk=20)
        if allowed_actions is not None:
            allowed = set(allowed_actions)
            full_alts = [a for a in full_alts if a["action"] in allowed]

        cand = [a for a in full_alts if a["p"] >= min_select_prob]
        if not cand:
            greedy_text, _ = self._generate_action_and_prob(prompt, max_new_tokens=max_new_tokens)
            return greedy_text, [{"action": greedy_text, "p": 1.0}], []

        s = sum(a["p"] for a in cand)
        used_dist = [{"action": a["action"], "p": (a["p"] / s)} for a in cand]

        if sample:
            probs = torch.tensor([x["p"] for x in used_dist], device=self.model.device)
            idx = torch.multinomial(probs, 1).item()
        else:
            idx = int(torch.argmax(torch.tensor([x["p"] for x in used_dist])).item())

        chosen = used_dist[idx]["action"]
        return chosen, used_dist, full_alts

    @torch.no_grad()
    def infer(self, prompt: str, min_prob: float = 0.01, max_new_tokens: int = 16):
        action_raw, p_raw = self._generate_action_and_prob(prompt, max_new_tokens=max_new_tokens)
        alts = self.enumerate_actions_ge(prompt, min_prob=min_prob, max_new_tokens=max_new_tokens)
        key = self._norm_action(action_raw)
        p_from = next((a["p"] for a in alts if a["action"] == key), None)
        if p_from is not None:
            p_raw = p_from
        return action_raw, p_raw, alts

    # ===== API pour l’app =====

    #avec distribution
    def get_action(self, prompt: str) -> str:
        chosen, _, _ = self.get_action_with_dists(prompt)
        return chosen
    #sans distribution
    """def get_action(self, prompt: str, max_new_tokens: int = 6) -> str:
        messages = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        ).to(self.model.device)
        with torch.inference_mode():
            out = self.model.generate(
                inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
                return_dict_in_generate=False,
                output_scores=False,
            )
        text = self.tokenizer.decode(out[0][inputs.shape[-1]:], skip_special_tokens=True).strip()
        return self._norm_action(text) or "f"
        """


    def get_action_with_dists(self, prompt: str,
                          min_select_prob: float = 0.12, max_new_tokens: int = 6):
        return self.act_over_threshold(
            prompt,
            min_select_prob=min_select_prob,
            max_new_tokens=max_new_tokens,
            allowed_actions=None,
            sample=True
        )


@st.cache_resource
def load_poker_model(hf_token: str, cache_version: int = 2):
    # cache_version permet de forcer un rechargement quand tu modifies ce fichier
    if not hf_token:
        st.error("Token HF non trouvé !"); st.stop()
    with st.spinner("Chargement du modèle spinGPT…"):
        model = PokerModel(hf_token)
    return model
