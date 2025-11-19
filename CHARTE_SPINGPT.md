# 🎨 Charte Graphique SpinGPT - Implémentation

Ce document décrit l'implémentation de la charte graphique SpinGPT dans l'application web.

## ✅ Modifications Appliquées

### 1. Système de Design Complet (`spingpt_brand_css.py`)

Un système de design complet a été créé avec :

- ✅ **Variables CSS** : Toutes les couleurs officielles SpinGPT
- ✅ **Header personnalisé** : Header fixe avec logo intégré
- ✅ **Boutons modernes** : Styles selon la charte (Primary bleu, Secondary blanc, Accent rouge)
- ✅ **Inputs modernes** : Design épuré avec focus bleu SpinGPT
- ✅ **Typography** : Police Inter avec hiérarchie claire
- ✅ **Cards modernes** : Cards avec ombres et hover effects
- ✅ **Grid system** : Système de grille moderne remplaçant les colonnes Streamlit
- ✅ **Animations fluides** : Transitions et animations selon les meilleures pratiques UX

### 2. Couleurs Officielles Implémentées

| Rôle                | Couleur      | HEX         | Usage                          |
| ------------------- | ------------ | ----------- | ------------------------------ |
| Primary             | Bleu profond | **#0A2A43** | Boutons primaires, titres      |
| Accent              | Rouge poker  | **#C13A3A** | Actions critiques, highlights  |
| Neutre              | Blanc        | **#FFFFFF** | Fond principal                 |
| Accent électronique | Rouge clair  | **#E54848** | Badge dealer, éléments actifs  |
| Background section  | Gris bleuté  | **#F2F6FA** | Sections, cards               |
| Texte courant       | Gris foncé   | **#2C2C2C** | Corps de texte                |

### 3. Fichiers Modifiés

1. **`spingpt_brand_css.py`** (nouveau) : Système de design complet
2. **`ui_components.py`** : Intégration du nouveau système + couleurs actions
3. **`config.py`** : Couleurs des cartes ajustées selon la charte
4. **`assets/`** (nouveau dossier) : Pour placer le logo

### 4. Logo

**Pour ajouter votre logo :**

1. Placez votre logo dans le dossier `assets/` avec un de ces noms :
   - `logo.png` (recommandé)
   - `logo.svg` (meilleure qualité)
   - `logo.jpg`

2. Le logo sera automatiquement détecté et affiché dans le header

**Taille recommandée :** 48px de hauteur (sera redimensionné automatiquement)

### 5. Utilisation

#### Classes CSS Utilitaires Disponibles

```html
<!-- Card moderne -->
<div class="spingpt-card fade-in">Contenu</div>

<!-- Grid moderne -->
<div class="spingpt-grid">
    <div class="spingpt-card">Card 1</div>
    <div class="spingpt-card">Card 2</div>
</div>

<!-- Sections avec fond gris bleuté -->
<div class="section-bg">Contenu de section</div>

<!-- Classes utilitaires -->
<span class="text-primary">Texte bleu</span>
<span class="text-accent">Texte rouge</span>
<span class="highlight-accent">Highlight rouge</span>
```

#### Dans Streamlit (Python)

```python
import streamlit as st

# Card moderne
st.markdown("""
<div class="spingpt-card fade-in">
    <h3 class="spingpt-card-title">Titre</h3>
    <p class="text-body">Contenu...</p>
</div>
""", unsafe_allow_html=True)

# Grid moderne (remplace st.columns)
st.markdown("""
<div class="spingpt-grid">
    <div class="spingpt-card">Card 1</div>
    <div class="spingpt-card">Card 2</div>
    <div class="spingpt-card">Card 3</div>
</div>
""", unsafe_allow_html=True)
```

### 6. Éléments Stylisés

- ✅ **Header fixe** : Header avec logo (72px de hauteur)
- ✅ **Sidebar** : Design épuré avec bordures subtiles
- ✅ **Boutons** : Animations hover, ombres, transitions fluides
- ✅ **Inputs** : Focus bleu SpinGPT, bordures subtiles
- ✅ **Cartes poker** : Style moderne avec hover effects
- ✅ **Metrics** : Cards pour afficher pot et stacks
- ✅ **Alerts** : Bordures colorées selon le type
- ✅ **Tables** : Design épuré avec hover rows
- ✅ **Scrollbar** : Personnalisée avec couleur SpinGPT

### 7. Responsive Design

L'interface s'adapte automatiquement :
- **Desktop** : Layout complet avec sidebar
- **Mobile** : Header réduit, layout optimisé

### 8. Animations

- **fadeIn** : Apparition en fondu depuis le bas
- **slideIn** : Glissement depuis la gauche
- **pulse** : Animation pour éléments actifs (tour de jeu)
- **hover effects** : Transformations subtiles au survol

## 🚀 Prochaines Étapes

1. **Ajouter le logo** : Placez `logo.png` dans `assets/`
2. **Tester** : Lancez `.\start-ui-only.ps1` pour voir le résultat
3. **Personnaliser** : Modifiez `spingpt_brand_css.py` si besoin d'ajustements

## 📝 Notes

- Toutes les couleurs sont définies en variables CSS pour faciliter les modifications
- Le système est compatible avec le mode UI-only
- Les animations sont optimisées pour les performances
- Le design est conforme aux meilleures pratiques UX modernes

