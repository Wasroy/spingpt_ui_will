import random, json, streamlit as st, time
import os
from collections import Counter
from itertools import combinations
from config import *
from supabase import create_client
from supabase_utils import insert_hand_minimal

def L(en: str, fr: str) -> str:
    import streamlit as st
    return fr if st.session_state.get("lang","en") == "fr" else en

class Card:
    def __init__(self, rank, suit): self.rank_val = RANKS[rank]; self.suit_name = SUITS[suit]; self.name = f"{rank}{suit[0].lower()}"
    def __str__(self): return f"{RANK_NAMES[self.rank_val]}{SUIT_ICONS[self.suit_name]}"

class Deck:
    def __init__(self): self.cards = [Card(r, s) for r in RANKS for s in SUITS]; random.shuffle(self.cards)
    def deal(self, num_cards=1): return [self.cards.pop() for _ in range(num_cards)]

def evaluate_hand(hand):
    ranks = sorted([c.rank_val for c in hand], reverse=True); suits = {c.suit_name for c in hand}
    is_flush = len(suits) == 1; is_straight = len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4)
    if ranks == [14, 5, 4, 3, 2]: is_straight = True; ranks = [5, 4, 3, 2, 1]
    rc = Counter(ranks); c = sorted(rc.values(), reverse=True)
    if is_straight and is_flush: return (8, ranks)
    if c[0]==4: return (7, sorted(rc, key=rc.get, reverse=True))
    if c==[3,2]: return (6, sorted(rc, key=rc.get, reverse=True))
    if is_flush: return (5, ranks)
    if is_straight: return (4, ranks)
    if c[0]==3: return (3, sorted(rc, key=rc.get, reverse=True))
    if c==[2,2,1]: return (2, sorted(rc, key=rc.get, reverse=True))
    if c[0]==2: return (1, sorted(rc, key=rc.get, reverse=True))
    return (0, ranks)

def get_best_hand(hole, board):
    return max([evaluate_hand(list(c)) for c in combinations(hole + board, 5)]) if len(hole + board) >= 5 else (0, [])

def _card_to_str_simple(c):
    """Helper pour convertir un objet Card en chaîne simple comme 'As' ou 'Th'."""
    rank = RANK_NAMES[c.rank_val]
    suit = c.suit_name[0]
    return f"{rank}{suit}"

def log_complete_hand_history(winner):
    s = st.session_state

    if s.get("current_hand_logged"):
        return
    s.current_hand_logged = True

    s.hu_hand_seq = int(s.get("hu_hand_seq") or 0) + 1

    played_at_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    player_profit = s.player_stack - s.hand_start_player_stack
    ai_profit     = s.ai_stack     - s.hand_start_ai_stack

    row = {
        "ts": played_at_iso,
        "pp": s.get("display_name") or s.get("pseudo") or ("Anonyme" if s.get("anonymous", True) else "Anonyme"),
        "w": (winner, max(int(player_profit if winner == "player" else ai_profit), 0)),
        "ai": (s.ai_pos, s.ai_start_stack),
        "h": {
            "p": "".join(_card_to_str_simple(c) for c in s.player_hand),
            "ai": "".join(_card_to_str_simple(c) for c in s.ai_hand)
        },
        "b": "".join(_card_to_str_simple(c) for c in s.board),
        "ph": s.prompt_actions
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception as e:
        st.sidebar.error(L(f"Error while saving hand log: {e}", f"Erreur lors de la sauvegarde du log: {e}"))

    # insert minimal côté DB
    try:
        insert_hand_minimal(
            played_at_iso,
            s.get("display_name") or s.get("pseudo") or "Anonymous",
            row
        )
    except Exception as e:
        st.sidebar.error(L(f"Supabase insert error: {e}", f"Supabase insert erreur: {e}"))

