# app.py
# ─────────────────────────────────────────────────────────────────────────────

import os, re, time, importlib, concurrent.futures, json
import streamlit as st

# ---------- Page ----------
st.set_page_config(
    page_title="SpinGPT - Quand les grands modèles jouent leurs cartes", 
    page_icon="assets/LogoSpinGPT.png", 
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar ouverte par défaut
)

# ---------- Language (EN/FR) ----------
lang_from_url = st.query_params.get("lang")
if lang_from_url:
    # Si un paramètre ?lang= est présent, il a la priorité
    st.session_state["lang"] = "fr" if str(lang_from_url).lower().startswith("fr") else "en"
elif "lang" not in st.session_state:
    # Valeur par défaut
    st.session_state["lang"] = "en"

# ---------- Page from URL query param (navigation simple) ----------
# On utilise ?p=home|auth|profile|board|newgame pour piloter la page courante.
page_from_url = st.query_params.get("p")
if page_from_url:
    # Nettoyer le query param pour ne pas le retraiter à chaque rerun
    qp = st.query_params
    if "p" in qp:
        del qp["p"]

    # Mapper la valeur vers la bonne page interne
    if page_from_url == "newgame":
        # Démarrer une nouvelle partie
        st.session_state["anonymous"] = (st.session_state.get("sb_user") is None)
        st.session_state["page"] = "loading"
    else:
        st.session_state["page"] = page_from_url

def L(en: str, fr: str) -> str:
    return fr if st.session_state.get("lang", "en") == "fr" else en

# Langue et utilisateur
# Note: Le toggle langue peut être ajouté dans le header si nécessaire
_user = st.session_state.get("sb_user")

# ---------- Imports projet ----------
from config import *

# Import conditionnel selon le mode (AVANT ui_components pour que get_ai_action soit disponible)
if UI_ONLY_MODE:
    # Mode UI-only : mock du modèle IA
    class MockPokerModel:
        def get_action(self, prompt: str) -> str:
            return "c"  # call par défaut
        def get_action_with_dists(self, prompt: str):
            return "c", [{"action": "c", "p": 1.0}], []
    
    def load_poker_model(token):
        return MockPokerModel()
    
    def get_ai_action(model):
        # Action simple en mode UI-only
        from app_state import process_action
        process_action("ai", "call", 0)
    
    st.session_state.poker_model = MockPokerModel()
else:
    from ia_model import load_poker_model
    from ia_bridge import get_ai_action

# Maintenant on peut importer ui_components qui utilise get_ai_action
from app_state import initialize_game
from supabase_utils import count_hands_for_current_user, get_client_with_auth
import ui_components as ui
importlib.reload(ui)

# ---------- Supabase (auth + profils) ----------
from supabase import create_client, Client

def sb() -> Client:
    if UI_ONLY_MODE:
        # En mode UI-only, retourner None au lieu de bloquer
        return None
    if not SUPABASE_URL or not SUPABASE_ANON_KEY or SUPABASE_URL.startswith("mock://"):
        if not UI_ONLY_MODE:
            st.warning(L("SUPABASE_URL / SUPABASE_ANON_KEY missing. Database features disabled.",
                        "SUPABASE_URL / SUPABASE_ANON_KEY manquants. Fonctionnalités base de données désactivées."))
        return None
    if "sb_client" not in st.session_state:
        try:
            st.session_state.sb_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        except Exception:
            return None
    return st.session_state.sb_client

def set_user(res):
    """Met en session l'utilisateur + récupère le pseudo (profiles)."""
    if UI_ONLY_MODE:
        return  # En mode UI-only, ignorer l'authentification
    st.session_state.sb_user = res.user
    st.session_state.sb_session = res.session
    try:
        client = sb()
        if client:
            prof = client.table("profiles").select("display_name").eq("user_id", res.user.id).single().execute()
            st.session_state.display_name = (prof.data or {}).get("display_name")
    except Exception:
        st.session_state.display_name = None

def sign_out():
    if not UI_ONLY_MODE:
        try:
            client = sb()
            if client:
                client.auth.sign_out()
        except Exception:
            pass
    for k in ("sb_user", "sb_session", "display_name"):
        st.session_state.pop(k, None)
    st.rerun()

