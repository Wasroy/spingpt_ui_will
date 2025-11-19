# Guide Mode UI-Only

## 🎨 Mode UI-Only - Pour travailler uniquement sur l'apparence

Ce mode a été spécialement configuré pour vous permettre de modifier uniquement l'apparence du site sans avoir besoin de configurer le backend (base de données Supabase et modèle IA).

## 🚀 Démarrage rapide

### Méthode 1 : Script dédié (le plus simple)
```powershell
.\start-ui-only.ps1
```

### Méthode 2 : Variable d'environnement
```powershell
$env:UI_ONLY_MODE = "true"
.\venv\Scripts\python.exe -m streamlit run app.py
```

### Méthode 3 : Fichier .env
Créez un fichier `.env` à la racine avec :
```env
UI_ONLY_MODE=true
```
Puis lancez normalement :
```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

## ✅ Ce qui fonctionne en mode UI-Only

- ✅ **Navigation complète** : Toutes les pages sont accessibles (Home, Auth, Profile, Leaderboard, Game)
- ✅ **Interface de jeu** : Vous pouvez voir l'interface de poker avec les cartes, boutons, etc.
- ✅ **Modification CSS** : Tous les styles dans `ui_components.py` sont actifs
- ✅ **Changements en temps réel** : Streamlit recharge automatiquement vos modifications
- ✅ **Pas d'authentification requise** : Cliquez directement sur "Nouvelle partie" pour voir le jeu

## ⚠️ Ce qui est désactivé en mode UI-Only

- ❌ **Base de données Supabase** : Pas de sauvegarde des parties, pas de classement réel
- ❌ **Modèle IA réel** : Remplacé par un mock simple (l'IA fait toujours "call")
- ❌ **Authentification** : Les fonctionnalités de connexion/inscription ne sont pas actives

## 📁 Fichiers à modifier pour l'apparence

### Principaux fichiers UI :
- **`ui_components.py`** : 
  - Variable `GLOBAL_CSS` : Styles globaux (couleurs, boutons, inputs, etc.)
  - Variable `ACTIONS_CSS` : Styles pour les actions dans le timeline
  - Fonctions `display_*` : Composants visuels du jeu

- **`app.py`** : 
  - Structure HTML des pages
  - Textes et contenus affichés

### Exemple de modification rapide :

Dans `ui_components.py`, vous pouvez changer les couleurs :
```python
GLOBAL_CSS = """
<style>
.stApp{
    background:radial-gradient(circle at 50% 0%, #4f8c5d 0%, #437c52 35%, #2d5d3a 100%);
}
/* Changez ces couleurs pour modifier le thème */
</style>
"""
```

## 🔄 Redémarrer après modification

Streamlit recharge automatiquement les fichiers modifiés. Si ce n'est pas le cas :
- Cliquez sur "Rerun" dans le menu Streamlit (≡ en haut à droite)
- Ou utilisez le raccourci `R` dans la console Streamlit

## 💡 Astuces

1. **Voir toutes les pages** : Utilisez le menu sidebar pour naviguer entre Home, Auth, Profile, Leaderboard
2. **Tester le jeu** : Cliquez sur "Nouvelle partie" dans la sidebar pour voir l'interface de jeu
3. **Mode développement** : Ouvrez les DevTools du navigateur (F12) pour inspecter les éléments
4. **Styles inline** : Vous pouvez aussi ajouter du CSS directement dans les `st.markdown()` avec `unsafe_allow_html=True`

## 🎯 Prochaines étapes

Une fois satisfait de l'apparence, vous pouvez :
1. Désactiver le mode UI-Only en supprimant `UI_ONLY_MODE=true` ou en ne définissant pas la variable
2. Configurer Supabase et HuggingFace pour utiliser l'application en mode complet

## ❓ Problèmes courants

**L'application ne démarre pas :**
- Vérifiez que l'environnement virtuel est activé : `.\venv\Scripts\python.exe`
- Vérifiez que Streamlit est installé : `pip install streamlit`

**Les modifications CSS ne s'appliquent pas :**
- Vérifiez que vous modifiez bien `GLOBAL_CSS` dans `ui_components.py`
- Redémarrez Streamlit (Ctrl+C puis relancez)

**Erreur "model not found" :**
- C'est normal en mode UI-Only, le modèle est remplacé par un mock. Vous pouvez ignorer cette erreur si vous ne travaillez que sur l'UI.

