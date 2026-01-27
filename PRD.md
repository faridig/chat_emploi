# PRD - Chat Emploi
## Product Requirements Document
### Version 1.0 - MVP
**Date** : 27 janvier 2026  
**Product Manager** : Farid  
**Statut** : En rédaction  

---

## 1. Résumé & Vision

### 1.1 Énoncé de Vision
"Transformer la recherche d'emploi, processus solitaire et décourageant, en une expérience conversationnelle intelligente et empathique, où chaque demandeur d'emploi bénéficie d'un agent de carrière personnel, disponible 24h/24."

### 1.2 Problème à Résoudre
Les candidats (juniors, seniors, personnes en reconversion) font face à :
- **Algorithmes froids** proposant des offres inadaptées
- **Processus solitaire** sans accompagnement personnalisé
- **Difficulté à adapter** son CV à chaque annonce
- **Manque de feedback** constructif sur leurs candidatures
- **Stress** avant les entretiens par manque de préparation ciblée

### 1.3 Solution Proposée
Une application de bureau intelligente basée sur une **architecture multi-agents** (LangGraph, CrewAI) qui :
1. **Comprend le profil** du candidat via une conversation naturelle
2. **Recherche activement** les offres pertinentes (API France Travail + recherche web)
3. **Accompagne** l'utilisateur dans l'adaptation de son CV et la rédaction de lettres motivées
4. **Prépare aux entretiens** via des simulations et des briefings personnalisés
5. **Suivi** l'ensemble du processus de candidature

### 1.4 Valeurs Clés
- **Empathie** : L'IA comprend et encourage, ne fait pas que traiter des données
- **Pertinence** : Matching qualitatif via RAG et analyse sémantique avancée
- **Confidentialité** : Données stockées localement, anonymisation définitive
- **Accessibilité** : Interface conversationnelle intuitive, pas de compétence technique requise

---

## 2. Objectifs & KPIs

### 2.1 Objectifs Business (Phase Expérimentale)
- **Valider l'hypothèse produit** : Les candidats préfèrent-ils une interface conversationnelle aux plateformes traditionnelles ?
- **Mesurer l'efficacité** du matching IA vs matching humain
- **Collecter des données** anonymisées pour améliorer les algorithmes
- **Préparer une future monétisation** via feedback utilisateurs

### 2.2 KPIs (Key Performance Indicators)
| KPI | Cible MVP | Mesure |
|-----|-----------|---------|
| **Taux de matching pertinent** | ≥ 70% | % d'offres que l'utilisateur juge "pertinentes" (via feedback) |
| **Temps moyen par session** | 15-20 min | Durée d'une session complète (CV → candidature) |
| **Satisfaction utilisateur** | ≥ 4/5 | Score NPS (Net Promoter Score) via feedback post-session |
| **Taux de génération réussie** | ≥ 90% | % de lettres de motivation générées sans erreur |
| **Latence des agents** | < 3s | Temps de réponse moyen des agents IA |
| **Couverture API France Travail** | 100% des offres < 30 jours | % d'offres accessibles via l'API |

### 2.3 Métriques de Monitoring Technique
- **Performance des agents** : Temps d'exécution, taux d'erreur, consommation mémoire
- **Qualité des embeddings** : Similarité cosinus moyenne entre CV et offres matching
- **Feedback loop** : Nombre de feedbacks collectés, tendance d'amélioration
- **Stabilité API** : Taux de succès des appels France Travail et Gemini
- **Utilisation ressources** : CPU, RAM, stockage local

---

## 3. Personas Utilisateurs

### 3.1 Persona Principal : "Julien, 28 ans, en reconversion"
**Démographie** :
- 28 ans, ancien commercial, souhaite devenir développeur web
- Niveau bac+3, en formation continue
- Cherche un premier emploi dans la tech

**Frustrations** :
- "Mon CV commercial ne parle pas aux recruteurs tech"
- "Je ne sais pas quelles compétences mettre en avant"
- "Les offres demandent toujours de l'expérience que je n'ai pas"
- "Je passe des heures à adapter mon CV pour chaque annonce"

**Objectifs avec Chat Emploi** :
- Comprendre comment transposer ses compétences commerciales vers la tech
- Découvrir des offres "junior friendly"
- Obtenir une lettre de motivation qui explique sa reconversion
- Préparer ses entretiens avec des arguments convaincants

