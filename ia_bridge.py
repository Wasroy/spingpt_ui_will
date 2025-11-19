import streamlit as st
import re, json, time, os
from config import *
from app_state import process_action

# ── 1. Helper pour formater une carte ───────────────────────────────
def _card_to_str(c):
    """
    Transforme un objet Card dont c.name vaut par ex. "6♥" ou "Kh"
    en "6h" ou "kh" (rang majuscule, suit en minuscule parmi {c,d,h,s}).
    """
    nm = c.name
    # le dernier caractère est toujours le symbole ou la lettre du suit
    rank_part = nm[:-1]
    suit_part = nm[-1]
    # mapping Unicode → lettre
    suit_map = {'♣':'c', '♠':'s', '♥':'h', '♦':'d',
                'C':'c', 'S':'s','H':'h','D':'d'}
    suit = suit_map.get(suit_part, suit_part.lower())
    return f"{rank_part}{suit}"

# ── 2. Prompt builder corrigé ────────────────────────────────────────
def _board_tag(idx: int) -> str:
    b = st.session_state.board
    if idx == 1 and len(b) >= 3:
        return "".join(_card_to_str(c) for c in b[:3])
    if idx == 2 and len(b) >= 4:
        return _card_to_str(b[3])
    if idx == 3 and len(b) >= 5:
        return _card_to_str(b[4])
    return ""

# ── 2. Prompt builder corrigé ───────────────────────────────────
def generate_prompt_for_ai() -> str:
    s = st.session_state
    hero_pos, vill_pos = s.ai_pos, s.player_pos
    hero_bb = s.ai_stack / BB
    vill_bb = s.player_stack / BB
    hand    = "".join(_card_to_str(c) for c in s.ai_hand)

    header = (
        f"pos:H={hero_pos} "
        f"stacks:H={hero_bb:.1f},{vill_pos}={vill_bb:.1f} "
        f"hand:{hand}"
    )

    # Regroupe toutes les actions par street
    street_name = {0: "pre", 1: "flop", 2: "turn", 3: "river"}
    grouped = {i: [] for i in range(4)}
    for st_num, tag, symb in s.prompt_actions:
        grouped[st_num].append(f"{tag} {symb}")

    history = []
    for i in range(s.street_num + 1):
        tag = street_name[i]

        # ---- CAS PRÉFLOP ----------------------------------------------------
        if i == 0:
            if not grouped[0]:
                # ⤷  Hero en SB → on n’ajoute **rien** ici
                if hero_pos == "SB":
                    continue
                # ⤷  Hero en BB → on garde le marqueur d’attente «pre:H»
                history.append("pre:H")
            else:
                first, *rest = grouped[0]
                part = f"{tag}:{first}"
                if rest:
                    part += "," + ",".join(rest)
                history.append(part)
        # ---- CAS POSTFLOP ---------------------------------------------------
        else:
            board = _board_tag(i)
            actions = ",".join(grouped[i])
            part = f"{tag}:{board} {actions}".strip()
            history.append(part)

    # Concatène et termine par «H:»
    return " | ".join([header] + history) + " H:"