def _norm_name(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip()

def is_pseudo_available(display_name: str) -> bool:
    """Interroge l'RPC côté DB pour savoir si le pseudo est libre (bypass RLS)."""
    if UI_ONLY_MODE:
        return True  # En mode UI-only, tous les pseudos sont disponibles
    try:
        client = sb()
        if not client:
            return True
        name = _norm_name(display_name)
        res = client.rpc("is_display_name_free", {"name": name}).execute()
        return bool(res.data)
    except Exception:
        return False

def signup_with_profile(email, password, display_name):
    """Inscription robuste : on vérifie le pseudo via RPC (bypass RLS).
       Si indisponible -> on n'appelle PAS sign_up(). Sinon sign_up + insert profil.
       Si confirmation email OFF et session reçue -> auto-login et route vers 'loading'."""
    if UI_ONLY_MODE:
        st.info(L("UI-Only Mode: Authentication is disabled. You can use any display name.",
                  "Mode UI-Only : L'authentification est désactivée. Vous pouvez utiliser n'importe quel pseudo."))
        st.session_state.display_name = display_name
        st.session_state.page = "loading" if not UI_ONLY_MODE else "play"
        st.rerun()
        return
    name = _norm_name(display_name)

    # 0) Vérif pseudo AVANT toute création de compte
    ok = is_pseudo_available(name)
    if not ok:
        st.error(L("This display name is already taken. Please choose another one.",
               "Ce pseudo est déjà utilisé. Choisis-en un autre."))
        return

    # 1) Créer le compte
    try:
        client = sb()
        if not client:
            st.error(L("Database connection unavailable.", "Connexion à la base de données indisponible."))
            return
        res = client.auth.sign_up({"email": email, "password": password})
    except Exception as e:
        msg = str(e)
        if "User already registered" in msg or "already registered" in msg:
            st.error(L("This email is already registered.", "Cette adresse email est déjà utilisée."))
        else:
            st.error(L(f"Signup error: {msg}", f"Erreur d’inscription : {msg}"))
        return

    if not res.user:
        st.error(L("Account creation failed.", "Création de compte impossible."))
        return

        # 2) Créer le profil
    try:
        client = sb()
        if client:
            client.table("profiles").insert({
                "user_id": res.user.id,
                "display_name": name,
                "email": email,
            }).execute()
    except Exception:
        st.error(L("This display name has just been taken. Please choose another one.",
               "Ce pseudo vient d'être pris à l'instant. Choisis-en un autre."))
        return

    # 3) Auto-login si possible (email confirmation OFF)
    if res.session:
        set_user(res)
        st.session_state.page = "loading"
        st.success(L("Account created and signed in.", "Compte créé et connecté."))
        st.rerun()
    else:
        st.success(L("Account created.", "Compte créé."))


def login_email(email, password):
    if UI_ONLY_MODE:
        st.info(L("UI-Only Mode: Authentication is disabled. Click 'New game' to start.",
                  "Mode UI-Only : L'authentification est désactivée. Cliquez sur 'Nouvelle partie' pour commencer."))
        st.session_state.anonymous = True
        st.session_state.page = "play"
        st.rerun()
        return
    try:
        client = sb()
        if not client:
            st.error(L("Database connection unavailable.", "Connexion à la base de données indisponible."))
            return
        res = client.auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
        st.error(L("Invalid email or password.", "Email ou mot de passe invalide.")); return
    if not res.user:
        st.error(L("Invalid email or password.", "Email ou mot de passe invalide.")); return
    set_user(res)

    try:
        client = sb()
        if client:
            client.table("profiles").update({"email": getattr(res.user, "email", None)})\
                .eq("user_id", res.user.id).execute()
    except Exception:
        pass

    st.session_state.anonymous = False
    st.session_state.page = "loading"
    st.rerun()


# ---------- Navigation header ----------
def render_header_navigation():
    """Crée la navigation dans le header"""
    user = st.session_state.get("sb_user")
    page = st.session_state.get("page", "home")
    lang = st.session_state.get("lang", "en")
    current_lang = "fr" if lang == "fr" else "en"
    
    nav_items = []
    
    # Home
    nav_items.append({
        "id": "home",
        "label": "🏠 " + ("Home" if lang == "en" else "Accueil"),
        "active": page == "home"
    })

    # Team (juste à droite de Home)
    nav_items.append({
        "id": "team",
        "label": "👥 " + ("Team" if lang == "en" else "Équipe"),
        "active": page == "team"
    })

    # New Game (toujours visible dans le header)
    nav_items.append({
        "id": "newgame",
        "label": "▶️ " + ("New game" if lang == "en" else "Nouvelle partie"),
        "active": False
    })

    # Profile (si connecté)
    if user:
        nav_items.append({
            "id": "profile",
            "label": "Profile" if lang == "en" else "Mon profil",
            "active": page == "profile"
        })
    
    # Leaderboard
    nav_items.append({
        "id": "board",
        "label": "🏆 " + ("Leaderboard" if lang == "en" else "Classement"),
        "active": page == "board"
    })
    
    # Auth (si pas connecté)
    if not user:
        nav_items.append({
            "id": "auth",
            "label": "Sign in / Sign up" if lang == "en" else "Se connecter / S'inscrire",
            "active": page == "auth"
        })
    
    # Construire le HTML avec des liens simples (href avec query param, même onglet),
    # en conservant toujours la langue courante dans l'URL (?p=...&lang=fr|en).
    nav_html = ''
    for item in nav_items:
        active_class = 'nav-btn-active' if item["active"] else ''
        page_id = item["id"]
        label = item["label"]
        button_html = (
            "<a class=\"spingpt-nav-btn {active_class}\" "
            "href=\"?p={page_id}&lang={lang}\" data-page=\"{page_id}\" role=\"button\" target=\"_self\">"
            "{label}</a>"
        ).format(
            active_class=active_class,
            page_id=page_id,
            lang=current_lang,
            label=label,
        )
        nav_html += button_html
    
    # Retourner le HTML pour qu'il soit injecté dans le header
    return nav_html

# ---------- Navigation Header (doit être appelé AVANT le CSS pour injecter dans le header) ----------
nav_html = render_header_navigation()

# ---------- 0. CSS ----------
ui.inject_global_css(nav_html=nav_html)

# ---------- 1. État initial ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "anonymous" not in st.session_state:
    st.session_state.anonymous = True  # par défaut : anonyme tant qu'on n'est pas loggé

# ---------- 2. Lancer le chargement du modèle (une seule fois) ----------
if UI_ONLY_MODE:
    # En mode UI-only, le modèle mock est déjà créé dans les imports
    pass
elif "model_future" not in st.session_state:
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    st.session_state.model_future = executor.submit(load_poker_model, HF_TOKEN)
    st.session_state.executor = executor

def model_ready():
    """True si le modèle est chargé et placé dans session_state.poker_model"""
    if UI_ONLY_MODE:
        return True  # Le modèle mock est toujours prêt
    if "poker_model" in st.session_state:
        return True
    future = st.session_state.model_future
    if future.done():
        st.session_state.poker_model = future.result()
        st.rerun()
    return False

def show_loading_page():
    """Overlay plein écran : titre + roue CSS centrée, masque le reste."""
    if UI_ONLY_MODE:
        # En mode UI-only, passer directement à la page de jeu
        st.session_state.page = "play"
        st.rerun()
        return
    
    st.markdown(f"""
    <style>
      #loading-overlay {{ position: fixed; inset: 0; z-index: 9999;
        background: rgba(0,0,0,0.12);
        display: flex; align-items: center; justify-content: center; }}
      #loading-overlay .inner {{ display: flex; flex-direction: column; align-items: center; gap: 12px; }}
      #loading-title {{ position: fixed; top: 10px; left: 24px;
        margin: 0; font-size: 2.2rem; font-weight: 800; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,.4); z-index: 10000; }}
      .loader {{ width: 56px; height: 56px; border: 6px solid rgba(255,255,255,0.25);
        border-top-color: rgba(255,255,255,0.95); border-radius: 50%; animation: spin 0.9s linear infinite; }}
      @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
      .load-label {{ font-weight: 600; color: #fff; text-shadow: 0 1px 2px rgba(0,0,0,.4); }}
    </style>
    <h1 id="loading-title">{L("Model initialization…","Initialisation du modèle…")}</h1>
    <div id="loading-overlay"><div class="inner">
        <div class="loader"></div>
        <div class="load-label">{L("Loading model…","Chargement du modèle…")}</div>
    </div></div>
    """, unsafe_allow_html=True)

    while not model_ready():
        time.sleep(0.1)

    st.session_state.page = "play"
    st.rerun()


# ---------- 3. Router ----------
page = st.session_state.page

# ====================== PAGE HOME ======================
if page == "home":
    
    # Logo sur la homepage
    import os
    import base64
    logo_path = None
    possible_logo_paths = [
        "assets/LogoSpinGPT.png",
        "assets/logo.png",
        "assets/logo.svg",
        "LogoSpinGPT.png",
        "logo.png"
    ]
    
    for path in possible_logo_paths:
        if os.path.exists(path):
            logo_path = path
            break
    
    if logo_path:
        try:
            with open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read()).decode()
                ext = os.path.splitext(logo_path)[1][1:].lower()
                mime_types = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'svg': 'image/svg+xml',
                    'gif': 'image/gif'
                }
                mime_type = mime_types.get(ext, 'image/png')
                logo_base64 = f"data:{mime_type};base64,{logo_data}"
                tagline = L("When large models play their cards", "Quand les grands modèles jouent leurs cartes")

                st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 2rem 0; padding: 2rem 0;">
                    <img src="{logo_base64}" alt="SpinGPT Logo" style="max-height: 200px; width: auto; margin-bottom: 1.5rem; object-fit: contain;" />
                    <h1 style="text-align: center; margin: 0; color: var(--text-primary); font-size: 2.5rem; font-weight: 700;">SpinGPT</h1>
                    <p class="spingpt-tagline">{tagline}</p>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            # Si erreur de chargement du logo, afficher le titre normalement
            st.title(L("spinGPT - Quand les grands modèles jouent leurs cartes", "spinGPT - IA de poker"))
    else:
        st.title(L("spinGPT - Quand les grands modèles jouent leurs cartes", "spinGPT - IA de poker"))

    home_md_en = r"""
### Why SpinGPT?

SpinGPT is a poker AI developed at LAMSADE (Université Paris-Dauphine – PSL) by Narada Maugin and Professor Tristan Cazenave.  
The purpose of this site is to collect hands in order to analyze SpinGPT's performance and robustness in real-play conditions,  
and to assess the relevance and usefulness of a large language model in an imperfect-information game like poker.

**Game format:** Texas Hold'em No-Limit, heads-up, starting stack **2,500**, blinds **50/100**.

For the last decade, poker has been a genuine playground for AI: from early theoretical solvers to systems able to beat professional players.  
Poker is no longer “the last barrier” where humans always win, but a training ground for modern algorithms.

In parallel, a more secret ecosystem has grown around private solvers and cheating bots. Very few of these systems are described publicly.  
We mostly infer their existence from occasional scandals, account closures, or anonymous testimonies. The line between legitimate research,  
educational tools and tools for cheating is very thin. That is one of the reasons why we insist on transparency in SpinGPT.

SpinGPT started as a small, honest counterpoint to this trend. Instead of building a closed bot, we start from an open-weight language model  
(*Llama‑3.1‑8B*), teach it to “speak poker” in Spin & Go heads‑up situations (1 vs 1) using real tournament hands played by Narada,  
then align it with a GTO solver using offline reinforcement learning. Our goal is to keep what we do documented, reproducible and publishable.

We do not connect SpinGPT to real‑money poker sites, and we do not sell it.  
Our aim is simpler, and we hope more useful: to study how far a general‑purpose language model can go on a precise poker task,  
to measure its strengths and limitations honestly, and to share this journey with the research community and curious players.

---

#### Challenge (through December 1, 2025)
Play against SpinGPT for a chance to win:
- **€500** to the player with the highest win rate (BB/100) against our AI, with at least **2,000 hands** (after variance reduction with Aivat),
- **€250** to the runner-up by win rate (BB/100) against our AI, with at least **2,000 hands** (after variance reduction with Aivat),
- **5 x €50** randomly drawn among players who have played at least **1,000 hands** against SpinGPT.

#### Participation rules
- Be at least 18 years old and know the rules of No-Limit Texas Hold'em.
- Create an account and provide a valid e-mail address (so we can contact you if you win).
- Do not use decision-assistance software.
- Consent to your hands being recorded for academic research only.

#### How to play
- Anonymous: click “New game” in the header to start immediately.
- With an account: sign in (or create an account) to be eligible for prizes. Your profile shows how many hands you have played.
- You can leave at any time.

---

Questions: narada.maugin [at] gmail.com

*Thank you for participating!*

<div style="text-align:right; font-size:0.9rem; color:#f5f5f5;">
Built&nbsp;with&nbsp;Meta&nbsp;Llama&nbsp;3
</div>
"""

    home_md_fr = r"""
### Pourquoi SpinGPT ?


SpinGPT est une IA de poker développée au LAMSADE (Université Paris-Dauphine – PSL) par Narada Maugin et le professeur Tristan Cazenave.  
Le but de ce site est de recueillir des mains pour analyser la performance et la robustesse de SpinGPT en conditions réelles,  
et de mieux comprendre la pertinence d’un grand modèle de langage (LLM) dans un jeu à information incomplète comme le poker.

**Format de jeu :** Texas hold'em no-limit, heads-up, tapis **2 500**, blindes **50/100**.

Depuis une dizaine d’années, le poker est devenu un véritable terrain de jeu pour l’IA : des premiers solveurs théoriques jusqu’aux systèmes  
capables de battre des joueurs professionnels. Le poker n’est plus « la dernière barrière » où l’humain surpasse toujours la machine,  
mais un terrain d'entraînement pour l’intelligence artificielle.

En parallèle, un écosystème plus secret s’est développé autour de solveurs privés et de bots de triche. Très peu de ces systèmes sont décrits publiquement.  
On en devine l’existence à travers des scandales ponctuels, des fermetures de comptes ou des témoignages anonymes.  
La frontière entre recherche légitime, outil pédagogique et arme de triche est très fine.  
C’est une des raisons pour lesquelles nous insistons sur la transparence des travaux autour de SpinGPT.

SpinGPT est né comme un petit contrepoint honnête à cette tendance. Plutôt que de construire un bot fermé, nous partons d’un modèle de langage  
open-weight (*Llama‑3.1‑8B*), nous lui apprenons à « parler poker » sur des situations de Spin & Go heads-up (1 contre 1) en l’entraînant sur  
une base de données de vraies mains jouées en tournoi par Narada, puis nous l’alignons avec un solveur GTO via du reinforcement learning hors ligne.  
Tout ce que nous faisons est pensé pour être documenté, reproductible et publiable.

Nous ne connectons pas SpinGPT à des sites de jeu en argent réel et nous ne le vendons pas.  
Notre objectif est plus simple – et, nous l’espérons, plus utile : étudier jusqu’où peut aller un grand modèle de langage construit à l’origine  
pour des tâches beaucoup moins spécifiques, mesurer honnêtement ses forces et ses limites, et partager ce chemin avec la communauté scientifique  
et les joueurs curieux.

---

#### Challenge (jusqu’au 1er décembre 2025)
Jouez contre SpinGPT et tentez de gagner l'un des prix suivants :
- **500 €** pour la personne avec le meilleur profit (en BB/100) contre notre IA sur au moins **2 000 mains** (après réduction de la variance avec Aivat),  
- **250 €** pour la personne avec le deuxième meilleur profit (en BB/100) contre notre IA sur au moins **2 000 mains** (après réduction de la variance avec Aivat),  
- **5 x 50 €** tirés au hasard parmi les joueurs et joueuses ayant disputé au moins **1 000 mains** contre SpinGPT.

#### Conditions de participation
- Avoir plus de 18 ans et connaître les règles du Texas Hold'em no-limit.
- Créer un compte et renseigner une adresse e-mail valide (pour vous contacter en cas de gain).
- Ne pas utiliser de logiciel d'aide à la décision.
- Accepter que les mains soient enregistrées à des fins de recherche universitaire uniquement.

#### Comment jouer
- En mode anonyme : cliquez sur « Nouvelle partie » dans le header et commencez immédiatement.  
- Avec compte : connectez-vous (ou créez un compte) pour être éligible aux récompenses. Votre profil affiche votre nombre de mains jouées.  
- Vous pouvez quitter à tout moment.

---

Pour toute question : narada.maugin [at] gmail.com

*Merci de votre participation !*

<div style="text-align:right; font-size:0.9rem; color:#f5f5f5;">
Construit&nbsp;avec&nbsp;Meta&nbsp;Llama&nbsp;3
</div>
"""

    st.markdown(L(home_md_en, home_md_fr), unsafe_allow_html=True)
    st.stop()