### 3.2 Persona Secondaire : "Sophie, 45 ans, cadre senior"
**Démographie** :
- 45 ans, 20 ans d'expérience en gestion de projet
- Recherche un poste de directrice d'équipe
- Maîtrise LinkedIn mais trouve le processus impersonnel

**Frustrations** :
- "Les algorithmes me proposent des postes trop juniors"
- "Mon CV est trop long, je ne sais pas quoi couper"
- "Je veux un accompagnement sur mesure, pas des conseils génériques"
- "Le stress des entretiens à mon niveau est intense"

**Objectifs avec Chat Emploi** :
- Mettre en valeur son expérience sans paraître surqualifiée
- Découvrir des entreprises qui valorisent l'expérience
- Préparer des réponses aux questions difficiles sur l'âge
- Obtenir un briefing approfondi sur les entreprises cibles

### 3.3 Persona Tertiaire : "Léa, 22 ans, jeune diplômée"
**Démographie** :
- 22 ans, master en marketing
- Première recherche d'emploi
- Active sur les réseaux sociaux mais peu sur les plateformes professionnelles

**Frustrations** :
- "Je ne sais pas par où commencer"
- "Mon CV est presque vide"
- "J'ai peur de ne pas être à la hauteur"
- "Les processus de candidature sont compliqués"

**Objectifs avec Chat Emploi** :
- Construire un CV attractif malgré le manque d'expérience
- Découvrir des programmes jeunes diplômés
- Recevoir des encouragements et conseils pratiques
- Simuler des entretiens pour gagner en confiance

---

## 4. Périmètre du Projet (MoSCoW)

### 4.1 MUST HAVE (MVP - Version 1.0)
**Fonctionnalités essentielles sans lesquelles le produit n'a pas de valeur :**

1. **Import & Anonymisation de CV**
   - Support PDF, DOCX, TXT
   - Anonymisation définitive (noms, coordonnées, emails)
   - Interface de vérification avant traitement

2. **Analyse Multimodale du CV**
   - Extraction intelligente via Gemini
   - Identification : compétences, expériences, formations
   - Structuration en JSON normalisé

3. **Recherche d'Offres France Travail**
   - Intégration API France Travail (offres < 30 jours)
   - Filtrage par localisation, métier, contrat
   - Pagination et mise en cache local

4. **Système de Matching RAG**
   - Embeddings des CV et offres (via LlamaIndex)
   - Similarité sémantique (cosinus)
   - Top 5 offres les plus pertinentes

5. **Génération de Lettre de Motivation**
   - Prompt engineering personnalisé
   - Intégration des spécificités offre + profil
   - Format structuré (objet, introduction, corps, conclusion)

6. **Agent Coach Conversationnel**
   - Dialogue empathique (ton encourageant)
   - Réponses contextuelles au profil
   - Suggestions d'amélioration du CV

7. **Interface Conversationnelle Principale**
   - Chat en temps réel
   - Indicateur "agent en train d'écrire"
   - Historique de la session

8. **Stockage Local Sécurisé**
   - Données chiffrées localement
   - Gestion des sessions utilisateur
   - Export des documents générés

9. **Monitoring de Base**
   - Logs d'exécution des agents
   - Tracking des erreurs API
   - Métriques de performance temps réel

### 4.2 SHOULD HAVE (Post-MVP - Haute priorité)

1. **Dashboard de Suivi des Candidatures**
   - Tableau visuel des candidatures (postulées, en cours, refusées)
   - Notes personnelles par entreprise
   - Rappels automatiques de relance

2. **Simulateur d'Entretien IA avec Analyse Émotionnelle**
   - Questions types (techniques, comportementales)
   - Analyse sémantique des réponses (contenu + émotion)
   - Feedback constructif avec suggestions d'amélioration
   - Exercices de respiration si stress détecté

3. **Mode "Préparation Intensive"**
   - Activation pour entretien imminent (< 48h)
   - Extraction approfondie infos entreprise (site web, actualités)
   - Briefing personnalisé avec angles d'attaque
   - Questions pertinentes à poser au recruteur

4. **Système de Feedback pour Amélioration des Agents**
   - Notation des offres (1-5 étoiles)
   - Feedback libre "Pourquoi cette note ?"
   - Collection anonymisée pour fine-tuning
   - Dashboard développeur avec insights

5. **Métriques Avancées de Pertinence**
   - Tracking du taux de matching pertinent
   - Analyse des patterns de succès/échec
   - A/B testing des prompts d'agents