def translate_action_for_app(model_action: str, state):
    """
    Convertit l’action brute venant du modèle en (« action », montant)
    compréhensible par process_action().

    Renvoie par ex. ("raise", 600) ou ("call", 0).
    """
    act = model_action.lower().strip()
    amount_to_call = state.bet_to_match - state.ai_bet

    # ────────────────────────────────────────────────────────────
    #  1) Actions simples : fold, check, call
    # ────────────────────────────────────────────────────────────
    if act.startswith("x"):                          # « check »
        if amount_to_call > 0:                       # check illégal → call
            state.action_log[STREET_MAP[state.street_num]].append(
                "IA-CORRECTION: Check illégal -> Call"
            )
            return "call", 0
        return "check", 0

    if act.startswith("f"):
        return "fold", 0
    if act.startswith("c"):
        return "call", 0

    #Call All-in de l'adversaire
    if state.player_stack == 0 and amount_to_call > 0:
        return "call", 0


    # ────────────────────────────────────────────────────────────
    #  2) ALL-IN :  a   ou   aX   (X en big blinds)
    # ────────────────────────────────────────────────────────────
    if act.startswith("a"):
        num = act[1:]            # ce qu’il y a après le « a » (éventuellement vide)
        if num:                  # aX  (all-in “plafonné” à X BB)
            try:
                x_bb = float(num)
            except ValueError:
                state.action_log[STREET_MAP[state.street_num]].append(
                    f"IA-CORRECTION: Action '{act}' inconnue -> Fold"
                )
                return "fold", 0
            # Cas spécial première action préflop : on ajoute la blinde déjà postée
            if state.street_num == 0 and state.bet_to_match == BB:
                posted = 0.5 if state.ai_pos == "SB" else 1
                total_bb = posted + x_bb
            else:
                total_bb = x_bb
            chips = round(total_bb * BB)
            chips = state.ai_stack + state.ai_bet
        else:               # juste « a » → all-in intégral
            chips = state.ai_stack + state.ai_bet

        is_raise = state.bet_to_match > 0

        full_stack = state.ai_stack + state.ai_bet
        if is_raise and chips < state.bet_to_match + state.last_raise:
            if chips == full_stack:                 # tapis exact → call all-in
                return "call", 0

        if is_raise:
            min_raise = state.bet_to_match + state.last_raise
            if chips < min_raise and chips < full_stack:
                state.action_log[STREET_MAP[state.street_num]].append(
                    f"IA-CORRECTION: Relance '{act}' illégale -> Call"
                )
                return "call", 0

        return ("raise" if is_raise else "bet", chips)

    # ────────────────────────────────────────────────────────────
    #  3) Bet / Raise classiques  bX  ou  rX
    # ────────────────────────────────────────────────────────────
    match = re.match(r'^(b|r)([0-9.]+)$', act)
    if not match:
        state.action_log[STREET_MAP[state.street_num]].append(
            f"IA-CORRECTION: Action '{act}' inconnue -> Fold"
        )
        return "fold", 0

    letter, amount_str = match.groups()
    try:
        x_bb = float(amount_str)
    except ValueError:
        state.action_log[STREET_MAP[state.street_num]].append(
            f"IA-CORRECTION: Montant '{amount_str}' invalide -> Fold"
        )
        return "fold", 0

    # Ajout de la blinde déjà postée pour la 1ʳᵉ action préflop (SB ou BB)
    if state.street_num == 0 and state.bet_to_match == BB:
        posted = 0.5 if state.ai_pos == "SB" else 1
        total_bb = posted + x_bb
    else:
        total_bb = x_bb

    chips = round(total_bb * BB)
    is_raise = state.bet_to_match > 0

    # Vérif min-raise (si ce n’est pas un all-in complet)
    if is_raise:
        min_raise = state.bet_to_match + state.last_raise
        if chips < min_raise and chips < state.ai_stack + state.ai_bet:
            state.action_log[STREET_MAP[state.street_num]].append(
                f"IA-CORRECTION: Relance '{act}' illégale -> Call"
            )
            return "call", 0

    return ("raise" if is_raise else "bet", chips)


def make_instruction() -> str:
    s = st.session_state
    hero_pos, vill_pos = s.ai_pos, s.player_pos
    hero_bb  = s.ai_stack   / BB
    vill_bb  = s.player_stack / BB
    hand     = ''.join(c.name for c in s.ai_hand)

    # Pour l’instant on renvoie position + stacks + hand :H:
    return (
        f"pos:H={hero_pos} "
        f"stacks:H={hero_bb:.1f},{vill_pos}={vill_bb:.1f} "
        f"hand:{hand} H:"
    )

def get_ai_action(model):
    prompt = generate_prompt_for_ai()

    # avec distribution
    chosen, used_dist, _ = model.get_action_with_dists(prompt)
    pd = [[d["action"], round(float(d["p"]), 2)] for d in used_dist]

    #sans distribution
    #chosen = model.get_action(prompt)
    #pd = [[chosen, 1.0]]


    s = st.session_state
    user = s.get("sb_user")
    pseudo = s.get("display_name") or s.get("pseudo") or ("Anonyme" if s.get("anonymous", True) else "Anonyme")
    #email = getattr(user, "email", None) if user else None

    rec_short = {
        "t": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "pp": pseudo,
        #"pe": email,
        "p": prompt,
        "a": chosen,
        "pd": pd
    }
    _append_decision_record_short(rec_short)

    action, amount = translate_action_for_app(chosen, st.session_state)
    process_action("ai", action, amount)

def _load_decisions_meta():
    s = st.session_state
    if "decisions_meta_cache" in s:
        return s["decisions_meta_cache"]
    try:
        with open(DECISIONS_META_FILE, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except Exception:
        meta = {"file_idx": 1, "count_in_file": 0}
    s["decisions_meta_cache"] = meta
    return meta

def _save_decisions_meta(meta, force=False):
    s = st.session_state
    s["decisions_meta_cache"] = meta
    if force:
        try:
            with open(DECISIONS_META_FILE, "w", encoding="utf-8") as f:
                json.dump(meta, f, separators=(",", ":"))
        except Exception:
            pass

def _current_decisions_path(meta):
    base_dir = os.path.dirname(DECISIONS_LOG_FILE)
    stem = "decisions_log_{:06d}.jsonl".format(meta["file_idx"])
    return os.path.join(base_dir, stem)

def _append_decision_record_short(rec_short):
    os.makedirs(os.path.dirname(DECISIONS_LOG_FILE), exist_ok=True)
    meta = _load_decisions_meta()
    path = _current_decisions_path(meta)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec_short, ensure_ascii=False, separators=(",", ":")) + "\n")
        meta["count_in_file"] = meta.get("count_in_file", 0) + 1
        if meta["count_in_file"] >= DECISIONS_CHUNK_SIZE:
            meta["file_idx"] += 1
            meta["count_in_file"] = 0
            _save_decisions_meta(meta, force=True)
        else:
            _save_decisions_meta(meta, force=False)
    except Exception as e:
        st.sidebar.error(f"Erreur log décision: {e}")

