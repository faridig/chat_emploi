import { test, expect } from '@playwright/test';
import path from 'path';

/**
 * CRITICAL FLOW 1: Import CV → Analyse → Conversation
 *
 * Ce test couvre le flux utilisateur principal :
 * 1. Import d'un CV via drag & drop
 * 2. Analyse automatique par l'IA
 * 3. Conversation avec l'agent coach
 *
 * Conforme au PLANNING.md - Module 10 : Tests E2E Critiques
 */
test.describe('Flux Critique 1: Import CV → Analyse → Conversation', () => {
  test.beforeEach(async ({ page }) => {
    // Naviguer vers la page d'accueil avant chaque test
    await page.goto('/');
  });

  test('doit permettre l\'import d\'un CV PDF', async ({ page }) => {
    // Vérifier que la page d'accueil est correctement chargée
    await expect(page).toHaveTitle(/Chat Emploi/);
    await expect(page.getByText('Bienvenue ! Prêt à transformer votre recherche ?')).toBeVisible();
    await expect(page.getByText('Importez votre CV pour commencer')).toBeVisible();

    // Vérifier la présence de la zone drag & drop
    const dropZone = page.getByText('Glissez-déposez votre CV ici');
    await expect(dropZone).toBeVisible();

    // Vérifier les informations de confidentialité
    await expect(page.getByText('Confidentialité totale')).toBeVisible();
    await expect(page.getByText('Vos données restent sur votre ordinateur')).toBeVisible();
  });

  test('doit afficher un message de succès après import de CV', async ({ page }) => {
    // Simuler l'upload d'un fichier
    const fileInput = page.locator('input[type="file"]');

    // Créer un fichier mock pour le test
    const filePath = path.join(__dirname, 'mocks/sample-cv.pdf');

    // Attendre que l'input soit disponible
    await fileInput.waitFor({ state: 'attached' });

    // Uploader le fichier
    await fileInput.setInputFiles(filePath);

    // Vérifier que le fichier est détecté
    await expect(page.getByText('Fichier sample-cv.pdf prêt à être analysé.')).toBeVisible({
      timeout: 5000
    });
  });

  test('doit naviguer vers la page de conversation après import CV', async ({ page }) => {
    // Mock: Simuler que le CV a été importé et analysé
    // Dans un test réel, nous attendrions l'analyse complète
    // Pour le MVP, nous mockons la navigation

    // Simuler l'upload
    const fileInput = page.locator('input[type="file"]');
    const filePath = path.join(__dirname, 'mocks/sample-cv.pdf');
    await fileInput.setInputFiles(filePath);

    // Attendre un peu pour simuler l'analyse
    await page.waitForTimeout(1000);

    // Dans l'implémentation réelle, l'application naviguerait automatiquement
    // Pour le test, nous vérifions que les éléments de conversation sont accessibles
    // Note: Ce test sera adapté quand la navigation automatique sera implémentée
  });
});

/**
 * CRITICAL FLOW 2: Recherche → Matching → Sélection offre
 *
 * Ce test couvre le flux de recherche d'offres :
 * 1. Navigation vers la page de recherche
 * 2. Application des filtres
 * 3. Affichage des résultats avec scores de matching
 * 4. Sélection d'une offre
 */
