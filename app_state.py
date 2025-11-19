import time
import streamlit as st
import uuid
from config import *
from poker_engine import Deck, get_best_hand, log_complete_hand_history

def L(en: str, fr: str) -> str:
    return fr if st.session_state.get("lang", "en") == "fr" else en

def initialize_game():
    st.session_state.player_stack = INITIAL_STACK; st.session_state.ai_stack = INITIAL_STACK
    st.session_state.player_pos = "SB"; st.session_state.ai_pos = "BB"
    st.session_state.game_over = False
    st.session_state.prompt_actions = []
    st.session_state.decision_logs = []
    st.session_state.hu_uid = str(uuid.uuid4())
    st.session_state.hu_hand_seq = 0
    start_new_hand()

def start_new_hand():
    st.session_state.current_hand_uid = str(uuid.uuid4())
    st.session_state.current_hand_logged = False 
    st.session_state.consecutive_checks = 0
    st.session_state.hand_start_player_stack = st.session_state.player_stack
    st.session_state.hand_start_ai_stack = st.session_state.ai_stack
    st.session_state.player_bet = st.session_state.ai_bet = 0
    st.session_state.pot = 0
    st.session_state.bet_to_match = st.session_state.last_raise = 0
    st.session_state.last_aggressor = None
    st.session_state.prompt_actions = []
    st.session_state.decision_logs = []
    st.session_state.show_ai_hand = False
    if st.session_state.player_stack <= 0 or st.session_state.ai_stack <= 0:
        st.session_state.game_over = True; return
    st.session_state.player_pos, st.session_state.ai_pos = st.session_state.ai_pos, st.session_state.player_pos
    st.session_state.player_start_stack = st.session_state.player_stack; st.session_state.ai_start_stack = st.session_state.ai_stack
    deck = Deck(); st.session_state.deck = deck
    st.session_state.player_hand = deck.deal(2); st.session_state.ai_hand = deck.deal(2)
    st.session_state.board = []; st.session_state.pot = 0; st.session_state.street_num = 0; st.session_state.winner = None
    log_keys = list(STREET_MAP.values()) + ['showdown']; st.session_state.action_log = {key: [] for key in log_keys}
    st.session_state.is_all_in = False
    if st.session_state.player_pos == "SB":
        sb_p, bb_p, sb_a, bb_a = "player", "ai", SB, BB
        st.session_state.player_bet, st.session_state.ai_bet = SB, BB
    else:
        sb_p, bb_p, sb_a, bb_a = "ai", "player", SB, BB
        st.session_state.ai_bet, st.session_state.player_bet = SB, BB
    st.session_state[f"{sb_p}_stack"] -= sb_a; st.session_state[f"{bb_p}_stack"] -= bb_a
    st.session_state.pot = sb_a + bb_a; st.session_state.bet_to_match = BB
    st.session_state.last_raise = BB; st.session_state.turn = sb_p
    street_name = STREET_MAP[st.session_state.street_num]
    player_label = L("Player", "Le Joueur")
    if sb_p == "player":
        st.session_state.action_log[street_name].append(f"{player_label} mise {SB}.")
        st.session_state.action_log[street_name].append(f"L'IA mise {BB}.")
    else:
        st.session_state.action_log[street_name].append(f"L'IA mise {SB}.")
        st.session_state.action_log[street_name].append(f"{player_label} mise {BB}.")
    player_is_all_in = st.session_state.player_stack <= 0; ai_is_all_in = st.session_state.ai_stack <= 0
    if player_is_all_in or ai_is_all_in:
        st.session_state.action_log['preflop'].append(
                L("A player is all-in with the blinds!", "Un joueur est à tapis avec les blindes !")
        )
        effective_bet = min(st.session_state.player_bet, st.session_state.ai_bet)
        if st.session_state.player_bet > effective_bet:
            refund = st.session_state.player_bet - effective_bet
            st.session_state.player_stack += refund; st.session_state.pot -= refund; st.session_state.player_bet -= refund
        elif st.session_state.ai_bet > effective_bet:
            refund = st.session_state.ai_bet - effective_bet
            st.session_state.ai_stack += refund; st.session_state.pot -= refund; st.session_state.ai_bet -= refund
        run_out_board_and_showdown()

def next_street():
    st.session_state.consecutive_checks = 0
    st.session_state.last_aggressor = None
    st.session_state.street_num += 1
    if st.session_state.street_num == 1: st.session_state.board = st.session_state.deck.deal(3)
    elif st.session_state.street_num in [2, 3]: st.session_state.board.extend(st.session_state.deck.deal(1))

    if st.session_state.street_num > 3:
        handle_showdown()
    else:
        st.session_state.turn = "player" if st.session_state.player_pos == "BB" else "ai"
        st.session_state.bet_to_match = 0; st.session_state.player_bet = 0; st.session_state.ai_bet = 0; st.session_state.last_raise = 0