# ====================== PAGE LOADING ======================
# ====================== PAGE LOADING ======================
if page == "loading":
    show_loading_page()
    st.stop()

# ====================== PAGE AUTH (login / signup) ======================

# ====================== PAGE AUTH ======================
if page == "auth":
    st.title(L("Player account", "Compte joueur"))

    tabs = st.tabs([L("Sign in", "Se connecter"), L("Create an account", "Créer un compte")])

    # --- SIGN IN ---
    with tabs[0]:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(L("Email", "Email"), key="login_email")
            pwd   = st.text_input(L("Password", "Mot de passe"), type="password", key="login_password")
            ok    = st.form_submit_button(L("Sign in", "Se connecter"))
        if ok:
            login_email(email.strip(), pwd)

    # --- SIGN UP ---
    with tabs[1]:
        with st.form("signup_form", clear_on_submit=False):
            pseudo = st.text_input(L("Display name", "Pseudo"), max_chars=24, key="signup_name")
            email2 = st.text_input(L("Email", "Email"), key="signup_email")
            pwd2   = st.text_input(L("Create password", "Mot de passe"), type="password", key="signup_password")
            ok2    = st.form_submit_button(L("Create my account", "Créer mon compte"))
        if ok2:
            if len(pseudo.strip()) < 2:
                st.error(L("Display name too short.", "Pseudo trop court."))
            else:
                try:
                    signup_with_profile(email2.strip(), pwd2, pseudo.strip())
                except Exception as e:
                    st.error(L(f"Signup error: {e}", f"Erreur d’inscription : {e}"))

    st.markdown("—")
    if st.button(L("⬅️ Back to home", "⬅️ Revenir à l’accueil")):
        st.session_state.page = "home"; st.rerun()
    st.stop()

