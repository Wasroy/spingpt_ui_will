# supabase_utils.py
from __future__ import annotations

import os
from typing import Optional, Tuple

import streamlit as st
from supabase import create_client

# --- lecture config avec fallback env ---
try:
    from config import SUPABASE_URL as CFG_URL, SUPABASE_ANON_KEY as CFG_KEY
except Exception:
    CFG_URL = None
    CFG_KEY = None

_CLIENT = None

def _env_or_cfg() -> Tuple[Optional[str], Optional[str]]:
    url = os.getenv("SUPABASE_URL") or CFG_URL
    key = os.getenv("SUPABASE_ANON_KEY") or CFG_KEY
    return url, key

def sb():
    global _CLIENT
    url, key = _env_or_cfg()
    if not url or not key:
        return None
    if _CLIENT is None:
        _CLIENT = create_client(url, key)
    try:
        uid, email, jwt = _get_auth_from_session()
        if jwt:
            _CLIENT.postgrest.auth(jwt)
    except Exception:
        pass
    return _CLIENT


def _get_auth_from_session():
    """
    Récupère uid/email/jwt depuis st.session_state, accepte dicts/objets.
    """
    s = st.session_state
    user = s.get("sb_user")
    session = s.get("sb_session")
    uid = email = jwt = None

    if isinstance(user, dict):
        uid   = user.get("id") or user.get("user", {}).get("id")
        email = user.get("email") or user.get("user", {}).get("email")
    else:
        try:
            uid = getattr(user, "id", None) or getattr(getattr(user, "user", None), "id", None)
            email = getattr(user, "email", None) or getattr(getattr(user, "user", None), "email", None)
        except Exception:
            pass

    if isinstance(session, dict):
        jwt = session.get("access_token") or session.get("accessToken")
    else:
        try:
            jwt = getattr(session, "access_token", None) or getattr(session, "accessToken", None)
        except Exception:
            pass

    return uid, email, jwt

def get_client_with_auth():
    """Retourne (client, uid, email, jwt)."""
    client = sb()
    if not client:
        return None, None, None, None
    uid, email, jwt = _get_auth_from_session()
    return client, uid, email, jwt

def _normalize_ts(ts: str) -> str:
    t = (ts or "").strip().replace(",", "T").replace("%", "")
    return t if t.endswith("Z") else (t + "Z" if t else t)

def insert_hand_minimal(played_at_iso: str, display_name: str, payload_hand: dict | None):
    client = sb()
    if not client:
        return

    s = st.session_state
    hu_uid = s.get("hu_uid")
    hu_seq = int(s.get("hu_hand_seq") or 0)
    hand_uid = s.get("current_hand_uid")

    if not hu_uid or hu_seq <= 0:
        return

    played_at_iso = _normalize_ts(played_at_iso)

    row = {
        "hu_uid": hu_uid,
        "hu_hand_seq": hu_seq,
        "display_name": (display_name or "Anonymous").strip() or "Anonymous",
        "played_at": played_at_iso,
        "hand": payload_hand or {},
    }
    if hand_uid:
        row["hand_uid"] = hand_uid

    uid = getattr(s.get("sb_user"), "id", None)
    if uid:
        row["user_id"] = uid

    client.table("hands").upsert(row, on_conflict="hu_uid,hu_hand_seq").execute()




def count_hands_for_current_user() -> int:
    """
    COUNT des mains:
      1) par user_id si uid dispo
      2) sinon par display_name (session_state.display_name)
    """
    client, uid, email, jwt = get_client_with_auth()
    if not client:
        return 0
    try:
        if uid:
            res = client.table("hands").select("id", count="exact").eq("user_id", uid).execute()
            return int(getattr(res, "count", 0) or 0)
        disp = (st.session_state.get("display_name") or "").strip()
        if disp:
            res = client.table("hands").select("id", count="exact").eq("display_name", disp).execute()
            return int(getattr(res, "count", 0) or 0)
    except Exception:
        return 0
    return 0

__all__ = [
    "sb",
    "get_client_with_auth",
    "insert_hand_minimal",
    "count_hands_for_current_user",
]

def _user_key(uid: str | None, display_name: str | None) -> str:
    disp = (display_name or "").strip()
    if uid:
        return f"uid:{uid}"
    if disp:
        return f"name:{disp}"
    return "anon:global"

def get_user_hand_count() -> int:
    client = sb()
    if not client:
        return 0
    uid = getattr(st.session_state.get("sb_user"), "id", None)
    if not uid:
        return 0
    res = client.table("profiles").select("hands_played").eq("user_id", uid).maybe_single().execute()
    data = getattr(res, "data", None) or {}
    return int(data.get("hands_played") or 0)

def get_anon_hand_count() -> int:
    client = sb()
    if not client:
        return 0
    res = client.table("site_stats").select("val").eq("key","anon_hands_total").maybe_single().execute()
    data = getattr(res, "data", None) or {}
    return int(data.get("val") or 0)

