# spingpt_brand_css.py
# Système de design complet SpinGPT selon votre charte officielle

SPINGPT_BRAND_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ========== VARIABLES - CHARTE SPINGPT ========== */
:root {
    /* Couleurs officielles SpinGPT */
    --spingpt-primary: #0A2A43;        /* Bleu profond - Primary */
    --spingpt-accent: #C13A3A;         /* Rouge poker - Accent */
    --spingpt-neutral: #FFFFFF;        /* Blanc - Neutre */
    --spingpt-accent-light: #E54848;   /* Rouge clair - Accent électronique */
    
    /* Couleurs dérivées */
    --spingpt-primary-light: #0D3454;
    --spingpt-primary-dark: #072033;
    --spingpt-accent-hover: #A82F2F;
    --spingpt-accent-light-hover: #D83A3A;
    
    /* Backgrounds */
    --bg-main: #FFFFFF;                /* Fond principal blanc */
    --bg-section: #F2F6FA;             /* Sections gris bleuté */
    --bg-card: #FFFFFF;
    --bg-hover: rgba(10, 42, 67, 0.05);
    
    /* Text */
    --text-primary: #0A2A43;           /* Titres - bleu foncé */
    --text-body: #2C2C2C;              /* Texte courant - gris foncé */
    --text-muted: #6B7280;
    --text-on-primary: #FFFFFF;        /* Texte sur fond bleu */
    
    /* Borders & Shadows */
    --border-color: rgba(10, 42, 67, 0.15);
    --border-light: rgba(10, 42, 67, 0.08);
    --shadow-sm: 0 1px 2px 0 rgba(10, 42, 67, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(10, 42, 67, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(10, 42, 67, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(10, 42, 67, 0.15);
    
    /* Radius */
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    --radius-full: 9999px;
    
    /* Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 0.75rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
}

/* ========== RESET & BASE ========== */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
}

.stApp {
    background: var(--bg-main) !important;
    color: var(--text-body) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400;
    line-height: 1.6;
}

/* ========== CACHER ÉLÉMENTS STREAMLIT NATIFS ========== */
header[data-testid="stHeader"] { 
    display: none !important; 
}

#MainMenu { 
    visibility: hidden !important; 
    height: 0 !important;
}

footer { 
    visibility: hidden !important; 
    height: 0 !important;
}

.stDeployButton { 
    display: none !important; 
}

[data-testid="stToolbar"] {
    display: none !important;
}

/* ========== HEADER CUSTOM AVEC LOGO ========== */
.spingpt-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 88px;
    background: var(--bg-main);
    border-bottom: 2px solid var(--border-color);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--spacing-xl);
    box-shadow: var(--shadow-md);
}

.spingpt-header-logo {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
}

/* Petit toggle de langue à côté du logo */
.spingpt-lang-toggle {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-left: var(--spacing-sm);
    padding: 2px 8px;
    border-radius: var(--radius-full);
    background: var(--bg-section);
    border: 1px solid var(--border-light);
    font-size: 0.75rem;
    line-height: 1;
}

.spingpt-lang-toggle a {
    text-decoration: none !important;
    color: var(--text-body) !important;
    padding: 0 2px;
}

.spingpt-lang-toggle a:hover {
    color: var(--spingpt-primary) !important;
}

.spingpt-lang-toggle-sep {
    opacity: 0.6;
    font-size: 0.7rem;
}

/* Tagline sous le logo sur la home */
.spingpt-tagline {
    margin-top: 0.75rem;
    font-size: 1.3rem;
    font-style: italic;
    font-weight: 500;
    color: var(--spingpt-accent);
    text-align: center;
}


.spingpt-logo-img {
    height: 72px;
    width: auto;
    object-fit: contain;
    flex-shrink: 0;
}

.spingpt-header-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--spingpt-primary) !important;
    margin: 0;
    letter-spacing: -0.5px;
    line-height: 1.2;
    text-shadow: none;
    white-space: nowrap;
    display: block;
}

/* Assurer que le titre h1 dans le header soit bien stylisé - surcharge Streamlit */
.spingpt-header h1.spingpt-header-title,
.spingpt-header .spingpt-header-title,
.spingpt-header h1,
div.spingpt-header h1 {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    color: #0A2A43 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
    letter-spacing: -0.5px !important;
    text-transform: none !important;
    font-family: 'Inter', sans-serif !important;
}

/* Surcharger tous les styles Streamlit possibles sur le titre du header */
.spingpt-header h1,
.spingpt-header h1 * {
    color: #0A2A43 !important;
}

.spingpt-header-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

/* Espace pour le header fixe */
.main .block-container {
    padding-top: calc(88px + 2rem) !important;
}

