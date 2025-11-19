import re
import streamlit as st
from config import *
from app_state import process_action, start_new_hand, initialize_game
import time

# Import conditionnel de get_ai_action (défini dans app.py en mode UI-only)
try:
    from ia_bridge import get_ai_action
except ImportError:
    # Si ia_bridge n'est pas disponible, get_ai_action sera défini dans app.py
    def get_ai_action(model):
        from app_state import process_action
        process_action("ai", "call", 0)

# =============================================================
# GLOBAL CSS & INJECTION UTIL
# -------------------------------------------------------------
# Import du système de design SpinGPT
try:
    from spingpt_brand_css import inject_spingpt_brand_css
except ImportError:
    # Fallback si le fichier n'existe pas
    def inject_spingpt_brand_css(logo_path=None):
        pass

def inject_global_css(nav_html: str = ""):
    """Injecte le CSS de la marque SpinGPT"""
    # Cherche le logo dans assets/LogoSpinGPT.png ou autres variantes
    import os
    logo_path = None
    possible_logo_paths = [
        "assets/LogoSpinGPT.png",
        "assets/logo.png",
        "assets/logo.svg",
        "assets/logo.jpg",
        "LogoSpinGPT.png",
        "logo.png",
        "logo.svg"
    ]
    
    for path in possible_logo_paths:
        if os.path.exists(path):
            logo_path = path
            break
    
    # Injecte le CSS SpinGPT avec le logo et la navigation si trouvé
    inject_spingpt_brand_css(logo_path=logo_path, nav_html=nav_html)
    
    # Styles supplémentaires spécifiques au poker si nécessaire
    st.markdown("""
    <style>
    /* Styles poker spécifiques supplémentaires */
    .metric-center{ 
        display:flex; 
        flex-direction:column; 
        align-items:center; 
        justify-content:center; 
    }
    
    /* Message notifications */
    [data-testid="stNotificationContent"] {
        color: var(--text-body) !important;
    }
    
    div.stAlert svg { 
        display: none !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
ACTIONS_CSS = """
<style>
/* Actions avec couleurs SpinGPT */
.action-player{
    color: #0A2A43 !important;  /* Bleu profond SpinGPT */
    font-weight: 600;
}
.action-ai {
    color: #C13A3A !important;  /* Rouge poker SpinGPT */
    font-weight: 600;
}
.action-pot {
    color: #E54848 !important;  /* Rouge clair - accent électronique */
    font-weight: 600;
}
.timeline-item {
    margin-bottom: 4px;
}

/* Styles pour Pot / Tapis avec couleurs SpinGPT */
.metric-label {
    font-weight: 700;
    color: #0A2A43 !important;  /* Bleu profond */
}
.metric-value {
    font-weight: 700;
    color: #0A2A43 !important;  /* Bleu profond */
}
</style>
"""

STREET_ICON = {"preflop":"🂡","flop":"🂡","turn":"🂡","river":"🂡","showdown":"🏆"}

# =============================================================
# UTILITIES
# =============================================================

def card_to_html(card):
    s = str(card)
    rank, suit = s[:-1], s[-1]
    suit_code = {'♠':'s','♣':'c','♦':'d','♥':'h','s':'s','c':'c','d':'d','h':'h'}.get(suit.lower(), '?')
    glyph, color = SUIT_DISPLAY.get(suit_code, ('?', '#000'))
    return f"<span class='playing-card' style='color:{color};'>{rank}{glyph}</span>"


def _contribution(side: str) -> int:
    """Amount committed this street by side."""
    return st.session_state.get(f"{side}_bet", 0)


def _last_action_current_street(side: str) -> tuple[str, int]:
    """Dernière action du side pour la street courante."""
    import re
    s = st.session_state
    street_names = ['preflop', 'flop', 'turn', 'river', 'showdown']
    current_street = street_names[s.street_num]

    player_name = s.get("display_name") or s.get("pseudo")
    player_prefixes = tuple(p for p in [
        player_name, L("Player","Le Joueur"), "Le Joueur", "Joueur", "Player"
    ] if p)
    ai_prefixes = ("L'IA", "AI", "SpinGPT")

    for line in reversed(s.action_log[current_street]):
        if side == 'player':
            matched = next((p for p in player_prefixes if line.startswith(p)), None)
        else:
            matched = next((p for p in ai_prefixes if line.startswith(p)), None)
        if not matched:
            continue
        body = line[len(matched):].strip()

        if ('se couche' in body) or ('fold' in body):
            return ('fold', 0)
        if ('check' in body) or ('checks' in body):
            return ('check', 0)

        m = re.search(r'\bpaie\s+(\d+)', body) or re.search(r'\bcalls?\s+(\d+)', body)
        if m: return ('call', int(m.group(1)))

        m = re.search(r'\bmise\s+(\d+)', body) or re.search(r'\bbets?\s+(\d+)', body)
        if m: return ('bet', int(m.group(1)))

        m = re.search(r'\brelance\s+à\s+(\d+)', body) or re.search(r'\braises?\s+to\s+(\d+)', body)
        if m: return ('raise', int(m.group(1)))

    return ('', 0)



# =============================================================
# GAME‑STATE VISUALS
# =============================================================

def display_game_over():
    winner = (st.session_state.get("display_name") or "Player") if st.session_state.winner == 'player' else "SpinGPT"
    st.balloons()
    st.success(L(f"Game over! {winner} wins!", f"Partie terminée ! {winner} a gagné !"))
    if st.button(L('Play again', 'Recommencer une partie')):
        initialize_game(); st.rerun()


def _player_block(side: str, label: str, stack: int, cards_html: str):
    turn_cls = 'active-turn' if st.session_state.turn == side else ''
    st.markdown(f"<h3 style='margin:0;'>{label}</h3>", unsafe_allow_html=True)

    # Stack / Tapis
    st.markdown(
        f"""<span style="font-weight:700;">{L("Stack", "Tapis")}&nbsp;:</span>
            <span class="player-stack" style="font-size:48px;">{stack}</span>""",
        unsafe_allow_html=True
    )

    # Cartes
    st.markdown(cards_html, unsafe_allow_html=True)

    act, contrib = _last_action_current_street(side)

    if act == 'check':
        display = L('checks', 'check')
    elif act == 'fold':
        display = L('folds', 'se couche')
    elif act == 'call':
        display = L(f'calls {int(contrib)}', f'paie {int(contrib)}')
    elif act == 'bet':
        from config import SB, BB
        if st.session_state.get('street_num', 0) == 0:
            is_sb = ((side == 'player' and st.session_state.player_pos == 'SB') or
                     (side == 'ai'     and st.session_state.ai_pos     == 'SB'))
            is_bb = ((side == 'player' and st.session_state.player_pos == 'BB') or
                     (side == 'ai'     and st.session_state.ai_pos     == 'BB'))
            if is_sb and contrib == SB:
                display = L(f"posts small blind ({SB})", f"poste la petite blinde ({SB})")
            elif is_bb and contrib == BB:
                display = L(f"posts big blind ({BB})", f"poste la grosse blinde ({BB})")
            else:
                display = L(f"bets {int(contrib)}", f"mise {int(contrib)}")
        else:
            display = L(f"bets {int(contrib)}", f"mise {int(contrib)}")
    elif act == 'raise':
        display = L(f'raises to {int(contrib)}', f'relance à {int(contrib)}')
    else:
        display = ''

    st.markdown(
        f"<span class='contrib {turn_cls}'>{display}</span>",
        unsafe_allow_html=True
    )


def render_card(unicode_card: str) -> str:
    """Renvoie la balise HTML d’une carte avec un style fixe."""
    return f'<span style="font-size:60px; line-height:80px; margin:0 4px;">{unicode_card}</span>'

def display_player_info():
    s = st.session_state
    hero_stack = s.player_stack
    ai_stack   = s.ai_stack
    s.setdefault('show_ai_hand', False)

    st.markdown("""
    <style>
    .dealer-badge{
      display:inline-block; padding:4px 7px; margin-left:6px;
      border-radius:999px; background:#FFD54F; color:#000; font-weight:700;
      font-size:12px; line-height:1; border:1px solid rgba(0,0,0,.2);
    }
    </style>
    """, unsafe_allow_html=True)

    hero_name = s.get("display_name") or s.get("pseudo") or L("Player", "Joueur")

    dealer = '<span class="dealer-badge">D</span>'
    hero_label = f"👨‍💻 {hero_name} ({s.player_pos})"
    if s.player_pos == "SB":
        hero_label += f" {dealer}"

    ai_label = f"🤖 spinGPT ({s.ai_pos})"
    if s.ai_pos == "SB":
        ai_label += f" {dealer}"

    col1, col2 = st.columns(2)

    # ---- Hero ------------------------------------------------
    with col1:
        hero_cards = ' '.join(card_to_html(c) for c in s.player_hand)
        _player_block('player', hero_label, hero_stack,
                      f"<span style='font-size:32px;'>{hero_cards}</span>")

    # ---- IA --------------------------------------------------
    with col2:
        if s.show_ai_hand:
            cards_html = ' '.join(card_to_html(c) for c in s.ai_hand)
        else:
            cards_html = ''.join(render_card('🎴') for _ in range(2))

        _player_block('ai', ai_label, ai_stack,
                      f"<span style='font-size:32px;'>{cards_html}</span>")


def display_board_and_pot():
    s = st.session_state
    st.markdown(
        f"<div class='metric-label' style='text-align:center;'>{L('Pot', 'Pot')}&nbsp;:&nbsp;"
        f"<span class='pot-center'>{s.pot}</span></div>",
        unsafe_allow_html=True
    )
    board_html = ' '.join(card_to_html(c) for c in s.board) if s.board else ''
    st.markdown(
        f"<div class='board-cards' style='text-align:center;'>{board_html}</div>",
        unsafe_allow_html=True
    )



def display_action_buttons():
    s = st.session_state
    if s.game_over:
        return

    # ---- State
    call_amt  = s.bet_to_match - s.player_bet
    can_check = call_amt <= 0
    is_preflop = (s.street_num == 0)
    hero      = s.player_stack
    opp_has   = s.ai_stack > 0

    # ---- Bounds
    min_raise = (s.bet_to_match + s.last_raise) if s.bet_to_match else BB
    if is_preflop and can_check:
        min_bet = min_raise
    else:
        min_bet = BB if can_check else min_raise

    eff = min(hero + s.player_bet, s.ai_stack + s.ai_bet)
    can_raise = opp_has and eff >= int(min_bet)

    # AI turn
    if s.turn != 'player':
        st.info(L("AI is thinking...", "L'IA réfléchit..."))
        time.sleep(0.02)
        get_ai_action(s.poker_model)
        st.rerun()
        return

    # Player turn
    st.info(L("It's your turn.", "À vous de jouer."))

    # ---- CSS (fixed action bar)
    st.markdown("""
    <style>
      section.main > div.block-container { padding-bottom: 170px !important; }
      form[aria-label="action_bar"]{
        position: fixed !important;
        left: 0; right: 0; bottom: 16px;
        z-index: 1000;
        margin: 0 auto !important;
        max-width: 1100px;
        background: rgba(0,0,0,.12);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 12px;
        padding: 12px;
      }
    </style>
    """, unsafe_allow_html=True)

    # ---- Action row
    with st.form("action_bar", clear_on_submit=True):
        cF, cC, cAmt, cRaise, cAI = st.columns([1, 1, 2.6, 1.2, 1.2])

        # Fold
        b_fold = cF.form_submit_button("Fold", use_container_width=True)

        # Call / Check
        if can_check:
            call_label = L("Check","Check")  # on garde "Check" en FR
        else:
            call_label = L(
                f"Call all-in ({int(call_amt)})" if call_amt >= hero else f"Call {int(call_amt)}",
                f"All-in ({int(call_amt)})" if call_amt >= hero else f"Payer {int(call_amt)}"
            )

        b_call = cC.form_submit_button(call_label, use_container_width=True)

        STEP = 50
        if can_raise:
            bet_amt = cAmt.number_input(
                "Amount",
                min_value=int(min_bet),
                max_value=int(eff),
                value=int(min_bet),
                step=int(STEP),
                format="%d",
                label_visibility="collapsed",
            )
            raise_label = "Raise" if (is_preflop or not can_check) else "Raise"
            if not is_preflop and can_check:
                raise_label = "Bet"
            b_raise = cRaise.form_submit_button(raise_label, use_container_width=True)
        else:
            cAmt.write("")
            raise_label = "Raise" if (is_preflop or not can_check) else "Bet"
            b_raise = cRaise.form_submit_button(raise_label, disabled=True, use_container_width=True)

        # All-in
        b_allin = cAI.form_submit_button("All-in", use_container_width=True)

        # ---- Dispatch
        if b_fold:
            process_action("player", "fold"); st.rerun()

        if b_call:
            process_action("player", "check" if can_check else "call"); st.rerun()

        if b_raise:
            action_type = "raise" if (is_preflop or not can_check) else "bet"
            process_action("player", action_type, int(bet_amt)); st.rerun()

        if b_allin:
            if can_check:
                if is_preflop:
                    process_action("player", "raise", hero + s.player_bet)
                else:
                    process_action("player", "bet", hero + s.player_bet)
            else:
                if hero <= call_amt:
                    process_action("player", "call")
                else:
                    process_action("player", "raise", hero + s.player_bet)
            st.rerun()



# -------------------------------------------------------------
# SIDEBAR & TIMELINE
# -------------------------------------------------------------
ACTIONS_CSS_INLINE = ACTIONS_CSS

def _format_action(raw: str):
    if raw.startswith("IA-CORRECTION"):
        return ""
    s = st.session_state
    lang_fr = (s.get("lang", "en") == "fr")

    # Winner (EN/FR)
    if raw.startswith(("Winner:", "Gagnant:")):
        who = raw.split(":", 1)[1].strip(". ").strip()
        body_out = L(f"Winner: {who}.", f"Gagnant : {who}.")
        return f'<div class="timeline-item">{body_out}</div>'

    # Split pot (EN/FR)
    if raw.startswith(("Result: split pot", "Résultat : partage du pot")):
        body_out = L("Result: split pot.", "Résultat : partage du pot.")
        return f'<div class="timeline-item">{body_out}</div>'

    # Result (EN/FR)
    if raw.startswith(("Result:", "Résultat : ")):
        if raw.startswith("Résultat : "):
            body_fr = raw.replace("Résultat : ", "").strip()
            try:
                name, rest = body_fr.split(" gagne ", 1)
                amt = rest.strip(". ")
            except Exception:
                return f'<div class="timeline-item">{raw}</div>'
            body_out = L(f"Result: {name} wins {amt}.", f"Résultat : {name} gagne {amt}.")
        else:
            body_out = raw.strip()
        body_out = re.sub(r'(\d+)', r'<span class="action-pot">\1</span>', body_out)
        return f'<div class="timeline-item">{body_out}</div>'

    player_name = (s.get("display_name") or s.get("pseudo"))
    player_fallback = L("Player","Le Joueur")

    if any(raw.startswith(p) for p in filter(None, [player_fallback, "Le Joueur", "Joueur", "Player", player_name])):
        shown_name = player_name or player_fallback
        pref = f'<span class="action-player">👤 {shown_name}</span>'
    
        for p in (player_fallback, "Le Joueur", "Joueur", "Player", player_name):
            if p and raw.startswith(p):
                body = raw.replace(p, '', 1)
                break
        actor_is_player = True
    elif any(raw.startswith(p) for p in ("L'IA", "AI", "spinGPT")):
        pref = '<span class="action-ai">🤖 spinGPT</span>'
        for p in ("L'IA", "AI", "spinGPT"):
            if raw.startswith(p):
                body = raw.replace(p, '', 1)
                break
        actor_is_player = False
    else:
        return f'<div class="timeline-item">{raw}</div>'


    m = re.search(r"\bmise\s+(\d+)\.", body)
    if m:
        amt = int(m.group(1))
        is_sb = (s.player_pos == "SB") if actor_is_player else (s.ai_pos == "SB")
        is_bb = (s.player_pos == "BB") if actor_is_player else (s.ai_pos == "BB")
        street = s.get("_rendering_street", None)               
        if street == 'preflop':   
            if is_sb and amt == SB:
                body_out = L(f" posts small blind ({SB}).", f" poste la petite blinde ({SB}).")
            elif is_bb and amt == BB:
                body_out = L(f" posts big blind ({BB}).", f" poste la grosse blinde ({BB}).")
        else:
            body_out = None
        if body_out is not None:
            body_out = re.sub(r'(\d+)', r'<span class="action-pot">\1</span>', body_out)
            return f'<div class="timeline-item">{pref}{body_out}</div>'

    if lang_fr:
        body_fr = body
        body_fr = body_fr.replace(" folds.", " se couche.")
        body_fr = body_fr.replace(" checks.", " check.")
        body_fr = re.sub(r"\bcalls?\s+(\d+)\.",   r" paie \1.",      body_fr)
        body_fr = re.sub(r"\bbets?\s+(\d+)\.",    r" mise \1.",      body_fr)
        body_fr = re.sub(r"\braises?\s+to\s+(\d+)\.", r" relance à \1.", body_fr)
        body_out = body_fr
    else:
        body_en = body
        body_en = body_en.replace(" se couche.", " folds.")
        body_en = body_en.replace(" check.", " checks.")
        body_en = re.sub(r"\bpaie\s+(\d+)\.",      r" calls \1.",      body_en)
        body_en = re.sub(r"\bmise\s+(\d+)\.",      r" bets \1.",       body_en)
        body_en = re.sub(r"\brelance à\s+(\d+)\.", r" raises to \1.",  body_en)
        body_out = body_en

    body_out = re.sub(r'(\d+)', r'<span class="action-pot">\1</span>', body_out)
    return f'<div class="timeline-item">{pref}{body_out}</div>'



def display_sidebar_log():
    """Historique complet dans la barre latérale."""
    st.sidebar.markdown(ACTIONS_CSS_INLINE, unsafe_allow_html=True)
    st.sidebar.subheader(L("📜 Hand history", "📜 Historique de la main"))

    street_label = {
        "preflop": L("Preflop", "Préflop"),
        "flop":    L("Flop", "Flop"),
        "turn":    L("Turn", "Turn"),
        "river":   L("River", "River"),
        "showdown":L("Showdown", "Showdown"),
    }
    for street, acts in st.session_state.action_log.items():
        if not acts:
            continue
        ico = STREET_ICON.get(street, '➜')
        with st.sidebar.expander(f"{ico} {street_label.get(street, street)}", expanded=True):
            st.session_state._rendering_street = street
            for a in acts:
                st.markdown(_format_action(a), unsafe_allow_html=True)



def display_action_timeline(n_last: int = 4):
    """Affiche les *n_last* dernières actions au centre."""
    # Finalement enlevé de la version finale
    flat = [a for acts in st.session_state.action_log.values() for a in acts]
    if not flat:
        return
    st.markdown(ACTIONS_CSS_INLINE, unsafe_allow_html=True)
    st.subheader(L('Last actions', 'Dernières actions'))
    for act in flat[-n_last:]:
        st.markdown(_format_action(act), unsafe_allow_html=True)


def display_end_of_hand():
    s = st.session_state
    if s.winner == 'tie':
        st.info(L("Hand is over. Split pot.", "La main est terminée. Égalité (pot partagé)."))
    elif s.winner == 'player':
        profit = s.player_stack - s.hand_start_player_stack
        winner_name = s.get("display_name", L("the player", "Le joueur"))
        st.success(L(f"Hand is over. Winner: {winner_name} (+{profit})",
                     f"La main est terminée. Gagnant : {winner_name} (+{profit})"))
    else:
        profit = s.ai_stack - s.hand_start_ai_stack
        st.success(L(f"Hand is over. Winner: spinGPT (+{profit})",
                     f"La main est terminée. Gagnant : spinGPT (+{profit})"))
    if st.button(L('Next hand', 'Prochaine main')):
        s.show_ai_hand = False
        start_new_hand()
        st.rerun()


def L(en: str, fr: str) -> str:
    import streamlit as st
    return fr if st.session_state.get("lang", "en") == "fr" else en
