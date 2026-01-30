/**
 * Tests utilisateur réels pour les personas du PRD
 * Module 12: Tests Utilisateur Réels
 *
 * Scénarios testés:
 * 1. Julien (reconversion) : CV commercial → offres tech
 * 2. Sophie (cadre senior) : CV long → mise en valeur expérience
 * 3. Léa (jeune diplômée) : CV léger → construction profil
 */


// Métriques collectées pendant les tests
const collectedMetrics: TestMetrics[] = [];

/**
 * Utilitaires de test
 */
class PersonaTestUtils {
  private page: Page;
  private personaId: string;
  private startTime: number;
  private metrics: Partial<TestMetrics> = {
    stepsCompleted: [],
    errorsEncountered: [],
    matchesFound: 0,
    averageMatchScore: 0,
    letterGenerated: false,
    success: false
  };

  constructor(page: Page, personaId: string) {
    this.page = page;
    this.personaId = personaId;
    this.startTime = Date.now();
    this.metrics.personaId = personaId;
  }

  async logStep(stepName: string) {
    this.metrics.stepsCompleted!.push(stepName);
    console.log(`[${this.personaId}] Étape complétée: ${stepName}`);
  }

  async logError(error: string) {
    this.metrics.errorsEncountered!.push(error);
    console.error(`[${this.personaId}] Erreur: ${error}`);
  }

  async completeTest(success: boolean) {
    const endTime = Date.now();
    this.metrics.endTime = endTime;
    this.metrics.startTime = this.startTime;
    this.metrics.totalTime = (endTime - this.startTime) / 1000; // en secondes
    this.metrics.success = success;

    collectedMetrics.push(this.metrics as TestMetrics);

    // Générer un rapport pour ce test
    await this.generateReport();
  }

  async generateReport() {
    const report = {
      persona: this.personaId,
      duration: `${this.metrics.totalTime}s`,
      steps: this.metrics.stepsCompleted!.length,
      matches: this.metrics.matchesFound,
      averageScore: this.metrics.averageMatchScore?.toFixed(2),
      letterGenerated: this.metrics.letterGenerated,
      errors: this.metrics.errorsEncountered!.length,
      success: this.metrics.success
    };

    console.log(`\n=== RAPPORT TEST ${this.personaId.toUpperCase()} ===`);
    console.table([report]);
    console.log(`Étapes complétées: ${this.metrics.stepsCompleted!.join(', ')}`);
    if (this.metrics.errorsEncountered!.length > 0) {
      console.log(`Erreurs: ${this.metrics.errorsEncountered!.join('; ')}`);
    }
    console.log('================================\n');
  }

  getMetrics(): Partial<TestMetrics> {
    return this.metrics;
  }
}

/**
 * Tests pour chaque persona
 */