### 4.3 COULD HAVE (Si temps/budget)

1. **Recherche Web Étendue**
   - Intégration d'autres sources d'offres (LinkedIn, Indeed via web scraping)
   - API de recherche web gratuite (SerpAPI gratuit si disponible)

2. **Export Multi-Formats**
   - PDF professionnel (CV + lettre + fiche entreprise)
   - Version anonymisée pour plateformes
   - Résumé audio pour préparation mobile

3. **Intégrations Réseaux Sociaux**
   - Import de profil LinkedIn
   - Suggestions de posts pour réseau professionnel
   - Template de messages de connexion

### 4.4 WON'T HAVE (Version 1.0)

1. **Modèle Économique**
   - Pas de monétisation dans le MVP
   - Pas de limitations artificielles d'usage

2. **Stockage Cloud**
   - Pas de synchronisation cloud
   - Pas de multi-appareils

3. **Collaboration Multi-utilisateurs**
   - Pas de comptes partagés
   - Pas de fonctionnalité "conseiller carrière"

4. **Support Multi-langues**
   - Français uniquement en v1

---

## 5. Fonctionnalités Clés & User Stories

### 5.1 Fonctionnalité 1 : Import & Anonymisation Intelligente du CV

**User Story** :
En tant que demandeur d'emploi, je veux importer mon CV et anonymiser mes données sensibles, pour protéger ma vie privée tout en permettant une analyse précise de mon profil.

**Critères d'Acceptation** :
- [ ] L'utilisateur peut glisser-déposer un fichier PDF, DOCX ou TXT
- [ ] L'application détecte automatiquement les données sensibles (noms, téléphones, emails, adresses)
- [ ] Interface de prévisualisation avec surlignage des données à anonymiser
- [ ] Bouton "Anonymiser définitivement" avec confirmation explicite
- [ ] Le CV anonymisé est stocké localement avec un ID unique
- [ ] L'original n'est conservé nulle part (mémoire tampon vidée)
- [ ] Feedback visuel : "CV anonymisé avec succès, X données protégées"

**Détails Techniques** :
- Librairie : `PyPDF2` pour PDF, `python-docx` pour DOCX
- Regex pour détection des données sensibles
- Interface : React + Drag & Drop API

### 5.2 Fonctionnalité 2 : Conversation avec l'Agent Coach

**User Story** :
En tant que candidat, je veux discuter avec un agent IA qui comprend mon profil et me guide dans ma recherche, pour me sentir accompagné et obtenir des conseils personnalisés.

**Critères d'Acceptation** :
- [ ] Interface chat similaire à WhatsApp/Telegram (bulles, avatar agent)
- [ ] L'agent commence par une introduction empathique : "Bonjour ! Je suis votre coach emploi. Parlez-moi de votre situation..."
- [ ] Compréhension contextuelle : l'agent se réfère aux informations du CV
- [ ] Suggestions proactives : "Votre expérience en [domaine] pourrait intéresser ces entreprises..."
- [ ] Ton adaptatif : encourageant, professionnel mais chaleureux
- [ ] Indicateur "Agent est en train d'écrire..." pendant la génération
- [ ] Historique conservé pendant toute la session
- [ ] Possibilité de rediriger vers d'autres agents : "Je vous passe mon collègue spécialiste des offres"

**Détails Techniques** :
- Framework : LangGraph pour orchestration des agents
- Modèle : Gemini Pro via API
- Prompt engineering avec personnalité "coach empathique"
- Système de contexte : mémorisation des 10 derniers messages

### 5.3 Fonctionnalité 3 : Matching RAG avec France Travail

**User Story** :
En tant que candidat, je veux que l'application trouve automatiquement les offres qui correspondent vraiment à mon profil, pour gagner du temps et découvrir des opportunités pertinentes.

**Critères d'Acceptation** :
- [ ] Appel à l'API France Travail avec filtres (date < 30 jours, région choisie)
- [ ] Embedding des offres et du CV via modèle sémantique
- [ ] Calcul de similarité cosinus pour chaque paire CV-offre
- [ ] Retour des 5 offres les plus pertinentes avec score de matching (0-100%)
- [ ] Pour chaque offre : titre, entreprise, lieu, contrat, résumé
- [ ] Option "Voir plus de détails" avec description complète
- [ ] Option "Cette offre ne me correspond pas" pour feedback
- [ ] Temps total de recherche < 10 secondes