def handle_showdown():
    s = st.session_state
    p_score = get_best_hand(s.player_hand, s.board); a_score = get_best_hand(s.ai_hand, s.board)
    player_invested = s.player_start_stack - s.player_stack; ai_invested = s.ai_start_stack - s.ai_stack
    common_pot = min(player_invested, ai_invested) * 2
    if p_score > a_score: winner, stack_update = "player", "player_stack"
    elif a_score > p_score: winner, stack_update = "ai", "ai_stack"
    else: winner, stack_update = "tie", None
    s.winner = winner
    s.show_ai_hand = True
    if winner == "tie": s.player_stack += common_pot // 2; s.ai_stack += common_pot // 2
    else: s[stack_update] += common_pot
    if player_invested > ai_invested: s.player_stack += player_invested - ai_invested
    elif ai_invested > player_invested: s.ai_stack += ai_invested - player_invested
    s.action_log["showdown"].append(L(f"Winner: {winner}.", f"Gagnant: {winner}."))
    s.turn = None
    gain = s.player_stack - s.hand_start_player_stack
    if gain > 0:
        who = s.get('display_name') or s.get('pseudo') or L('the player','Le joueur')
        s.action_log["showdown"].append(L(f"Result: {who} wins {gain}.",
                                      f"Résultat : {who} gagne {gain}."))
    elif gain < 0:
        s.action_log["showdown"].append(L(f"Result: spinGPT wins {-gain}.",
                                      f"Résultat : spinGPT gagne {-gain}."))
    else:
        s.action_log["showdown"].append(L("Result: split pot.", "Résultat : partage du pot."))

    log_complete_hand_history(winner)

def run_out_board_and_showdown():
    st.session_state.turn = None
    cards_to_deal = 5 - len(st.session_state.board)
    if cards_to_deal > 0: st.session_state.board.extend(st.session_state.deck.deal(cards_to_deal))
    handle_showdown()

def process_action(actor: str, action: str, amount: int = 0):
    opponent = "ai" if actor == "player" else "player"
    name = st.session_state.get("display_name") or st.session_state.get("pseudo") or L("Player", "Le Joueur")
    actor_name = name if actor == "player" else "L'IA"
    street_name = STREET_MAP[st.session_state.street_num]
    stack = st.session_state[f"{actor}_stack"]

    st.session_state.setdefault("consecutive_checks", 0)
    st.session_state.setdefault("prompt_actions", [])
    st.session_state.setdefault("last_aggressor", None)

    def record_prompt_action():
        hero_tag = "H"
        vill_tag = st.session_state.player_pos
        actor_tag = hero_tag if actor == "ai" else vill_tag
        if action == "check": sym = "x"
        elif action == "fold": sym = "f"
        elif action == "call": sym = "c"
        elif action in ("bet", "raise"): sym = ("r" if action == "raise" else "b") + f"{amount/BB:g}"
        else: sym = "a"
        st.session_state.prompt_actions.append((st.session_state.street_num, actor_tag, sym))

    if action == "call" and st.session_state.bet_to_match == st.session_state[f"{actor}_bet"]:
        action = "check"

    if action == "fold":
        s = st.session_state
        record_prompt_action()
        st.session_state.winner = opponent
        st.session_state[f"{opponent}_stack"] += st.session_state.pot
        st.session_state.action_log[street_name].append(f"{actor_name} se couche.")
        st.session_state.turn = None
        net = s.ai_stack - s.hand_start_ai_stack if opponent == "ai" else s.player_stack - s.hand_start_player_stack
        who = (s.get('display_name') or s.get('pseudo') or L('The player','Le joueur'))
        s.action_log["showdown"].append(
            L(f"Result: {who} wins {net}.", f"Résultat : {who} gagne {net}.")
        )

        log_complete_hand_history(opponent)

    elif action == "check":
        st.session_state.action_log[street_name].append(f"{actor_name} check.")

    elif action == "call":
        to_call = st.session_state.bet_to_match - st.session_state[f"{actor}_bet"]
        paid = min(to_call, stack)
        st.session_state[f"{actor}_stack"] -= paid
        st.session_state[f"{actor}_bet"] += paid
        st.session_state.pot += paid
        st.session_state.action_log[street_name].append(f"{actor_name} paie {paid}.")

    elif action in ("bet", "raise"):
        total_bet = min(amount, stack + st.session_state[f"{actor}_bet"])
        to_pay = total_bet - st.session_state[f"{actor}_bet"]
        st.session_state[f"{actor}_stack"] -= to_pay
        st.session_state[f"{actor}_bet"] = total_bet
        st.session_state.pot += to_pay
        st.session_state.last_raise = total_bet - st.session_state.bet_to_match
        st.session_state.bet_to_match = total_bet
        st.session_state.last_aggressor = actor
        verb = "relance à" if action == "raise" else "mise"
        st.session_state.action_log[street_name].append(f"{actor_name} {verb} {total_bet}.")

    else:
        raise ValueError(f"Action inconnue : {action}")

    st.session_state.consecutive_checks = (st.session_state.consecutive_checks + 1 if action == "check" else 0)

    if (st.session_state.player_stack <= 0) or (st.session_state.ai_stack <= 0):
        st.session_state.is_all_in = True
    if st.session_state.is_all_in and action == "call":
        record_prompt_action()
        run_out_board_and_showdown()
        return

    def betting_round_closed() -> bool:
        if st.session_state.street_num == 0:
            mises_equal = st.session_state.player_bet == st.session_state.ai_bet
            if action == "check" and st.session_state[f"{actor}_pos"] == "BB" and mises_equal: return True
            if (action == "call" and mises_equal and st.session_state.last_aggressor and actor != st.session_state.last_aggressor): return True
            return False
        if action == "call": return True
        if action == "check" and st.session_state.consecutive_checks >= 2: return True
        return False

    if betting_round_closed():
        record_prompt_action()
        if st.session_state.street_num == 3:
            handle_showdown()
        else:
            next_street()
    else:
        record_prompt_action()
        st.session_state.turn = opponent