test.describe('Tests Utilisateur Réels - Personas PRD', () => {
  // Configuration commune
  test.beforeEach(async ({ page }) => {
    await page.goto(testConfig.baseURL);
    await page.waitForLoadState('networkidle');
  });

  // Test pour Julien (reconversion)
  test('Julien - Reconversion commercial → tech', async ({ page }) => {
    const persona = personas.julien;
    const utils = new PersonaTestUtils(page, persona.id);

    try {
      // 1. Import du CV
      await test.step('Import CV', async () => {
        const fileInput = page.locator('input[type="file"]').first();
        await fileInput.setInputFiles({
          name: persona.cvFile,
          mimeType: 'text/plain',
          buffer: Buffer.from(mockCVs.julien)
        });

        await expect(page.locator('[data-testid="cv-preview"]')).toBeVisible({ timeout: 10000 });
        await utils.logStep('CV importé');
      });

      // 2. Anonymisation
      await test.step('Anonymisation', async () => {
        await page.click('[data-testid="anonymize-btn"]');
        await expect(page.locator('[data-testid="anonymization-success"]')).toBeVisible({ timeout: 5000 });
        await utils.logStep('CV anonymisé');
      });

      // 3. Conversation initiale avec l'agent
      await test.step('Conversation avec agent coach', async () => {
        const chatInput = page.locator('[data-testid="chat-input"]');
        await chatInput.fill(`Je suis ${persona.name}, ${persona.description}. Je cherche un poste de ${persona.profileData.targetRole} à ${persona.profileData.targetLocation}.`);
        await page.click('[data-testid="send-btn"]');

        // Attendre la réponse de l'agent
        await expect(page.locator('[data-testid="agent-message"]')).toHaveCount(1, { timeout: 15000 });
        await utils.logStep('Conversation initiée');
      });

      // 4. Recherche d'offres
      await test.step('Recherche offres', async () => {
        await page.click('[data-testid="search-offers-btn"]');
        await expect(page.locator('[data-testid="offer-card"]')).toBeVisible({ timeout: 15000 });

        // Vérifier qu'on a des résultats
        const offerCards = page.locator('[data-testid="offer-card"]');
        const count = await offerCards.count();
        expect(count).toBeGreaterThan(0);

        utils.metrics.matchesFound = count;
        await utils.logStep(`Recherche complétée: ${count} offres trouvées`);
      });

      // 5. Vérification qualité matching
      await test.step('Vérification matching', async () => {
        const matchScores: number[] = [];
        const offerCards = page.locator('[data-testid="offer-card"]');
        const count = await offerCards.count();

        for (let i = 0; i < Math.min(count, 3); i++) {
          const card = offerCards.nth(i);
          const scoreText = await card.locator('[data-testid="match-score"]').textContent();
          if (scoreText) {
            const score = parseFloat(scoreText.replace('%', '')) / 100;
            matchScores.push(score);
          }
        }

        if (matchScores.length > 0) {
          const averageScore = matchScores.reduce((a, b) => a + b, 0) / matchScores.length;
          utils.metrics.averageMatchScore = averageScore;

          // Vérifier le score minimum
          expect(averageScore).toBeGreaterThanOrEqual(persona.metrics.expectedMatchRate);
          await utils.logStep(`Score matching moyen: ${(averageScore * 100).toFixed(1)}%`);
        }
      });

      // 6. Sélection d'une offre et génération lettre
      await test.step('Génération lettre de motivation', async () => {
        // Sélectionner la première offre
        await page.click('[data-testid="offer-card"]:first-child [data-testid="select-offer-btn"]');

        // Attendre l'écran de génération
        await expect(page.locator('[data-testid="letter-generation-screen"]')).toBeVisible({ timeout: 10000 });

        // Personnaliser la lettre selon le persona
        const toneSlider = page.locator('[data-testid="tone-slider"]');
        await toneSlider.fill('75'); // Enthousiaste pour Julien

        // Générer la lettre
        await page.click('[data-testid="generate-letter-btn"]');

        // Attendre la génération
        await expect(page.locator('[data-testid="letter-preview"]')).toBeVisible({ timeout: 20000 });

        utils.metrics.letterGenerated = true;
        await utils.logStep('Lettre générée avec succès');
      });

      // 7. Vérification dashboard
      await test.step('Vérification dashboard', async () => {
        await page.click('[data-testid="dashboard-tab"]');
        await expect(page.locator('[data-testid="application-card"]')).toBeVisible({ timeout: 5000 });
        await utils.logStep('Candidature ajoutée au dashboard');
      });

      // Test réussi
      await utils.completeTest(true);

    } catch (error) {
      await utils.logError(`Test échoué: ${error instanceof Error ? error.message : String(error)}`);
      await utils.completeTest(false);
      throw error;
    }
  });

  // Test pour Sophie (cadre senior)
  test('Sophie - Cadre senior avec expérience longue', async ({ page }) => {
    const persona = personas.sophie;
    const utils = new PersonaTestUtils(page, persona.id);

    try {
      // 1. Import du CV
      await test.step('Import CV', async () => {
        const fileInput = page.locator('input[type="file"]').first();
        await fileInput.setInputFiles({
          name: persona.cvFile,
          mimeType: 'text/plain',
          buffer: Buffer.from(mockCVs.sophie)
        });

        await expect(page.locator('[data-testid="cv-preview"]')).toBeVisible({ timeout: 10000 });
        await utils.logStep('CV importé (long)');
      });

      // 2. Anonymisation
      await test.step('Anonymisation', async () => {
        await page.click('[data-testid="anonymize-btn"]');
        await expect(page.locator('[data-testid="anonymization-success"]')).toBeVisible({ timeout: 5000 });
        await utils.logStep('CV anonymisé');
      });

      // 3. Conversation adaptée au profil senior
      await test.step('Conversation pour profil senior', async () => {
        const chatInput = page.locator('[data-testid="chat-input"]');
        await chatInput.fill(`Je suis ${persona.name}, ${persona.description}. Avec ${persona.profileData.experienceYears} ans d'expérience, je recherche un poste de ${persona.profileData.targetRole} à ${persona.profileData.targetLocation}.`);
        await page.click('[data-testid="send-btn"]');

        await expect(page.locator('[data-testid="agent-message"]')).toHaveCount(1, { timeout: 15000 });

        // Vérifier que l'agent reconnaît l'expérience
        const agentMessage = await page.locator('[data-testid="agent-message"]:last-child').textContent();
        expect(agentMessage?.toLowerCase()).toContain('expérience');
        expect(agentMessage?.toLowerCase()).toContain('senior');

        await utils.logStep('Conversation adaptée au profil senior');
      });

      // 4. Recherche d'offres senior
      await test.step('Recherche offres senior', async () => {
        await page.click('[data-testid="search-offers-btn"]');
        await expect(page.locator('[data-testid="offer-card"]')).toBeVisible({ timeout: 15000 });

        // Vérifier la pertinence des offres
        const offerCards = page.locator('[data-testid="offer-card"]');
        const count = await offerCards.count();

        // Vérifier qu'on a des offres pertinentes pour un senior
        let seniorOffersCount = 0;
        for (let i = 0; i < Math.min(count, 5); i++) {
          const card = offerCards.nth(i);
          const title = await card.locator('[data-testid="offer-title"]').textContent();
          if (title?.toLowerCase().includes('senior') || title?.toLowerCase().includes('directeur') || title?.toLowerCase().includes('manager')) {
            seniorOffersCount++;
          }
        }

        expect(seniorOffersCount).toBeGreaterThan(0);
        utils.metrics.matchesFound = count;
        await utils.logStep(`Recherche senior: ${count} offres, ${seniorOffersCount} offres senior`);
      });

      // 5. Vérification matching qualité élevée
      await test.step('Vérification matching haute qualité', async () => {
        const offerCards = page.locator('[data-testid="offer-card"]');
        const count = await offerCards.count();

        let totalScore = 0;
        let scoredCards = 0;

        for (let i = 0; i < Math.min(count, 3); i++) {
          const card = offerCards.nth(i);
          const scoreText = await card.locator('[data-testid="match-score"]').textContent();
          if (scoreText) {
            const score = parseFloat(scoreText.replace('%', '')) / 100;
            totalScore += score;
            scoredCards++;

            // Pour Sophie, on attend des scores élevés
            expect(score).toBeGreaterThanOrEqual(0.7);
          }
        }

        if (scoredCards > 0) {
          const averageScore = totalScore / scoredCards;
          utils.metrics.averageMatchScore = averageScore;
          expect(averageScore).toBeGreaterThanOrEqual(persona.metrics.expectedMatchRate);
          await utils.logStep(`Score matching senior moyen: ${(averageScore * 100).toFixed(1)}%`);
        }
      });

      // 6. Génération lettre professionnelle
      await test.step('Génération lettre professionnelle', async () => {
        // Sélectionner une offre senior
        const seniorOffer = page.locator('[data-testid="offer-card"]').filter({ hasText: /senior|directeur|manager/i }).first();
        await expect(seniorOffer).toBeVisible();
        await seniorOffer.click();

        await page.click('[data-testid="select-offer-btn"]');
        await expect(page.locator('[data-testid="letter-generation-screen"]')).toBeVisible({ timeout: 10000 });

        // Ton professionnel pour Sophie
        const toneSlider = page.locator('[data-testid="tone-slider"]');
        await toneSlider.fill('50'); // Professionnel

        // Mettre en avant l'expérience
        const experienceCheckboxes = page.locator('[data-testid="experience-checkbox"]');
        const count = await experienceCheckboxes.count();
        if (count > 0) {
          await experienceCheckboxes.first().check();
        }

        await page.click('[data-testid="generate-letter-btn"]');
        await expect(page.locator('[data-testid="letter-preview"]')).toBeVisible({ timeout: 20000 });

        // Vérifier que la lettre mentionne l'expérience
        const letterContent = await page.locator('[data-testid="letter-content"]').textContent();
        expect(letterContent?.toLowerCase()).toContain('expérience');
        expect(letterContent?.toLowerCase()).toContain('années');

        utils.metrics.letterGenerated = true;
        await utils.logStep('Lettre professionnelle générée');
      });

      await utils.completeTest(true);

    } catch (error) {
      await utils.logError(`Test échoué: ${error instanceof Error ? error.message : String(error)}`);
      await utils.completeTest(false);
      throw error;
    }
  });

  // Test pour Léa (jeune diplômée)
  test('Léa - Jeune diplômée avec peu d\'expérience', async ({ page }) => {
    const persona = personas.lea;
    const utils = new PersonaTestUtils(page, persona.id);

    try {
      // 1. Import du CV léger
      await test.step('Import CV jeune diplômée', async () => {
        const fileInput = page.locator('input[type="file"]').first();
        await fileInput.setInputFiles({
          name: persona.cvFile,
          mimeType: 'text/plain',
          buffer: Buffer.from(mockCVs.lea)
        });

        await expect(page.locator('[data-testid="cv-preview"]')).toBeVisible({ timeout: 10000 });
        await utils.logStep('CV jeune diplômée importé');
      });

      // 2. Anonymisation
      await test.step('Anonymisation', async () => {
        await page.click('[data-testid="anonymize-btn"]');
        await expect(page.locator('[data-testid="anonymization-success"]')).toBeVisible({ timeout: 5000 });
        await utils.logStep('CV anonymisé');
      });

      // 3. Conversation encourageante pour jeune diplômée
      await test.step('Conversation encourageante', async () => {
        const chatInput = page.locator('[data-testid="chat-input"]');
        await chatInput.fill(`Je suis ${persona.name}, ${persona.description}. Je viens de terminer mes études et je cherche mon premier emploi comme ${persona.profileData.targetRole} à ${persona.profileData.targetLocation}.`);
        await page.click('[data-testid="send-btn"]');

        await expect(page.locator('[data-testid="agent-message"]')).toHaveCount(1, { timeout: 15000 });

        // Vérifier que l'agent est encourageant
        const agentMessage = await page.locator('[data-testid="agent-message"]:last-child').textContent();
        expect(agentMessage?.toLowerCase()).toContain('diplômé');
        expect(agentMessage?.toLowerCase()).toContain('premier');
        expect(agentMessage?.toLowerCase()).toMatch(/bravo|félicitation|encourage/i);

        await utils.logStep('Conversation encourageante initiée');
      });

      // 4. Recherche d'offres junior
      await test.step('Recherche offres junior', async () => {
        await page.click('[data-testid="search-offers-btn"]');
        await expect(page.locator('[data-testid="offer-card"]')).toBeVisible({ timeout: 15000 });

        const offerCards = page.locator('[data-testid="offer-card"]');
        const count = await offerCards.count();

        // Vérifier qu'on a des offres adaptées aux juniors
        let juniorOffersCount = 0;
        for (let i = 0; i < Math.min(count, 5); i++) {
          const card = offerCards.nth(i);
          const title = await card.locator('[data-testid="offer-title"]').textContent();
          const description = await card.locator('[data-testid="offer-description"]').textContent();
          const text = (title + ' ' + description).toLowerCase();

          if (text.includes('junior') || text.includes('débutant') || text.includes('formation') || text.includes('diplômé')) {
            juniorOffersCount++;
          }
        }

        expect(juniorOffersCount).toBeGreaterThan(0);
        utils.metrics.matchesFound = count;
        await utils.logStep(`Recherche junior: ${count} offres, ${juniorOffersCount} offres junior`);
      });

      // 5. Vérification matching adapté
      await test.step('Vérification matching junior', async () => {
        const offerCards = page.locator('[data-testid="offer-card"]');
        const count = await offerCards.count();

        let totalScore = 0;
        let scoredCards = 0;

        for (let i = 0; i < Math.min(count, 3); i++) {
          const card = offerCards.nth(i);
          const scoreText = await card.locator('[data-testid="match-score"]').textContent();
          if (scoreText) {
            const score = parseFloat(scoreText.replace('%', '')) / 100;
            totalScore += score;
            scoredCards++;
          }
        }

        if (scoredCards > 0) {
          const averageScore = totalScore / scoredCards;
          utils.metrics.averageMatchScore = averageScore;
          expect(averageScore).toBeGreaterThanOrEqual(persona.metrics.expectedMatchRate);
          await utils.logStep(`Score matching junior moyen: ${(averageScore * 100).toFixed(1)}%`);
        }
      });

      // 6. Génération lettre enthousiaste
      await test.step('Génération lettre enthousiaste', async () => {
        // Sélectionner une offre junior
        const juniorOffer = page.locator('[data-testid="offer-card"]').filter({ hasText: /junior|débutant|diplômé/i }).first();
        await expect(juniorOffer).toBeVisible();
        await juniorOffer.click();

        await page.click('[data-testid="select-offer-btn"]');
        await expect(page.locator('[data-testid="letter-generation-screen"]')).toBeVisible({ timeout: 10000 });

        // Ton enthousiaste pour Léa
        const toneSlider = page.locator('[data-testid="tone-slider"]');
        await toneSlider.fill('80'); // Enthousiaste

        // Mettre en avant les compétences et la formation
        const skillCheckboxes = page.locator('[data-testid="skill-checkbox"]');
        const count = await skillCheckboxes.count();
        if (count > 0) {
          for (let i = 0; i < Math.min(count, 3); i++) {
            await skillCheckboxes.nth(i).check();
          }
        }

        await page.click('[data-testid="generate-letter-btn"]');
        await expect(page.locator('[data-testid="letter-preview"]')).toBeVisible({ timeout: 20000 });

        // Vérifier que la lettre est motivée
        const letterContent = await page.locator('[data-testid="letter-content"]').textContent();
        expect(letterContent?.toLowerCase()).toContain('motivé');
        expect(letterContent?.toLowerCase()).toContain('diplôme');
        expect(letterContent?.toLowerCase()).toContain('apprendre');

        utils.metrics.letterGenerated = true;
        await utils.logStep('Lettre enthousiaste générée');
      });

      // 7. Vérification dashboard avec première candidature
      await test.step('Première candidature dashboard', async () => {
        await page.click('[data-testid="dashboard-tab"]');
        await expect(page.locator('[data-testid="application-card"]')).toBeVisible({ timeout: 5000 });

        // Message spécial pour première candidature
        const welcomeMessage = page.locator('[data-testid="first-application-message"]');
        if (await welcomeMessage.isVisible()) {
          await utils.logStep('Message de bienvenue première candidature affiché');
        }

        await utils.logStep('Première candidature ajoutée au dashboard');
      });

      await utils.completeTest(true);

    } catch (error) {
      await utils.logError(`Test échoué: ${error instanceof Error ? error.message : String(error)}`);
      await utils.completeTest(false);
      throw error;
    }
  });

  // Rapport final après tous les tests
  test.afterAll(async () => {
    console.log('\n=== RAPPORT FINAL TESTS PERSONAS ===');
    console.log(`Total tests exécutés: ${collectedMetrics.length}`);

    const successfulTests = collectedMetrics.filter(m => m.success);
    const failedTests = collectedMetrics.filter(m => !m.success);

    console.log(`Tests réussis: ${successfulTests.length}`);
    console.log(`Tests échoués: ${failedTests.length}`);

    if (successfulTests.length > 0) {
      console.log('\nMétriques moyennes des tests réussis:');
      const avgTime = successfulTests.reduce((sum, m) => sum + m.totalTime, 0) / successfulTests.length;
      const avgMatches = successfulTests.reduce((sum, m) => sum + m.matchesFound, 0) / successfulTests.length;
      const avgScore = successfulTests.reduce((sum, m) => sum + m.averageMatchScore, 0) / successfulTests.length;

      console.log(`- Temps moyen par session: ${avgTime.toFixed(1)}s`);
      console.log(`- Offres trouvées en moyenne: ${avgMatches.toFixed(1)}`);
      console.log(`- Score matching moyen: ${(avgScore * 100).toFixed(1)}%`);
      console.log(`- Lettres générées: ${successfulTests.filter(m => m.letterGenerated).length}/${successfulTests.length}`);
    }

    if (failedTests.length > 0) {
      console.log('\nTests échoués:');
      failedTests.forEach(metrics => {
        console.log(`- ${metrics.personaId}: ${metrics.errorsEncountered.join('; ')}`);
      });
    }

    // Générer un rapport Markdown
    await generateMarkdownReport(collectedMetrics);
  });
});