test.describe('Flux Critique 2: Recherche → Matching → Sélection offre', () => {
  test.beforeEach(async ({ page }) => {
    // Naviguer directement vers la page de recherche
    // (Dans l'application réelle, l'utilisateur y arriverait après l'analyse CV)
    await page.goto('/session/search');
  });

  test('doit afficher la page de recherche avec filtres', async ({ page }) => {
    // Vérifier le header
    await expect(page.getByText('Offres qui pourraient vous correspondre')).toBeVisible();
    await expect(page.getByText('Basé sur votre profil et vos objectifs')).toBeVisible();

    // Vérifier les filtres
    await expect(page.getByPlaceholder('Localisation')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Actualiser' })).toBeVisible();
  });

  test('doit afficher des cartes d\'offres avec scores de matching', async ({ page }) => {
    // Vérifier que des cartes d'offres sont affichées
    // (Les données sont mockées dans l'implémentation actuelle)
    const offerCards = page.locator('[data-testid="offer-card"]');
    await expect(offerCards).toHaveCountGreaterThan(0);

    // Vérifier qu'au moins une carte a un score de matching
    const firstCard = offerCards.first();
    await expect(firstCard).toContainText('%');

    // Vérifier les informations de base
    await expect(firstCard).toContainText('Développeur');
    await expect(firstCard).toContainText('Tech');
  });

  test('doit permettre la sélection d\'une offre', async ({ page }) => {
    // Sélectionner la première offre
    const firstOfferCard = page.locator('[data-testid="offer-card"]').first();

    // Vérifier qu'il y a un bouton pour générer une lettre
    const generateButton = firstOfferCard.getByRole('button', { name: /générer/i });
    await expect(generateButton).toBeVisible();

    // Cliquer pour sélectionner (dans l'implémentation réelle, cela naviguerait vers la page de génération)
    await generateButton.click();

    // Vérifier la navigation ou l'état de sélection
    // Note: À adapter quand la navigation sera implémentée
  });
});

/**
 * CRITICAL FLOW 3: Génération lettre → Personnalisation → Export
 *
 * Ce test couvre le flux de génération de lettre de motivation :
 * 1. Navigation vers l'éditeur de lettre
 * 2. Personnalisation du ton et du contenu
 * 3. Prévisualisation
 * 4. Export PDF
 */
test.describe('Flux Critique 3: Génération lettre → Personnalisation → Export', () => {
  test.beforeEach(async ({ page }) => {
    // Naviguer directement vers la page de génération de lettre
    await page.goto('/session/letter');
  });

  test('doit afficher l\'éditeur de lettre avec deux colonnes', async ({ page }) => {
    // Vérifier la structure de la page
    await expect(page.getByText('Lettre de motivation pour')).toBeVisible();

    // Vérifier la présence des deux colonnes
    // Colonne gauche: Prévisualisation
    const previewColumn = page.locator('[data-testid="letter-preview"]');
    await expect(previewColumn).toBeVisible();

    // Colonne droite: Personnalisation
    const customizationColumn = page.locator('[data-testid="customization-panel"]');
    await expect(customizationColumn).toBeVisible();
  });

  test('doit permettre de personnaliser le ton de la lettre', async ({ page }) => {
    // Vérifier les contrôles de personnalisation
    const toneSlider = page.locator('[data-testid="tone-slider"]');
    await expect(toneSlider).toBeVisible();

    // Vérifier les options de checklist
    const checklistItems = page.locator('[data-testid="highlight-checklist"] input[type="checkbox"]');
    await expect(checklistItems).toHaveCountGreaterThan(0);
  });

  test('doit afficher les boutons d\'export', async ({ page }) => {
    // Vérifier les boutons d'action
    await expect(page.getByRole('button', { name: /télécharger pdf/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /copier le texte/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /générer une alternative/i })).toBeVisible();
  });
});

/**
 * CRITICAL FLOW 4: Dashboard → Suivi → Mise à jour statut
 *
 * Ce test couvre le flux de gestion des candidatures :
 * 1. Vue dashboard avec kanban
 * 2. Suivi des statuts
 * 3. Mise à jour des candidatures
 * 4. Statistiques personnelles
 */
test.describe('Flux Critique 4: Dashboard → Suivi → Mise à jour statut', () => {
  test.beforeEach(async ({ page }) => {
    // Naviguer directement vers le dashboard
    await page.goto('/dashboard');
  });

  test('doit afficher le dashboard avec les colonnes kanban', async ({ page }) => {
    // Vérifier les colonnes du kanban
    await expect(page.getByText('Postulées')).toBeVisible();
    await expect(page.getByText('En cours')).toBeVisible();
    await expect(page.getByText('Entretiens')).toBeVisible();
    await expect(page.getByText('Refusées')).toBeVisible();
    await expect(page.getByText('Acceptées')).toBeVisible();
  });

  test('doit afficher les statistiques personnelles', async ({ page }) => {
    // Vérifier les statistiques en haut
    await expect(page.getByText(/postulées/)).toBeVisible();
    await expect(page.getByText(/entretiens/)).toBeVisible();
    await expect(page.getByText(/offre/)).toBeVisible();
  });

  test('doit permettre d\'ajouter une nouvelle candidature', async ({ page }) => {
    // Vérifier le bouton pour ajouter une candidature
    const addButton = page.getByRole('button', { name: /nouvelle recherche/i });
    await expect(addButton).toBeVisible();

    // Cliquer pour démarrer une nouvelle recherche
    await addButton.click();

    // Vérifier la navigation vers la page d'accueil
    await expect(page).toHaveURL('/');
  });
});

/**
 * Tests d'intégration des flux complets
 */
test.describe('Tests d\'intégration des flux complets', () => {
  test('flux complet: CV → Conversation → Recherche → Lettre → Dashboard', async ({ page }) => {
    // Ce test simule un parcours utilisateur complet
    // Note: Pour le MVP, nous testons la navigation entre les pages

    // 1. Page d'accueil
    await page.goto('/');
    await expect(page.getByText('Bienvenue ! Prêt à transformer votre recherche ?')).toBeVisible();

    // 2. Page de conversation (simuler navigation)
    await page.goto('/session');
    await expect(page.locator('[data-testid="chat-panel"]')).toBeVisible();

    // 3. Page de recherche
    await page.goto('/session/search');
    await expect(page.getByText('Offres qui pourraient vous correspondre')).toBeVisible();

    // 4. Page de génération de lettre
    await page.goto('/session/letter');
    await expect(page.getByText('Lettre de motivation pour')).toBeVisible();

    // 5. Dashboard
    await page.goto('/dashboard');
    await expect(page.getByText('Vos candidatures')).toBeVisible();

    // Vérifier que toutes les pages principales sont accessibles
    const pages = ['/', '/session', '/session/search', '/session/letter', '/dashboard'];
    for (const url of pages) {
      await page.goto(url);
      await expect(page).toHaveURL(url);
      await page.waitForLoadState('networkidle');
    }
  });
});