/* ========== CONTAINER PRINCIPAL ========== */
.main .block-container {
    max-width: 1400px !important;
    padding: 2rem var(--spacing-xl) !important;
    margin: 0 auto !important;
    background: var(--bg-main);
}

/* Sections avec fond gris bleuté */
.section-bg {
    background: var(--bg-section);
    padding: var(--spacing-xl);
    border-radius: var(--radius-lg);
    margin: var(--spacing-lg) 0;
}

/* ========== SIDEBAR COMPLÈTEMENT MASQUÉE ========== */
[data-testid="stSidebar"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    opacity: 0 !important;
}

[data-testid="stSidebar"] * {
    display: none !important;
}

.css-1d391kg {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
}

/* ========== NAVIGATION HEADER ========== */
.spingpt-header-nav {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    flex-wrap: wrap;
}

.spingpt-nav-btn {
    background: transparent !important;
    color: var(--text-body) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.625rem 1.25rem !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    white-space: nowrap !important;
    text-decoration: none !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1.5 !important;
    letter-spacing: 0.2px !important;
}

.spingpt-nav-btn:hover {
    background: var(--bg-hover) !important;
    color: var(--spingpt-primary) !important;
    transform: translateY(-1px) !important;
}

.spingpt-nav-btn:active {
    transform: translateY(0) scale(0.98) !important;
    background: rgba(10, 42, 67, 0.1) !important;
}

.spingpt-nav-btn.nav-btn-active {
    color: var(--spingpt-primary) !important;
    font-weight: 600 !important;
    background: rgba(10, 42, 67, 0.08) !important;
}

.spingpt-nav-btn.nav-btn-active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 1.25rem;
    right: 1.25rem;
    height: 2px;
    background: var(--spingpt-primary);
    border-radius: 2px 2px 0 0;
}

/* ========== BOUTONS SPINGPT ========== */

/* Primary Button - Bleu foncé */
div.stButton > button[type="primary"],
div.stButton > button:not([kind]):not([class*="secondary"]):not([class*="tertiary"]) {
    background: var(--spingpt-primary) !important;
    color: var(--text-on-primary) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: var(--shadow-md) !important;
    cursor: pointer !important;
    letter-spacing: 0.3px;
}

div.stButton > button:hover {
    background: var(--spingpt-primary-light) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
}

div.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: var(--shadow-sm) !important;
}

div.stButton > button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
    background: var(--spingpt-primary) !important;
}

/* Secondary Button - Blanc avec bordure bleue */
div.stButton > button[kind="secondary"],
button[class*="secondary"] {
    background: var(--bg-main) !important;
    color: var(--spingpt-primary) !important;
    border: 2px solid var(--spingpt-primary) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
}

div.stButton > button[kind="secondary"]:hover {
    background: var(--spingpt-primary) !important;
    color: var(--text-on-primary) !important;
    box-shadow: var(--shadow-md) !important;
}

/* Accent Button - Rouge poker */
button[class*="accent"],
button[data-accent="true"] {
    background: var(--spingpt-accent) !important;
    color: var(--text-on-primary) !important;
    border: none !important;
}

button[class*="accent"]:hover,
button[data-accent="true"]:hover {
    background: var(--spingpt-accent-hover) !important;
}

/* Form Submit Buttons */
div.stFormSubmitButton > button {
    background: var(--spingpt-primary) !important;
    color: var(--text-on-primary) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: var(--shadow-md) !important;
}

div.stFormSubmitButton > button:hover {
    background: var(--spingpt-primary-light) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* Forcer le texte en blanc sur les boutons de soumission de formulaire (Sign in / Sign up) */
div.stFormSubmitButton > button,
div.stFormSubmitButton > button * {
    color: var(--text-on-primary) !important;
    fill: var(--text-on-primary) !important;
    -webkit-text-fill-color: var(--text-on-primary) !important;
}

/* ========== INPUTS MODERNES ========== */
div.stTextInput > div > div > input,
div.stNumberInput > div > div > input,
div[data-baseweb="input"] input,
div.stSelectbox > div > div > select,
textarea {
    background: var(--bg-main) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-body) !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', sans-serif !important;
}

div.stTextInput > div > div > input:focus,
div.stNumberInput > div > div > input:focus,
textarea:focus,
div.stSelectbox > div > div > select:focus {
    outline: none !important;
    border-color: var(--spingpt-primary) !important;
    box-shadow: 0 0 0 3px rgba(10, 42, 67, 0.1) !important;
    background: var(--bg-section) !important;
}

div.stTextInput > div > div > input::placeholder,
textarea::placeholder {
    color: var(--text-muted) !important;
    opacity: 0.7;
}

label {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    margin-bottom: 0.5rem !important;
}