/**
 * Génère un rapport Markdown des tests
 */
async function generateMarkdownReport(metrics: TestMetrics[]) {
  const reportPath = './test-reports/persona-tests-report.md';
  const fs = require('fs');
  const path = require('path');

  // Créer le dossier si nécessaire
  const dir = path.dirname(reportPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const successfulTests = metrics.filter(m => m.success);
  const failedTests = metrics.filter(m => !m.success);

  const report = `# Rapport des Tests Utilisateur Réels - Personas PRD

**Date**: ${new Date().toISOString().split('T')[0]}
**Environnement**: ${process.env.CI ? 'CI/CD' : 'Local'}

## Résumé

- **Total tests exécutés**: ${metrics.length}
- **Tests réussis**: ${successfulTests.length} (${((successfulTests.length / metrics.length) * 100).toFixed(1)}%)
- **Tests échoués**: ${failedTests.length} (${((failedTests.length / metrics.length) * 100).toFixed(1)}%)

## Détails par Persona

${metrics.map(m => `
### ${m.personaId.toUpperCase()}

- **Statut**: ${m.success ? '✅ SUCCÈS' : '❌ ÉCHEC'}
- **Durée**: ${m.totalTime.toFixed(1)} secondes
- **Étapes complétées**: ${m.stepsCompleted.length}
- **Offres trouvées**: ${m.matchesFound}
- **Score matching moyen**: ${(m.averageMatchScore * 100).toFixed(1)}%
- **Lettre générée**: ${m.letterGenerated ? '✅ Oui' : '❌ Non'}

**Étapes**:
${m.stepsCompleted.map(step => `  - ${step}`).join('\n')}

${m.errorsEncountered.length > 0 ? `
**Erreurs**:
${m.errorsEncountered.map(error => `  - ${error}`).join('\n')}
` : ''}
`).join('\n')}

## Métriques Globales

### Performance
- **Temps moyen par session**: ${successfulTests.length > 0 ? (successfulTests.reduce((sum, m) => sum + m.totalTime, 0) / successfulTests.length).toFixed(1) : 'N/A'} secondes
- **Temps cible**: < 1500 secondes (25 minutes)
- **Respect délai**: ${successfulTests.length > 0 && (successfulTests.reduce((sum, m) => sum + m.totalTime, 0) / successfulTests.length) < 1500 ? '✅' : '⚠️'}

### Qualité Matching
- **Score matching moyen**: ${successfulTests.length > 0 ? ((successfulTests.reduce((sum, m) => sum + m.averageMatchScore, 0) / successfulTests.length) * 100).toFixed(1) : 'N/A'}%
- **Cible**: > 70%
- **Atteinte cible**: ${successfulTests.length > 0 && (successfulTests.reduce((sum, m) => sum + m.averageMatchScore, 0) / successfulTests.length) > 0.7 ? '✅' : '⚠️'}

### Complétude Fonctionnelle
- **Lettres générées**: ${successfulTests.filter(m => m.letterGenerated).length}/${successfulTests.length} (${successfulTests.length > 0 ? ((successfulTests.filter(m => m.letterGenerated).length / successfulTests.length) * 100).toFixed(1) : '0'}%)
- **Cible**: 100%
- **Atteinte cible**: ${successfulTests.length > 0 && successfulTests.filter(m => m.letterGenerated).length === successfulTests.length ? '✅' : '⚠️'}

## Recommandations

${failedTests.length > 0 ? `
### Correctifs nécessaires
${failedTests.map(m => `1. **${m.personaId}**: ${m.errorsEncountered[0]}`).join('\n')}
` : '✅ Aucun correctif immédiat nécessaire.'}

### Améliorations suggérées
1. **Optimisation performance**: ${successfulTests.length > 0 && (successfulTests.reduce((sum, m) => sum + m.totalTime, 0) / successfulTests.length) > 1200 ? 'Les sessions dépassent 20 minutes en moyenne. Optimiser les temps de réponse des agents IA.' : 'Les performances sont dans les cibles.'}
2. **Amélioration matching**: ${successfulTests.length > 0 && (successfulTests.reduce((sum, m) => sum + m.averageMatchScore, 0) / successfulTests.length) < 0.75 ? 'Le score matching moyen est inférieur à 75%. Revoir les embeddings et le RAG.' : 'La qualité du matching est satisfaisante.'}
3. **Robustesse**: ${failedTests.length > 0 ? 'Améliorer la gestion des erreurs pour les cas limites.' : 'La robustesse est bonne.'}

## Validation des Personas

### Julien (Reconversion)
- **Validé**: ${metrics.find(m => m.personaId === 'julien')?.success ? '✅' : '❌'}
- **Points forts**: ${metrics.find(m => m.personaId === 'julien')?.stepsCompleted.filter(s => s.includes('junior') || s.includes('reconversion')).length ? 'Reconnaissance des profils en reconversion' : 'À améliorer'}
- **Améliorations**: ${metrics.find(m => m.personaId === 'julien')?.averageMatchScore && metrics.find(m => m.personaId === 'julien')!.averageMatchScore < 0.7 ? 'Améliorer le matching pour les reconversions' : 'Satisfaisant'}

### Sophie (Cadre Senior)
- **Validé**: ${metrics.find(m => m.personaId === 'sophie')?.success ? '✅' : '❌'}
- **Points forts**: ${metrics.find(m => m.personaId === 'sophie')?.stepsCompleted.filter(s => s.includes('senior') || s.includes('expérience')).length ? 'Reconnaissance de l\'expérience senior' : 'À améliorer'}
- **Améliorations**: ${metrics.find(m => m.personaId === 'sophie')?.averageMatchScore && metrics.find(m => m.personaId === 'sophie')!.averageMatchScore < 0.8 ? 'Améliorer le matching pour les profils senior' : 'Satisfaisant'}

### Léa (Jeune Diplômée)
- **Validé**: ${metrics.find(m => m.personaId === 'lea')?.success ? '✅' : '❌'}
- **Points forts**: ${metrics.find(m => m.personaId === 'lea')?.stepsCompleted.filter(s => s.includes('junior') || s.includes('diplômé')).length ? 'Accompagnement des jeunes diplômés' : 'À améliorer'}
- **Améliorations**: ${metrics.find(m => m.personaId === 'lea')?.averageMatchScore && metrics.find(m => m.personaId === 'lea')!.averageMatchScore < 0.75 ? 'Améliorer le matching pour les débutants' : 'Satisfaisant'}

---

*Rapport généré automatiquement par les tests Playwright*
`;

  fs.writeFileSync(reportPath, report);
  console.log(`Rapport généré: ${reportPath}`);
}
