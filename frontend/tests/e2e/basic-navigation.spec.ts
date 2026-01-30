import { test, expect } from '@playwright/test';

/**
 * Tests de navigation de base pour vérifier que toutes les pages principales sont accessibles
 * Conforme au PLANNING.md - Module 10 : Tests E2E Critiques
 */

test.describe('Navigation de base', () => {
  test('doit charger la page d\'accueil', async ({ page }) => {
    await page.goto('/');

    // Vérifier les éléments clés de la page d'accueil
    await expect(page).toHaveTitle(/Chat Emploi/);
    await expect(page.getByText('Bienvenue ! Prêt à transformer votre recherche ?')).toBeVisible();
    await expect(page.getByText('Importez votre CV pour commencer')).toBeVisible();
    await expect(page.getByText('Glissez-déposez votre CV ici')).toBeVisible();
  });

  test('doit naviguer vers la page de conversation', async ({ page }) => {
    await page.goto('/session');

    // Vérifier que le panneau de chat est présent
    await expect(page.locator('[data-testid="chat-panel"]')).toBeVisible();
  });

  test('doit naviguer vers la page de recherche d\'offres', async ({ page }) => {
    await page.goto('/session/search');

    // Vérifier le header de la page de recherche
    await expect(page.getByText('Offres qui pourraient vous correspondre')).toBeVisible();
    await expect(page.getByText('Basé sur votre profil et vos objectifs')).toBeVisible();

    // Vérifier qu'il y a des cartes d'offres
    const offerCards = page.locator('[data-testid="offer-card"]');
    await expect(offerCards).toHaveCountGreaterThan(0);
  });

  test('doit naviguer vers la page de génération de lettre', async ({ page }) => {
    await page.goto('/session/letter');

    // Vérifier la structure de la page
    await expect(page.locator('[data-testid="letter-preview"]')).toBeVisible();
    await expect(page.locator('[data-testid="customization-panel"]')).toBeVisible();

    // Vérifier les boutons d'action
    await expect(page.getByRole('button', { name: /télécharger pdf/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /copier le texte/i })).toBeVisible();
  });

  test('doit naviguer vers le dashboard', async ({ page }) => {
    await page.goto('/dashboard');

    // Vérifier le header du dashboard
    await expect(page.getByText('Vos candidatures')).toBeVisible();

    // Vérifier les colonnes du kanban
    await expect(page.getByText('Postulées')).toBeVisible();
    await expect(page.getByText('En cours')).toBeVisible();
    await expect(page.getByText('Entretiens')).toBeVisible();
  });

  test('doit pouvoir naviguer entre toutes les pages principales', async ({ page }) => {
    // Tester la navigation séquentielle
    const pages = [
      { url: '/', title: 'Chat Emploi' },
      { url: '/session', element: '[data-testid="chat-panel"]' },
      { url: '/session/search', text: 'Offres qui pourraient vous correspondre' },
      { url: '/session/letter', element: '[data-testid="letter-preview"]' },
      { url: '/dashboard', text: 'Vos candidatures' },
    ];

    for (const pageInfo of pages) {
      await page.goto(pageInfo.url);
      await page.waitForLoadState('networkidle');

      if ('title' in pageInfo) {
        await expect(page).toHaveTitle(new RegExp(pageInfo.title));
      } else if ('element' in pageInfo) {
        await expect(page.locator(pageInfo.element)).toBeVisible();
      } else if ('text' in pageInfo) {
        await expect(page.getByText(pageInfo.text)).toBeVisible();
      }
    }
  });
});

/**
 * Tests des fonctionnalités de base
 */
test.describe('Fonctionnalités de base', () => {
  test('doit permettre l\'upload d\'un fichier CV', async ({ page }) => {
    await page.goto('/');

    // Vérifier que l'input file est présent
    const fileInput = page.locator('[data-testid="file-input"]');
    await expect(fileInput).toBeAttached();

    // Simuler l'upload d'un fichier (le fichier mock existe dans tests/e2e/mocks/)
    await fileInput.setInputFiles('tests/e2e/mocks/sample-cv.pdf');

    // Vérifier que le fichier est détecté
    // Note: Dans l'implémentation actuelle, un message s'affiche quand un fichier est sélectionné
    await expect(page.getByText(/prêt à être analysé/i)).toBeVisible({
      timeout: 3000
    });
  });

  test('doit afficher des cartes d\'offres avec scores de matching', async ({ page }) => {
    await page.goto('/session/search');

    // Attendre que les cartes soient chargées
    const offerCards = page.locator('[data-testid="offer-card"]');
    await expect(offerCards.first()).toBeVisible({ timeout: 5000 });

    // Vérifier qu'au moins une carte a un score de matching (format XX%)
    const firstCard = offerCards.first();
    const cardText = await firstCard.textContent();
    expect(cardText).toMatch(/\d+%/);

    // Vérifier les informations de base
    expect(cardText).toMatch(/Développeur|Tech|Python|React/i);
  });

  test('doit afficher l\'éditeur de lettre avec contrôles de personnalisation', async ({ page }) => {
    await page.goto('/session/letter');

    // Vérifier la prévisualisation
    const preview = page.locator('[data-testid="letter-preview"]');
    await expect(preview).toBeVisible();

    // Vérifier les contrôles de personnalisation
    const toneSlider = page.locator('[data-testid="tone-slider"]');
    await expect(toneSlider).toBeVisible();

    const checklist = page.locator('[data-testid="highlight-checklist"]');
    await expect(checklist).toBeVisible();

    // Vérifier qu'il y a des cases à cocher
    const checkboxes = checklist.locator('input[type="checkbox"]');
    await expect(checkboxes).toHaveCountGreaterThan(0);
  });
});
