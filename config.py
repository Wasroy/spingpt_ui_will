import os
BB = 100
SB = 50
INITIAL_STACK = 25 * BB
MODEL_PATH = "model"  
# LOG_DIR adapté pour Windows et Linux
USER = os.getenv("USER") or os.getenv("USERNAME") or "default"
if os.name == "nt":  # Windows
    LOG_DIR = os.path.join(os.getenv("APPDATA", "."), "spinGPT", "logs", "25BB")
else:  # Linux/Mac
    LOG_DIR = "/mnt/ssd/users/{user}/spinGPT/logs/25BB".format(user=USER)
LOG_FILE = os.path.join(LOG_DIR, "hands_log.jsonl")
DECISIONS_LOG_FILE = os.path.join(LOG_DIR, "decisions_log.jsonl")
DECISIONS_CHUNK_SIZE = 5000
DECISIONS_META_FILE = os.path.join(LOG_DIR, "decisions_meta.json")
os.makedirs(LOG_DIR, exist_ok=True)
SUITS = {
    's': 'spades',
    'c': 'clubs',
    'd': 'diamonds',
    'h': 'hearts',
}

SUIT_ICONS = {
    'spades':   '♠',
    'clubs':    '♣',
    'diamonds': '♦',
    'hearts':   '♥',
}

# ──────────────────────────────────────────────────────────────
#  Palette 4-couleurs pour l'IHM (Charte SpinGPT)
# ──────────────────────────────────────────────────────────────
SUIT_DISPLAY = {
    's': ('♠', '#2C2C2C'),   # pique   – gris foncé (texte courant SpinGPT)
    'c': ('♣', '#0A2A43'),   # trèfle  – bleu profond SpinGPT
    'd': ('♦', '#0D3454'),   # carreau – bleu clair (variation bleu SpinGPT)
    'h': ('♥', '#C13A3A'),   # cœur    – rouge poker SpinGPT
}
RANKS = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
RANK_NAMES = {v: k for k, v in RANKS.items()}
STREET_MAP = {0: "preflop", 1: "flop", 2: "turn", 3: "river"}

# Mode UI-only : désactive le backend (Supabase + IA) pour travailler uniquement sur l'apparence
UI_ONLY_MODE = os.getenv("UI_ONLY_MODE", "false").lower() in ("true", "1", "yes")

SUPABASE_URL = os.getenv("SUPABASE_URL") if not UI_ONLY_MODE else "mock://supabase"
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") if not UI_ONLY_MODE else "mock-key"
HF_TOKEN = os.getenv("HF_TOKEN") if not UI_ONLY_MODE else "mock-token"