**Détails Techniques** :
- RAG : LlamaIndex pour gestion des embeddings
- Modèle d'embedding : `text-embedding-004` (Gemini) ou alternative open-source
- Indexation vectorielle locale avec FAISS ou Chroma
- Cache des offres (24h) pour éviter les appels API répétés

### 5.4 Fonctionnalité 4 : Génération de Lettre de Motivation

**User Story** :
En tant que candidat, je veux générer une lettre de motivation sur-mesure pour une offre spécifique, pour postuler rapidement avec un document professionnel et persuasif.

**Critères d'Acceptation** :
- [ ] Sélection d'une offre parmi les résultats du matching
- [ ] Génération en < 15 secondes
- [ ] Lettre structurée : objet, formule d'appel, introduction, 2-3 paragraphes de corps, conclusion, formule de politesse
- [ ] Intégration intelligente des éléments du CV pertinents pour l'offre
- [ ] Ton adapté au type d'entreprise (startup vs grand groupe)
- [ ] Options de personnalisation : "ajouter un projet spécifique", "changer le ton"
- [ ] Prévisualisation avec mise en forme correcte
- [ ] Export PDF avec mise en page professionnelle
- [ ] Option "Générer une version alternative" si première version non satisfaisante

**Détails Techniques** :
- Template système avec variables : `{nom_entreprise}`, `{poste}`, `{competences_cles}`
- Prompt contextuel incluant CV et offre complète
- Validation de la longueur (300-500 mots)
- Librairie PDF : ReportLab ou WeasyPrint

### 5.5 Fonctionnalité 5 : Dashboard de Suivi

**User Story** :
En tant que candidat, je veux visualiser l'état de toutes mes candidatures, pour organiser ma recherche et ne pas oublier de relancer les employeurs.

**Critères d'Acceptation** :
- [ ] Vue kanban : Postulées / En cours / Entretiens / Refusées / Acceptées
- [ ] Carte par candidature : entreprise, poste, date de candidature, statut
- [ ] Ajout manuel de candidatures (hors Chat Emploi)
- [ ] Notes privées par entreprise : "Relancer le 15/02", "Contact : M. Dupont"
- [ ] Rappels automatiques : "Vous avez postulé chez X il y a 7 jours, souhaitez-vous relancer ?"
- [ ] Statistiques : nombre de candidatures, taux de réponse, secteur le plus actif
- [ ] Export des données en CSV
- [ ] Synchronisation locale (pas de cloud)

**Détails Techniques** :
- Base de données locale : SQLite avec SQLAlchemy
- Interface : React avec bibliothèque de drag & drop (dnd-kit)
- Notifications système (Electron)
- Chiffrement des notes sensibles

---

## 6. Flux Utilisateur Principal

### 6.1 Flowchart Simplifié
```
[Démarrage] 
    ↓
[Import CV] → Drag & drop → Anonymisation → Validation
    ↓
[Conversation initiale] → Agent Coach pose des questions → Profil enrichi
    ↓
[Recherche offres] → Appel API France Travail → RAG Matching → Top 5 offres
    ↓
[Sélection offre] → Utilisateur choisit 1-3 offres intéressantes
    ↓
[Boucle par offre sélectionnée] 
    ├→ [Génération lettre] → Personnalisation → Export PDF
    ├→ [Préparation entretien] → Briefing entreprise → Questions types
    └→ [Ajout dashboard] → Candidature suivie
    ↓
[Session suivante] → Reprise depuis dashboard ou nouvelle recherche
```

### 6.2 Scénario Type "Julien"

1. **00:00-02:00** : Julien ouvre l'app, importe son CV commercial
2. **02:00-05:00** : L'agent Coach discute avec lui, comprend sa reconversion vers le web
3. **05:00-10:00** : Recherche offres "développeur junior" en région parisienne
4. **10:00-12:00** : Julien sélectionne 2 offres intéressantes
5. **12:00-17:00** : Génération de 2 lettres expliquant sa reconversion
6. **17:00-20:00** : Simulation d'entretien pour l'offre préférée
7. **20:00-25:00** : Ajout au dashboard, planification des relances

**Durée totale** : ~25 minutes pour 2 candidatures complètes

---

## 7. Exigences Non-Fonctionnelles

