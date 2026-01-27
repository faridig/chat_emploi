# DESIGN.md - Chat Emploi
## Document de Design UX/UI
### Version 1.0 - MVP
**Date** : 27 janvier 2026  
**Lead Designer** : UX/UI Expert  
**Statut** : Validé avec le Product Owner  

---

## 1. Principes de Design

### 1.1 Principes Fondamentaux
- **Empathique** : L'interface encourage, comprend et soutient sans jugement
- **Minimal & Apaisant** : Épuré, pas de surcharge visuelle, espace pour respirer
- **Progressif** : Chaque étape avance vers un objectif concret (l'emploi)
- **Contextuel** : L'interface s'adapte au stade du parcours utilisateur
- **Micro-Interactif** : Feedback subtil qui récompense l'action

### 1.2 Ton & Personnalité
- **Coach bienveillant** : Comme un ami expérimenté qui vous soutient
- **Encourageant mais réaliste** : Optimiste sans être naïf
- **Professionnel accessible** : Expert mais pas intimidant
- **Franc mais délicat** : Direct dans les conseils, doux dans la formulation

---

## 2. Guide de Style (Base)

### 2.1 Palette de Couleurs

#### Palette Principale (Apaisante & Encourageante)
```
--color-primary: #4A90E2;       /* Bleu confident mais chaleureux */
--color-primary-light: #7BB4F5; /* Variante légère pour hover */
--color-secondary: #50C878;     /* Vert d'espoir, croissance */
--color-secondary-light: #80E0A7;

--color-background: #F8FAFC;    /* Fond très léger gris bleuté */
--color-surface: #FFFFFF;       /* Surfaces (cartes, panneaux) */
--color-border: #E2E8F0;       /* Bordures subtiles */

--color-text-primary: #1A202C;  /* Texte principal - bon contraste */
--color-text-secondary: #718096;/* Texte secondaire */
--color-text-tertiary: #A0AEC0; /* Texte discrétionnaire */
```

#### Palette d'États
```
--color-success: #38A169;       /* Succès (vert plus franc) */
--color-warning: #D69E2E;       /* Attention (orange doux) */
--color-error: #E53E3E;         /* Erreur (rouge mais pas agressif) */
--color-info: #4299E1;          /* Information (bleu vif) */
```

#### Accents Ludiques (Utilisation parcimonieuse)
```
--color-accent-warm: #FF6B6B;   /* Pour micro-interactions spéciales */
--color-accent-cool: #9F7AEA;   /* Accents occasionnels */
```

### 2.2 Typographie

#### Familles de Polices
- **Police Principale** : `Inter` ou `System UI` (sans-serif moderne, excellente lisibilité)
- **Police Code/Monospace** : `JetBrains Mono` ou `Monospace system` (pour preview code)

#### Échelle Typographique (scale 1.25)
```
--text-xs: 0.75rem;    /* 12px - légendes, micro-textes */
--text-sm: 0.875rem;   /* 14px - corps secondaire */
--text-base: 1rem;     /* 16px - corps principal */
--text-lg: 1.125rem;   /* 18px - sous-titres */
--text-xl: 1.25rem;    /* 20px - titres sections */
--text-2xl: 1.5rem;    /* 24px - titres principaux */
--text-3xl: 1.875rem;  /* 30px - hero, accroches */
```

#### Styles de Texte
- **Titres** : `font-weight: 600`, `letter-spacing: -0.025em`
- **Corps** : `font-weight: 400`, `line-height: 1.6`
- **Labels/Boutons** : `font-weight: 500`, `letter-spacing: 0.025em`

### 2.3 Iconographie
- **Style** : Ligne fine (`stroke-width: 1.5`) avec coins légèrement arrondis
- **Consistance** : Taille standard `20px` pour les actions, `24px` pour la navigation
- **Librairie** : `Lucide Icons` ou `Heroicons` pour cohérence
- **Couleur** : `--color-text-secondary` par défaut, `--color-primary` au hover/actif

### 2.4 Espacement & Grille
- **Unité de base** : `4px` (tout espacement multiple de 4)
- **Grille** : `8px` pour micro-espacements, `16px` pour espacements standard
- **Conteneurs** : `max-width: 1200px` pour contenu, `padding: 24px` sur desktop
- **Cartes/Panneaux** : `border-radius: 12px`, `box-shadow: 0 1px 3px rgba(0,0,0,0.1)`

### 2.5 Éléments d'Illustration
- **Style** : Illustrations vectorielles minimales, traits organiques
- **Couleurs** : Palette principale en tons pastels (30% opacity pour fonds)
- **Utilisation** : Uniquement pour les états vides, écrans d'accueil, feedback positifs
- **Thème** : Métaphores de croissance (plantes, étoiles, chemins), diversité inclusive

---

## 3. Sitemap / Architecture

### 3.1 Arborescence des Écrans
```
APP (Desktop Electron)
├── ÉCRAN D'ACCUEIL
│   ├── Import CV (drag & drop)
│   ├── Bienvenue + présentation agent
│   └── Démarrer nouvelle session
│
├── SESSION GUIDÉE (navigation contextuelle)
│   ├── ÉTAPE 1 : Profil & Objectifs (chat)
│   ├── ÉTAPE 2 : Recherche d'Offres
│   ├── ÉTAPE 3 : Sélection & Matching
│   ├── ÉTAPE 4 : Génération Lettre
│   ├── ÉTAPE 5 : Préparation Entretien
│   └── ÉTAPE 6 : Ajout au Dashboard
│
├── DASHBOARD (vue globale)
│   ├── Vue Kanban (Postulées/En cours/...)
│   ├── Détails candidature
│   ├── Notes & Rappels
│   └── Statistiques personnelles
│
├── PARAMÈTRES
│   ├── Préférences interface
│   ├── Gestion données locales
│   ├── Config API (Gemini, France Travail)
│   └── À propos & aide
│
└── MODAUX CONTEXTUELS
    ├── Prévisualisation CV
    ├── Détails offre complète
    ├── Éditeur lettre de motivation
    ├── Simulateur entretien
    └── Feedback utilisateur
```

### 3.2 Navigation Contextuelle
- **Barre supérieure fixe** : Timeline de progression + avatar agent + actions globales
- **Panneau latéral droit** : Contenu contextuel (CV en cours, offre sélectionnée, notes)
- **Zone principale centrale** : Contenu actif (chat, liste offres, dashboard)
- **Barre inférieure** : Actions locales (suivant/précédent, export, aide)

---

## 4. Description Détaillée des Écrans Clés

### 4.1 Écran d'Accueil (Premier Lancement)

#### Éléments Visibles
```
[HEADER]
  - Logo Chat Emploi (petit)
  - Tagline : "Votre coach emploi empathique"

[MAIN CONTENT - Centré]
  - Illustration : main tendue avec petite plante
  - Titre : "Bienvenue ! Prêt à transformer votre recherche ?"
  - Sous-titre : "Importez votre CV pour commencer"

  [ZONE DRAG & DROP]
    - Icône upload (size: 64px)
    - Texte : "Glissez-déposez votre CV ici"
    - Formats supportés : PDF, DOCX, TXT
    - Bouton "Parcourir les fichiers"

  [INFORMATIONS]
    - Badge : "🔒 Confidentialité totale"
    - Texte : "Vos données restent sur votre ordinateur"
    - Lien "En savoir plus sur l'anonymisation"

[FOOTER]
  - Bouton secondaire : "Mode démo (sans CV)"
  - Indicateur : "Première connexion"
```

#### États
- **Vide** : Comme ci-dessus
- **Drag active** : Zone surlignée `--color-primary-light` avec opacité 30%
- **Chargement** : Animation de progression circulaire + texte "Analyse en cours..."
- **Erreur** : Message en haut "Format non supporté" + suggestion de correction

#### Interactions
- **Drag & Drop** : Feedback visuel immédiat (bordure pulsing)
- **Hover zone** : Léger changement de couleur de fond
- **Click parcourir** : Open file dialog natif
- **Succès** : Transition automatique vers Étape 1 (3 secondes)

### 4.2 Écran Conversation (Étape 1)

#### Éléments Visibles
```
[HEADER FIXE - Timeline de Progression]
  - 6 indicateurs visuels : CV → Profil → Recherche → Lettre → Entretien → Suivi
  - Indicateur actif : "Profil" surligné + illustration micro
  - Progression : barre fine colorée connectant les étapes accomplies

[ZONE CHAT PRINCIPALE]
  [MESSAGE BIENVENUE - Agent]
    - Avatar agent (illustration stylisée)
    - Bulle : "Bonjour ! Je suis Alex, votre coach emploi. 
      Ravie de vous rencontrer ! Parlez-moi de votre situation..."
    - Indicateur "En train d'écrire..." (animation points)

  [INPUT UTILISATEUR]
    - Textarea avec placeholder : "Je recherche un poste de..."
    - Boutons actions rapides :
      * "Je suis en reconversion"
      * "Je cherche mon premier emploi"
      * "Je veux évoluer dans mon domaine"
    - Bouton envoyer (flèche droite)

[PANEL LATÉRAL DROIT - Contexte]
  - Titre : "Votre profil en cours"
  - Carte CV : titre, expériences clés (extraites)
  - Indicateur : "Complétude : 40%" + barre de progression
  - Suggestions : "Pensez à mentionner : vos soft skills"
```

#### États
- **Conversation normale** : Bulles alternées agent/utilisateur
- **Agent réfléchit** : Avatar avec animation subtile (léger pulse) + texte "Réflexion en cours..."
- **Génération longue** (lettre, recherche) : Overlay semi-transparent avec estimation temps
- **Erreur API** : Message empathique "Je rencontre un petit problème technique, un instant..."

#### Interactions
- **Envoyer message** : Animation d'envoi (bulle qui glisse)
- **Réponse agent** : Apparition progressive (typewriter effect)
- **Click suggestions** : Pré-remplit l'input
- **Hover avatar** : Tooltip "Alex, votre coach - Spécialiste reconversion"

### 4.3 Écran Recherche d'Offres (Étape 2-3)

#### Éléments Visibles
```
[HEADER]
  - Timeline : Étape "Recherche" active
  - Titre : "Offres qui pourraient vous correspondre"
  - Sous-titre : "Basé sur votre profil et vos objectifs"

[FILTRES RAPIDES]
  - Localisation : dropdown + badge "Paris"
  - Type de contrat : Toggle group (CDI, CDD, Stage...)
  - Télétravail : Toggle switch
  - Bouton "Actualiser la recherche"

[LISTE DES OFFRES]
  [CARTE OFFRE - Composant]
    - Badge matching : "92% de compatibilité" (couleur gradient selon score)
    - Titre poste + entreprise (en gras)
    - Localisation + type contrat + date publication
    - Extrait : premières lignes de la description
    - Compétences clés : badges (max 3)
    - Actions : "Voir détails" | "Générer lettre" | "Ignorer"

  [PAGINATION]
    - Boutons Précédent/Suivant
    - Indicateur "5 offres sur 47 correspondantes"

[PANEL DÉTAILS (modale on click)]
  - Description complète avec mise en forme
  - Exigences en liste
  - Avantages entreprise
  - Boutons d'action primaires
```

#### États
- **Chargement** : 5 cartes skeleton avec animation shimmer
- **Aucun résultat** : Illustration + "Aucune offre exacte aujourd'hui. Essayez d'élargir vos critères ?"
- **Recherche en cours** : Indicateur "Scan des nouvelles offres..." + compteur
- **Erreur API** : "Les offres sont temporairement indisponibles. Voulez-vous retenter ?"

#### Interactions
- **Hover carte** : Léger élévation (shadow) + bordure colorée
- **Click compatibilité** : Tooltip expliquant le calcul
- **Drag carte** : Vers la zone "Favoris" ou "À ignorer"
- **Scroll** : Infinite scroll avec lazy loading

### 4.4 Écran Génération Lettre (Étape 4)

#### Éléments Visibles
```
[HEADER]
  - Timeline : Étape "Lettre" active
  - Titre : "Lettre de motivation pour [Poste] chez [Entreprise]"
  - Badge : "Génération personnalisée en cours"

[ZONE ÉDITION DEUX COLONNES]
  [COLONNE GAUCHE - Prévisualisation]
    - Rendu lettre format A4 (ombre portée)
    - Mise en forme typographique professionnelle
    - Surlignage des passages personnalisés (couleur pastel)
    - Indicateur "325 mots - Longueur idéale"

  [COLONNE DROITE - Personnalisation]
    - Section "Ton souhaité" : slider Amical → Professionnel
    - Section "Points à mettre en avant" : checklist (3-5 items pré-sélectionnés)
    - Section "Expériences à inclure" : toggle experiences du CV
    - Section "Projets spécifiques" : input optionnel
    - Bouton "Regénérer avec ces paramètres"

[ACTIONS]
  - Bouton principal : "Télécharger PDF" (icône download)
  - Bouton secondaire : "Copier le texte"
  - Bouton tertiaire : "Générer une alternative"
  - Indicateur : "Lettre sauvegardée automatiquement"
```

#### États
- **Génération** : Animation de construction (blocs qui s'assemblent)
- **Prévisualisation** : Mode lecture avec surlignages
- **Édition** : Mode focus sur la colonne droite
- **Export réussi** : Confirmation subtile + animation de téléchargement

#### Interactions
- **Hover passage** : Tooltip "Basé sur votre expérience en [domaine]"
- **Click ton** : Prévisualisation immédiate du changement
- **Drag slider** : Aperçu en temps réel de l'impact
- **Click regénérer** : Animation de rafraîchissement

### 4.5 Dashboard (Vue Globale)

#### Éléments Visibles
```
[HEADER]
  - Titre : "Vos candidatures"
  - Statistiques rapides : "12 postulées • 3 entretiens • 1 offre"
  - Bouton "Nouvelle recherche"

[VUE KANBAN]
  [COLONNE "Postulées"]
    - Carte candidature : Entreprise, Poste, Date, Badge "Lettre générée"
    - Action : "Préparer l'entretien" | "Marquer refusée"

  [COLONNE "Entretiens"]
    - Carte avec date/heure en évidence
    - Countdown : "Entretien dans 2 jours"
    - Bouton "Mode préparation intensive"

  [COLONNE "Offres reçues"]
    - Carte avec montant/contrat en évidence
    - Actions décisionnelles

[PANEL STATISTIQUES]
  - Graphique secteur d'activité
  - Taux de réponse (courbe)
  - Temps moyen entre candidature et réponse
  - Suggestions : "Vous avez 90% de succès dans le secteur Tech"
```

#### États
- **Vide** : Illustration + "Commencez votre première recherche !"
- **Données limitées** : Message encourageant "Les premières candidatures sont les plus importantes"
- **Beaucoup de données** : Options de filtrage avancé activées

#### Interactions
- **Drag & Drop entre colonnes** : Feedback visuel + animation fluide
- **Hover carte** : Affichage notes privées
- **Click statistique** : Drill-down sur les données
- **Click nouvelle recherche** : Retour à l'étape 1 avec contexte préservé

---

## 5. Comportements Globaux

### 5.1 Système de Progression Visuelle (Idée 1 validée)

#### Implementation Timeline
- **Position** : Barre horizontale fixe en haut (hauteur : 60px)
- **Étapes** : Icône + label court, connectées par une ligne de progression
- **Animation** :
  - Étape accomplie : Icône se remplit de couleur, petite étoile apparaît
  - Transition entre étapes : Ligne se remplit avec animation liquide
  - Toutes étapes accomplies : Mini-feu d'artifice discret

#### Feedback Micro
- **Accomplissement** : Son doux (optionnel) + vibration légère si périphérique supporte
- **Rétroaction** : Au survol d'une étape passée, rappel de ce qui a été fait
- **Encouragement** : Messages contextuels "Bravo ! Votre profil est complet" au passage d'étape

### 5.2 Système de Feedback Micro-Interactif (Idée 3 validée)

#### Messages Contextuels Empathiques
- **Au lieu de** : "CV importé"
- **Remplacer par** : "✓ Excellent ! J'ai bien saisi vos 5 ans d'expérience en gestion de projet"

#### Animations Subtiles
1. **Agent pense** : Avatar avec halo pulsant très lentement
2. **Action réussie** : Petite plante qui pousse dans le coin inférieur droit
3. **Échec/Erreur** : Nuage qui passe avec expression compatissante
4. **Attente longue** : Animation de café/patience "Je prends le temps qu'il faut"

#### Avatar Réactif
- **Écoute** : Tête légèrement penchée, yeux attentifs
- **Réflexion** : Main au menton, yeux vers le haut
- **Encouragement** : Sourire chaleureux, pouce levé discret
- **Félicitations** : Confettis miniatures autour de l'avatar

### 5.3 Transitions & Animations

#### Principes
- **Durée** : 200-300ms pour les transitions principales
- **Easing** : `cubic-bezier(0.4, 0, 0.2, 1)` (standard material)
- **Performance** : Préférer transform/opacity aux propriétés coûteuses

#### Transitions Clés
1. **Changement d'écran** : Fade out/in avec léger slide horizontal
2. **Apparition modale** : Scale up depuis le centre avec backdrop flou
3. **Notifications toast** : Slide from bottom avec fade
4. **Changement d'état** : Morphing smooth entre les états

### 5.4 États Spéciaux & Gestion d'Erreurs

#### États de Chargement
- **Skeleton screens** : Pour le contenu qui prend >500ms
- **Placeholder progressif** : Contenu partiel affiché pendant le chargement
- **Indicateur d'activité** : Animation subtile dans la barre de progression

#### Messages d'Erreur Empathiques
```
HIÉRARCHIE :
1. Notification toast (non intrusive) : "Oups, petit problème technique"
2. Message inline dans le contexte : "Je n'arrive pas à accéder aux offres pour le moment"
3. Écran d'erreur dédié (seulement si blocage complet) avec illustration et solutions
```

#### États Vides (Empty States)
- Toujours une illustration + message encourageant + CTA clair
- Exemple : "Pas encore d'offres favorites. Trouvez-en une qui vous plaît !"

### 5.5 Accessibilité & Inclusivité

#### Contraste & Lisibilité
- **Contraste minimum** : 4.5:1 pour le texte normal, 3:1 pour les grands textes
- **Taille de texte** : Scalable jusqu'à 200% sans perte de fonctionnalité
- **Focus visible** : Outline clair pour la navigation clavier

#### Navigation Clavier
- **Tab order** : Logique, suit le flux visuel
- **Raccourcis** : 
  - `Cmd/Ctrl + N` : Nouvelle recherche
  - `Cmd/Ctrl + S` : Sauvegarder session
  - `Esc` : Fermer modale/quitter édition

#### Mode Sombre (Future Phase)
- Palette préparée pour conversion facile
- Couleurs avec suffisamment de luminance différentielle
- Preference media query `prefers-color-scheme`

---

## 6. Patterns Réutilisables (Design System)

### 6.1 Composants de Base

#### Boutons
```
.btn-primary
  - Couleur: --color-primary
  - Hover: --color-primary-light
  - Animation: scale(1.02) au hover

.btn-secondary
  - Fond transparent, bordure
  - Hover: fond léger

.btn-text
  - Lien stylé comme bouton
  - Animation: underline from center
```

#### Cartes (Cards)
```
.card
  - border-radius: 12px
  - box-shadow: 0 2px 8px rgba(0,0,0,0.08)
  - transition: transform 0.2s, box-shadow 0.2s

.card:hover
  - transform: translateY(-2px)
  - box-shadow: 0 4px 12px rgba(0,0,0,0.12)
```

#### Inputs & Formulaires
```
.input
  - border: 1px solid --color-border
  - border-radius: 8px
  - focus: border-color --color-primary + glow subtil

.input-error
  - border-color: --color-error
  - icon warning + message d'aide
```

### 6.2 Feedback Components

#### Toast Notifications
- Position: Bottom right
- Durée: 5s (6s pour erreurs)
- Animation: Slide up + fade
- Types: Succès (✓), Erreur (!), Info (i), Avertissement (⚠)

#### Tooltips
- Délai d'apparition: 300ms
- Durée max: 10s
- Position: Préférer top/bottom, éviter de cacher le contenu

#### Loaders & Spinners
- Pour actions <2s: Spinner simple
- Pour actions 2-10s: Spinner + pourcentage/progression
- Pour actions >10s: Spinner + message d'estimation

---

## 7. Guidelines d'Implémentation Frontend

### 7.1 Structure CSS/JS
- **Approche** : CSS Modules ou Styled Components pour le scope
- **Variables** : Toutes les couleurs/espaces en CSS Custom Properties
- **Breakpoints** : Desktop uniquement, mais prévoir mobile pour le futur
- **Performance** : Lazy loading des illustrations/animations complexes

### 7.2 Animations Performance
```css
/* BON */
transform: translateY(-2px);
opacity: 0.9;

/* À ÉVITER */
margin-top: -2px;
filter: blur(1px); /* Coûteux */
```

### 7.3 Assets & Illustrations
- **Format** : SVG pour les illustrations (vectoriel, scalable)
- **Optimisation** : SVGO pour réduire la taille
- **Lazy loading** : Images hors viewport chargées en différé
- **Fallbacks** : Couleur de fond pendant le chargement

---

## 8. Validation & Tests UX

### 8.1 Scénarios de Test (MVP)
1. **Première utilisation** : Import CV → Conversation → Première recherche
2. **Utilisation experte** : Dashboard → Recherche ciblée → Génération rapide
3. **Gestion erreurs** : API offline → Recovery → Continuité
4. **Session longue** : Multiples candidatures → Organisation → Suivi

### 8.2 Métriques UX à Suivre
- **Taux d'abandon** : À quelles étapes les utilisateurs quittent-ils ?
- **Temps par étape** : Où passent-ils le plus de temps ?
- **Utilisation features** : Quelles fonctionnalités sont les plus utilisées ?
- **Satisfaction** : Feedback via prompts contextuels "Cette fonctionnalité vous aide-t-elle ?"

### 8.3 Points d'Attention Spéciaux
- **Stress utilisateur** : Surveiller les signes de frustration (clics rapides, annulations)
- **Confidentialité** : Toujours rappeler que les données sont locales
- **Accessibilité cognitive** : Instructions claires, pas de jargon technique

---

## 9. Prochaines Évolutions Design (Post-MVP)

### 9.1 Phase 2
1. **Mode sombre complet** avec palette adaptée
2. **Personnalisation avancée** : Thèmes couleurs, avatars agents
3. **Animations avancées** : Lottie pour les micro-interactions complexes
4. **Voice UI** : Interaction vocale pour la préparation entretien

### 9.2 Phase 3
1. **Version mobile responsive** : Adaptation du design system
2. **Design système complet** : Composants documentés, tokens
3. **Internationalisation** : Support RTL, adaptations culturelles
4. **Accessibilité avancée** : Screen readers, navigation alternative

---

## 10. Notes pour l'Implémentation

### 10.1 Priorités MVP
1. **Timeline de progression** : Indispensable pour le sentiment d'avancement
2. **Système de feedback empathique** : Différencie le produit
3. **Micro-interactions basiques** : Même simples, elles font la différence
4. **États vides bien conçus** : Première impression cruciale

### 10.2 Livrables Attendu de l'Équipe Design
- **Figma** : Library de composants + prototypes interactifs
- **Design tokens** : JSON exportable pour les développeurs
- **Guidelines d'animation** : After Effects/Lottie pour les interactions complexes
- **Documentation** : Comment utiliser le design system

### 10.3 Collaboration Dev/Design
- **Revue hebdomadaire** : Alignement sur l'implémentation
- **Design QA** : Vérification des détails d'implémentation
- **Feedback continu** : Améliorations basées sur les tests utilisateurs

---

**Document approuvé le 27 janvier 2026**  
*Ce document sert de référence unique pour l'équipe design et les développeurs frontend. Toute modification doit être documentée et communiquée à toutes les parties.*