# ====================== PAGE PROFIL ======================
# ====================== PAGE PROFILE ======================
if page == "profile":
    user = st.session_state.get("sb_user")
    if not user:
        st.info(L("Sign in to view your profile.", "Connecte-toi pour voir ton profil."))
        if st.button(L("Go to sign in", "Aller à la connexion")):
            st.session_state.page = "auth"; st.rerun()
        st.stop()

    st.title(L("My profile", "Mon profil"))
    st.markdown("""
    <style>
    .profile-info a {
        color: #fff !important;
        text-decoration: underline;
        background: rgba(0,0,0,0.25);
        padding: 2px 6px; border-radius: 6px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    email = getattr(user, "email", "—")
    display = st.session_state.get("display_name") or "—"
    st.markdown(
    f"""
    <div class="profile-info">
        <p><strong>{L('Email','Email')} :</strong> <a href="mailto:{email}">{email}</a></p>
        <p><strong>{L('Display name','Pseudo')} :</strong> {display}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    cnt = count_hands_for_current_user()
    st.metric(L("Hands recorded", "Mains enregistrées"), int(cnt))
    st.stop()

# ====================== PAGE LEADERBOARD ======================
# ====================== PAGE LEADERBOARD ======================
# ====================== PAGE BOARD ======================
if page == "board":
    st.title(L("Leaderboard", "Classement"))

    import os, json
    import pandas as pd
    from config import LOG_FILE
    client = sb()

    # Base RPC existant (peu importe son contenu exact, on va écraser hands_played et ajouter W–L)
    if UI_ONLY_MODE or not client:
        st.info(L("UI-Only Mode: Leaderboard is disabled. Database features are not available.",
                  "Mode UI-Only : Le classement est désactivé. Les fonctionnalités de base de données ne sont pas disponibles."))
        st.stop()
    try:
        res = client.rpc("get_leaderboard_with_wl", {"limit_n": 100}).execute()
        df = pd.DataFrame(res.data or [])
    except Exception as e:
        st.error(f"DB error: {e}")
        st.stop()

    if df.empty or "display_name" not in df.columns:
        st.info(L("No data yet.", "Aucune donnée pour le moment."))
        st.stop()

    # --- 1) Recalcule hands_played depuis la table hands (même logique que la page Profile) ---
    names = sorted(set(df["display_name"].dropna()))
    counts = {}
    for name in names:
        try:
            r = client.table("hands").select("id", count="exact").eq("display_name", name).limit(1).execute()
            counts[name] = int(getattr(r, "count", 0) or 0)
        except Exception:
            counts[name] = 0
    df["hands_played"] = df["display_name"].map(counts).fillna(0).astype(int)

    # --- 2) Calcule W–L directement depuis hands_log.jsonl (ignore "Anonyme/Anonymous") ---
    @st.cache_data(show_spinner=False)
    def compute_wl_from_log(log_path: str, mtime: float) -> dict[str, tuple[int, int]]:
        wl = {}
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue

                    name = (rec.get("pp") or "").strip()
                    if not name or name.lower().startswith(("anonyme", "anonymous")):
                        continue

                    w = rec.get("w"); ai = rec.get("ai")
                    if not isinstance(w, list) or len(w) < 2 or not isinstance(ai, list) or len(ai) < 2:
                        continue

                    winner, profit = w[0], int(w[1])
                    ai_start = int(ai[1])  # stack IA au début de la main

                    # variation IA sur la main
                    ai_profit = profit if winner == "ai" else -profit if winner == "player" else 0
                    ai_end = ai_start + ai_profit  # stack IA à la fin de la main

                    # Fin de HU: IA à 0 -> win humain ; IA à 5000 -> loss humain
                    if ai_end <= 0:
                        w0, l0 = wl.get(name, (0, 0))
                        wl[name] = (w0 + 1, l0)
                    elif ai_end >= 2500 * 2:  # 5000 jetons = 25BB
                        w0, l0 = wl.get(name, (0, 0))
                        wl[name] = (w0, l0 + 1)
        except FileNotFoundError:
            pass
        return wl

    mtime = os.path.getmtime(LOG_FILE) if os.path.exists(LOG_FILE) else 0.0
    wl_map = compute_wl_from_log(LOG_FILE, mtime)
    df["wins"] = df["display_name"].map(lambda n: wl_map.get(n, (0, 0))[0]).fillna(0).astype(int)
    df["losses"] = df["display_name"].map(lambda n: wl_map.get(n, (0, 0))[1]).fillna(0).astype(int)
    df["W–L"] = df["wins"].astype(str) + "–" + df["losses"].astype(str)

    # --- 3) Tri par mains et reconstruction du rang ---
    df = df.sort_values("hands_played", ascending=False, kind="mergesort").reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)

    # --- 4) Affichage ---
    cols = ["rank", "display_name", "hands_played", "W–L"]
    out = df[cols].copy()
    out.columns = [L("Rank", "Rang"), L("Player", "Joueur"), L("Hands", "Mains"), "W–L"]
    st.dataframe(out, use_container_width=True)
    st.stop()