### 7.1 Performance
- **Temps de réponse agents** : < 3 secondes pour 95% des requêtes
- **Recherche offres** : < 10 secondes (incluant appel API et matching)
- **Génération lettre** : < 15 secondes
- **Interface** : 60 FPS stable, pas de lag lors des interactions
- **Démarrage application** : < 5 secondes

### 7.2 Sécurité & Confidentialité
- **Stockage local** : Données chiffrées avec AES-256
- **Anonymisation** : Irréversible, pas de log des données originales
- **API keys** : Stockées localement chiffrées, jamais en clair dans le code
- **Communication** : HTTPS obligatoire pour tous les appels API
- **Audit trail** : Logs locaux des actions (sans données personnelles)

### 7.3 Compatibilité
- **OS** : Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Navigateur embarqué** : Chromium (Electron) version stable
- **CPU/RAM** : 4 cores, 8GB RAM minimum recommandé
- **Stockage** : 500MB pour l'app + 100MB par utilisateur
- **Connexion** : Internet requis (API Gemini et France Travail)

### 7.4 Maintenabilité & Monitoring
- **Logs structurés** : JSON logs avec niveaux (DEBUG, INFO, ERROR)
- **Métriques temps réel** : Prometheus/Grafana local ou console dédiée
- **Health checks** : Vérification automatique des APIs externes
- **Error tracking** : Capture des erreurs avec stack trace
- **Documentation** : README technique + guide déploiement

### 7.5 Architecture Technique
- **Frontend** : React + TypeScript + Electron
- **Backend local** : Python (FastAPI) pour les agents IA
- **Communication** : WebSocket pour chat temps réel, REST pour autres opérations
- **Base de données** : SQLite local
- **Vector store** : FAISS ou Chroma (embeddings locaux)
- **Orchestration agents** : LangGraph avec CrewAI patterns
- **LLM** : Gemini Pro via API (fallback : modèle local Ollama si configuré)

---

## 8. Prochaines Étapes (Post-MVP)

### 8.1 Phase 2 (1-2 mois après MVP)
1. **A/B testing** des différents prompts d'agents
2. **Fine-tuning** des modèles sur les feedbacks collectés
3. **Expansion sources d'offres** : LinkedIn, Indeed, Welcome to the Jungle
4. **Module avancé de préparation aux tests techniques** (pour les devs)

### 8.2 Phase 3 (3-4 mois)
1. **Version mobile** : Application companion pour préparation entretien
2. **Communauté** : Forum anonyme d'entraide entre candidats
3. **Partner program** : Intégration avec centres de formation, écoles
4. **Analytics avancés** : Dashboard entreprise pour centres d'emploi

### 8.3 Phase 4 (6+ mois)
1. **Monétisation** : Freemium (coaching premium, fonctionnalités avancées)
2. **Version entreprise** : Pour les recruteurs souhaitant améliorer leur matching
3. **Internationalisation** : UK, Germany, Spain (adaptation marchés locaux)
4. **Recherche académique** : Publication sur l'efficacité du matching IA vs humain

---

## 9. Annexes

### 9.1 Glossaire Technique
- **RAG** : Retrieval-Augmented Generation - Technique combinant recherche d'information et génération de texte
- **Embedding** : Représentation vectorielle d'un texte permettant des comparaisons sémantiques
- **LLM** : Large Language Model - Modèle de langage à grande échelle (Gemini, GPT, etc.)
- **LangGraph** : Framework pour construire des applications avec agents IA et state machines
- **CrewAI** : Framework pour orchestrer des équipes d'agents IA collaboratifs
- **LlamaIndex** : Framework pour construire des applications RAG avec indexation vectorielle

### 9.2 Références APIs
- **France Travail API** : Documentation JSON disponible localement
- **Google Gemini API** : https://ai.google.dev/
- **Recherche web** : À déterminer (SerpAPI gratuit tier ou alternative)

### 9.3 Équipe & Contacts
- **Product Owner** : Farid
- **Développeurs** : À recruter/assigner
- **Designer UX/UI** : À recruter/assigner
- **Data Scientist** : À recruter/assigner (pour fine-tuning)

---

## 10. Notes de Version

### v1.0 (MVP)
- Première version fonctionnelle avec les 5 fonctionnalités principales
- Focus sur l'expérience utilisateur fluide
- Architecture de base pour le monitoring et l'amélioration continue

**Date de livraison cible** : 2-3 mois de développement

---
*Document rédigé le 27 janvier 2026 - Pour usage interne uniquement*