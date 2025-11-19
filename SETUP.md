# Guide d'installation et de démarrage - SpinGPT Web v2

## Prérequis

- Python 3.9 ou supérieur
- Un compte Supabase (pour SUPABASE_URL et SUPABASE_ANON_KEY) - **uniquement en mode production**
- Un token HuggingFace (pour HF_TOKEN) - **uniquement en mode production**

## Mode UI-Only (pour travailler sur l'apparence uniquement)

Si vous voulez uniquement modifier l'apparence du site sans avoir besoin du backend (base de données et IA), vous pouvez utiliser le **mode UI-Only**.

### Avantages du mode UI-Only :
- ✅ Pas besoin de configurer Supabase
- ✅ Pas besoin de token HuggingFace
- ✅ L'application démarre instantanément (pas de chargement du modèle IA)
- ✅ Parfait pour modifier uniquement les fichiers CSS et UI
- ✅ Vous pouvez voir toutes les pages et tester l'interface

### Comment activer le mode UI-Only :

**Option 1 : Script de lancement dédié (recommandé)**
```powershell
.\start-ui-only.ps1
```

**Option 2 : Variable d'environnement**
```powershell
$env:UI_ONLY_MODE = "true"
.\venv\Scripts\python.exe -m streamlit run app.py
```

**Option 3 : Fichier .env**
Créez un fichier `.env` avec :
```env
UI_ONLY_MODE=true
```

En mode UI-Only :
- L'authentification est désactivée (vous pouvez cliquer sur "Nouvelle partie" directement)
- Le modèle IA est remplacé par un mock simple
- Les fonctionnalités de base de données sont désactivées
- Vous pouvez naviguer entre toutes les pages pour voir l'apparence

## Installation

### 1. Créer et activer l'environnement virtuel

```powershell
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel (PowerShell)
.\venv\Scripts\Activate.ps1

# Ou si vous utilisez cmd
.\venv\Scripts\activate.bat
```

### 2. Installer les dépendances

```powershell
pip install -r requirements.txt
```

**Note :** Si vous rencontrez des erreurs de fichiers verrouillés, attendez quelques secondes et réessayez :
```powershell
.\venv\Scripts\python.exe -m pip install --no-cache-dir streamlit torch transformers peft accelerate supabase pyngrok
```

### 3. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
SUPABASE_URL=votre_url_supabase
SUPABASE_ANON_KEY=votre_cle_supabase
HF_TOKEN=votre_token_huggingface
```

**Où obtenir ces valeurs :**
- **SUPABASE_URL** et **SUPABASE_ANON_KEY** : Dans votre projet Supabase, allez dans Settings > API
- **HF_TOKEN** : Sur [huggingface.co](https://huggingface.co), allez dans Settings > Access Tokens

**Alternative :** Vous pouvez aussi définir ces variables directement dans votre terminal PowerShell avant de lancer l'app :

```powershell
$env:SUPABASE_URL="votre_url"
$env:SUPABASE_ANON_KEY="votre_cle"
$env:HF_TOKEN="votre_token"
```

## Lancer l'application

### Avec l'environnement virtuel activé :

```powershell
streamlit run app.py
```

### Sans activer l'environnement virtuel :

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

## Notes importantes

1. **Premier lancement** : Le modèle IA sera téléchargé au premier lancement, ce qui peut prendre du temps selon votre connexion.

2. **Configuration Windows** : Le chemin des logs a été adapté pour Windows. Les logs seront sauvegardés dans `%APPDATA%\spinGPT\logs\25BB\`

3. **Problèmes courants** :
   - Si le modèle ne se charge pas, vérifiez que `HF_TOKEN` est correctement défini
   - Si Supabase ne fonctionne pas, vérifiez vos credentials dans `.env` ou les variables d'environnement

## Structure du projet

- `app.py` : Application principale Streamlit
- `config.py` : Configuration (blinds, stacks, chemins de logs, etc.)
- `ia_model.py` : Chargement du modèle IA
- `ia_bridge.py` : Interface entre le jeu et l'IA
- `poker_engine.py` : Moteur de jeu de poker
- `app_state.py` : Gestion de l'état de l'application
- `ui_components.py` : Composants UI
- `supabase_utils.py` : Utilitaires Supabase

## Support

Pour toute question, contactez : narada.maugin [at] gmail.com