# ====================== PAGE TEAM ======================
if page == "team":
    st.title(L("Team", "Équipe"))

    # Tristan
    st.image("assets/Tristan_Cazenave_ProfilePicture.jpg", width=160)
    st.header("Tristan Cazenave — " + L("Scientific Director", "Directeur scientifique"))
    st.markdown(
        L(
            """
Tristan Cazenave is a Professor of Artificial Intelligence at LAMSADE, Université Paris‑Dauphine – PSL and CNRS. 
He has been working on games for more than thirty years: from Go to real‑time strategy games, then poker, and even applications in biology.

In SpinGPT, he is our scientific compass. He makes sure that experiments are solid, that results are measured honestly, 
and that every number corresponds to a real research question:

> “Has the model actually learned something about the game,  
> or is it simply copying superficial patterns?”

His path, from self‑play in Go through modern Monte Carlo methods and reinforcement learning, gives the project depth and a strong technical foundation. 

""",
            """
Tristan Cazenave est Professeur d’Intelligence Artificielle au LAMSADE, Université Paris-Dauphine – PSL et CNRS. 
Il travaille depuis plus de trente ans sur les jeux : du Go aux jeux de stratégie en temps réel, puis le poker et même des applications en biologie.

Dans SpinGPT, il est notre boussole scientifique. Il s’assure que les expériences sont solides, que les résultats sont mesurés honnêtement 
et que chaque chiffre répond à une vraie question de recherche :

> « Le modèle a-t-il réellement appris quelque chose sur le jeu,  
> ou se contente-t-il de recopier des motifs superficiels ? »

Son parcours dans l’auto-jeu en Go en passant par les méthodes Monte Carlo modernes et l’apprentissage par renforcement donne au projet une profondeur  et une base technique forte. 

"""
        )
    )

    st.markdown("[LinkedIn](https://www.linkedin.com/in/tristan-cazenave-11474815/)")

    st.markdown("---")

    # Narada
    st.image("assets/Narada_Maugin_ProfilePicture.jpg", width=160)
    st.header("Narada Maugin — " + L("Lead Developer & Expert Player", "Développeur principal & joueur expert"))
    st.markdown(
        L(
            """
Narada is both an AI researcher (Master’s student at Université Paris Cité, specializing in LLMs, RL and Game AI) 
and a former professional poker player.

He provides SpinGPT’s dataset:

- about **8,800 Spin & Go hands** at **€50, €100 and €250** buy‑ins,  
- resulting in roughly **320,000 individual decisions** made by an experienced human player.

In the project, Narada has two main roles:

- **On the AI side**: designing the training pipeline, choosing models, running experiments against reference bots and defining statistical evaluation methods.  
- **On the poker side**: bringing field intuition — which spots are truly critical, which lines are standard or marginal, and where an AI that *looks strong* may actually be following a fragile strategy.

He also organizes and supervises SpinGPT vs. human matches in Spin & Go heads‑up (1 vs 1) configurations, and makes sure they stay consistent with what we model.

""",
            """
Narada est à la fois chercheur en IA (étudiant en master à l’Université Paris Cité, spécialisé en LLM, RL et Game AI) 
et ancien joueur professionnel de Poker.

Il fournit le dataset de SpinGPT :

- environ **8 800 mains de Spin & Go**,aux buy-ins **50 €, 100 € et 250 €**,  
- soit environ **320 000 décisions individuelles** prises par un joueur humain expérimenté.

Dans le projet, Narada assure deux rôles principaux :

- **Côté IA** : conception du pipeline d’entraînement, choix de modèles, expériences contre des bots de référence et méthodes d’évaluation statistique.  
- **Côté poker** : intuition de terrain — quels spots sont vraiment critiques, quelles lignes sont standard ou marginales, et où une IA qui *semble forte* peut en réalité suivre une stratégie fragile.

Il organise et supervise également les matchs SpinGPT vs. humains, sur des configurations de Spin & Go heads-up (1 vs 1) et s'assure de la cohérence avec ce que nous modélisons.
"""
        )
    )

    st.markdown("[LinkedIn](https://www.linkedin.com/in/narada-maugin/)")

    st.markdown("---")

    # William
    st.image("assets/William_Miserolle_ProfilePicture.jpg", width=160)
    st.header("William — " + L("Interface, Storytelling & Bridge to Students", "Interface, récit & lien avec les étudiants"))
    st.markdown(
        L(
            """
William is a student in Mathematics and Computer Science for Decision and Data at Université Paris-Dauphine – PSL, 
and is interested in AI, product and user experience.

In SpinGPT, his contribution focuses on:

- **Interface & UX**: making interactions with the web application easy for players, by designing screens that let them follow the experience easily.

- **Branding & pedagogy**: telling the story of the project, explaining what we do and what we don’t do 
  (for example: why we’re not trying to turn SpinGPT into a cheating bot).

- **Link with the student community**: helping students and volunteers discover the project and take part in the studies.
""",
            """
William est étudiant en Mathématiques et Informatique pour la Décision et les Données à l’Université Paris-Dauphine – PSL, 
et s’intéresse particulièrement à l’IA, au produit et à l’expérience utilisateur.

Dans SpinGPT, sa contribution se concentre sur :

- **Interface & UX** : rendre les interactions avec l’application web facile pour les joueurs en concevant des écrans qui permettent 
de suivre l’expérience facilement.

- **Marque & pédagogie** : raconter le projet, expliquer ce que nous faisons et ce que nous ne faisons pas 
  (par exemple : pourquoi nous ne cherchons pas à transformer SpinGPT en bot de triche).

- **Lien avec la communauté étudiante** : aider les étudiants et les volontaires à découvrir le projet et à participer aux études.
  .
"""
        )
    )

    st.markdown("[LinkedIn](https://www.linkedin.com/in/william-miserolle)")

    st.stop()





# ====================== PARTIE ======================
if st.session_state.get("sb_user"):
    st.session_state.anonymous = False


if not UI_ONLY_MODE and "poker_model" not in st.session_state:
    st.session_state.page = "loading"; st.rerun()

poker_model = st.session_state.get("poker_model")

if "player_stack" not in st.session_state:
    initialize_game()

st.markdown(f"{L('Blinds','Blindes')} : {SB}/{BB} | {L('Starting stack','Tapis de départ')} : {INITIAL_STACK}")

if st.session_state.game_over:
    ui.display_game_over(); st.stop()

ui.display_player_info()
st.markdown('---')
ui.display_board_and_pot()
st.markdown('---')
ui.display_sidebar_log()

if st.session_state.winner:
    ui.display_end_of_hand()
else:
    ui.display_action_buttons()