/* ========== TYPOGRAPHY SPINGPT ========== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    line-height: 1.2 !important;
    font-family: 'Inter', sans-serif !important;
}

h1 { 
    font-size: 2.5rem !important; 
    font-weight: 800 !important;
}

h2 { 
    font-size: 2rem !important; 
    font-weight: 700 !important;
}

h3 { 
    font-size: 1.5rem !important; 
    font-weight: 600 !important;
}

p, span, div, li {
    color: var(--text-body) !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
}

/* Highlights en rouge poker */
.highlight-accent {
    color: var(--spingpt-accent) !important;
    font-weight: 600;
}

/* ========== CARDS MODERNES ========== */
.spingpt-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
    margin-bottom: var(--spacing-lg);
}

.spingpt-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
    border-color: var(--spingpt-primary);
}

.spingpt-card-header {
    border-bottom: 1px solid var(--border-light);
    padding-bottom: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.spingpt-card-title {
    color: var(--text-primary);
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
}

/* ========== GRID SYSTEM ========== */
.spingpt-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
    margin: var(--spacing-xl) 0;
}

.spingpt-flex {
    display: flex;
    gap: var(--spacing-md);
    flex-wrap: wrap;
}

/* ========== ALERTS MODERNES ========== */
div.stAlert {
    border-radius: var(--radius-md) !important;
    border: none !important;
    padding: 1rem 1.5rem !important;
    box-shadow: var(--shadow-md) !important;
    background: var(--bg-section) !important;
}

div.stAlert[data-baseweb="notification"] {
    border-left: 4px solid var(--spingpt-primary) !important;
    color: var(--text-body) !important;
}

div.stAlert.warning {
    border-left-color: var(--spingpt-accent) !important;
    background: rgba(193, 58, 58, 0.05) !important;
}

div.stAlert.error {
    border-left-color: var(--spingpt-accent) !important;
    background: rgba(193, 58, 58, 0.08) !important;
    color: var(--spingpt-accent) !important;
}

div.stAlert.success {
    border-left-color: #10b981 !important;
    background: rgba(16, 185, 129, 0.05) !important;
}

/* ========== METRICS MODERNES ========== */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    padding: var(--spacing-lg);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--spingpt-primary);
}

div[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 2.5rem !important;
}

div[data-testid="stMetricLabel"] {
    color: var(--text-body) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    margin-top: 0.5rem;
}

/* ========== TABLES MODERNES ========== */
.dataframe {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border-color) !important;
}

.dataframe th {
    background: var(--bg-section) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    padding: 1rem !important;
    border-bottom: 2px solid var(--border-color) !important;
}

.dataframe td {
    color: var(--text-body) !important;
    padding: 0.75rem 1rem !important;
    border-bottom: 1px solid var(--border-light) !important;
}

.dataframe tr:hover {
    background: var(--bg-hover) !important;
}

/* ========== CARTES POKER ========== */
span.playing-card {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 80px;
    margin: 0 4px;
    background: var(--bg-main) !important;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-md);
    font-size: 38px;
    font-weight: 600;
    letter-spacing: 0;
    line-height: 1;
    color: var(--text-body);
    transition: all 0.3s ease;
}

span.playing-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--spingpt-primary);
}

.board-cards .playing-card {
    font-size: 34px;
    width: 48px;
    height: 64px;
}

/* ========== DEALER BADGE ========== */
.dealer-badge {
    display: inline-block;
    padding: 6px 12px;
    margin-left: 10px;
    border-radius: var(--radius-full);
    background: var(--spingpt-accent-light) !important;
    color: var(--text-on-primary) !important;
    font-weight: 700;
    font-size: 0.875rem;
    line-height: 1;
    border: none;
    box-shadow: var(--shadow-sm);
}

/* ========== CONTRIBUTIONS & ACTIONS ========== */
.contrib {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--spingpt-accent) !important;
    margin-top: -4px;
}

.active-turn {
    animation: pulse 1.5s infinite alternate;
    color: var(--spingpt-accent-light) !important;
}

@keyframes pulse {
    from {
        transform: scale(1);
        opacity: 1;
    }
    to {
        transform: scale(1.05);
        opacity: 0.8;
    }
}

/* ========== STACK & POT ========== */
.player-stack {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary) !important;
}

.pot-center {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary) !important;
}

/* ========== ANIMATIONS ========== */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideIn {
    from {
        transform: translateX(-20px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

.slide-in {
    animation: slideIn 0.4s ease-out;
}

/* ========== SCROLLBAR ========== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-section);
}

::-webkit-scrollbar-thumb {
    background: var(--spingpt-primary);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--spingpt-primary-light);
}

/* ========== LOADING STATES ========== */
.loading-spinner {
    border: 3px solid rgba(10, 42, 67, 0.1);
    border-top: 3px solid var(--spingpt-primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem !important;
    }
    
    .spingpt-header {
        padding: 0 var(--spacing-md);
        height: 72px;
    }
    
    .spingpt-header-title {
        font-size: 1.4rem;
        font-weight: 800;
    }
    
    .spingpt-logo-img {
        height: 56px;
    }
    
    .spingpt-header-logo {
        gap: var(--spacing-sm);
    }
    
    .spingpt-grid {
        grid-template-columns: 1fr;
    }
    
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.25rem !important; }
}

/* ========== UTILITAIRES ========== */
.text-primary { color: var(--text-primary) !important; }
.text-body { color: var(--text-body) !important; }
.text-accent { color: var(--spingpt-accent) !important; }
.bg-section { background: var(--bg-section) !important; }
.border-primary { border-color: var(--spingpt-primary) !important; }

</style>
"""

SPINGPT_HEADER_HTML = """
<div class="spingpt-header fade-in">
    <div class="spingpt-header-logo">
        <img src="{logo_path}" alt="SpinGPT Logo" class="spingpt-logo-img" />
        <h1 class="spingpt-header-title">SpinGPT</h1>
        <div class="spingpt-lang-toggle">
            <a href="?lang=en" class="spingpt-lang-en" target="_self">EN</a>
            <span class="spingpt-lang-toggle-sep">/</span>
            <a href="?lang=fr" class="spingpt-lang-fr" target="_self">FR</a>
        </div>
    </div>
    <div class="spingpt-header-actions">
        <div class="spingpt-header-nav" id="spingpt-header-nav">
            <!-- Navigation sera injectée ici via JavaScript -->
        </div>
    </div>
</div>
"""

def inject_spingpt_brand_css(logo_path: str = None, nav_html: str = ""):
    """Injecte le CSS de la marque SpinGPT"""
    import streamlit as st
    import base64
    import os
    
    st.markdown(SPINGPT_BRAND_CSS, unsafe_allow_html=True)
    
    # Si pas de logo_path fourni, chercher automatiquement
    if not logo_path:
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
    
    # Préparer le HTML de navigation (vide par défaut, sera rempli par JavaScript)
    nav_content = nav_html if nav_html else '<div class="spingpt-header-nav" id="spingpt-header-nav"></div>'
    
    if logo_path:
        try:
            # Si c'est un chemin local, convertir en base64
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_data = base64.b64encode(f.read()).decode()
                    ext = os.path.splitext(logo_path)[1][1:].lower()
                    # Gérer différents types d'images
                    mime_types = {
                        'png': 'image/png',
                        'jpg': 'image/jpeg',
                        'jpeg': 'image/jpeg',
                        'svg': 'image/svg+xml',
                        'gif': 'image/gif'
                    }
                    mime_type = mime_types.get(ext, 'image/png')
                    logo_base64 = f"data:{mime_type};base64,{logo_data}"
                    header_html = SPINGPT_HEADER_HTML.format(logo_path=logo_base64)
                    # Remplacer le placeholder de navigation
                    if nav_html:
                        header_html = header_html.replace(
                            '<div class="spingpt-header-nav" id="spingpt-header-nav">\n            <!-- Navigation sera injectée ici via JavaScript -->',
                            f'<div class="spingpt-header-nav" id="spingpt-header-nav">{nav_html}'
                        )
                    st.markdown(header_html, unsafe_allow_html=True)
            else:
                # Si c'est déjà une URL ou chemin relatif, utiliser tel quel
                header_html = SPINGPT_HEADER_HTML.format(logo_path=logo_path)
                # Remplacer le placeholder de navigation
                if nav_html:
                    header_html = header_html.replace(
                        '<div class="spingpt-header-nav" id="spingpt-header-nav">\n            <!-- Navigation sera injectée ici via JavaScript -->',
                        f'<div class="spingpt-header-nav" id="spingpt-header-nav">{nav_html}'
                    )
                st.markdown(header_html, unsafe_allow_html=True)
        except Exception as e:
            # Si erreur, continuer sans logo mais avec le CSS
            pass
    else:
        # Header sans logo avec navigation
        header_html = f"""
        <div class="spingpt-header fade-in">
            <div class="spingpt-header-logo">
                <h1 class="spingpt-header-title">SpinGPT</h1>
                <div class="spingpt-lang-toggle">
                    <a href="?lang=en" class="spingpt-lang-en" target="_self">EN</a>
                    <span class="spingpt-lang-toggle-sep">/</span>
                    <a href="?lang=fr" class="spingpt-lang-fr" target="_self">FR</a>
                </div>
            </div>
            <div class="spingpt-header-actions">
                {nav_content}
            </div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    

