#!/usr/bin/env node

/**
 * Script d'analyse du bundle size pour Chat Emploi
 * Module 11 : Cool Down & Polish
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const PROJECT_ROOT = path.join(__dirname, '..');
const BUILD_DIR = path.join(PROJECT_ROOT, '.next');
const PACKAGE_JSON = path.join(PROJECT_ROOT, 'package.json');

// Couleurs pour la console
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bold: '\x1b[1m'
};

// Helper pour formatter les tailles
function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Analyse des dépendances
function analyzeDependencies() {
  console.log(`${colors.cyan}${colors.bold}=== Analyse des Dépendances ===${colors.reset}\n`);

  try {
    const packageData = JSON.parse(fs.readFileSync(PACKAGE_JSON, 'utf8'));
    const deps = packageData.dependencies || {};
    const devDeps = packageData.devDependencies || {};

    console.log(`${colors.white}Dépendances de production (${Object.keys(deps).length}):${colors.reset}`);
    Object.entries(deps)
      .sort(([a], [b]) => a.localeCompare(b))
      .forEach(([name, version]) => {
        console.log(`  ${colors.green}✓${colors.reset} ${name}@${version}`);
      });

    console.log(`\n${colors.white}Dépendances de développement (${Object.keys(devDeps).length}):${colors.reset}`);
    Object.entries(devDeps)
      .sort(([a], [b]) => a.localeCompare(b))
      .forEach(([name, version]) => {
        console.log(`  ${colors.blue}⚙${colors.reset} ${name}@${version}`);
      });

    // Vérifier les dépendances problématiques
    const problematicDeps = {
      'lodash': 'Utiliser lodash-es ou des imports spécifiques',
      'moment': 'Préférer date-fns ou dayjs (plus léger)',
      'jquery': 'Pas nécessaire avec React',
      'axios': 'Préférer fetch() natif si possible',
    };

    console.log(`\n${colors.yellow}${colors.bold}Vérification des dépendances problématiques:${colors.reset}`);
    let hasProblems = false;

    Object.keys(problematicDeps).forEach(dep => {
      if (deps[dep] || devDeps[dep]) {
        console.log(`${colors.red}⚠${colors.reset} ${dep}: ${problematicDeps[dep]}`);
        hasProblems = true;
      }
    });

    if (!hasProblems) {
      console.log(`${colors.green}✓${colors.reset} Aucune dépendance problématique détectée`);
    }

  } catch (error) {
    console.error(`${colors.red}Erreur lors de l'analyse des dépendances:${colors.reset}`, error.message);
  }
}

// Analyse de la configuration Tailwind
function analyzeTailwindConfig() {
  console.log(`\n${colors.cyan}${colors.bold}=== Analyse de la Configuration Tailwind ===${colors.reset}\n`);

  const tailwindConfigPath = path.join(PROJECT_ROOT, 'tailwind.config.ts');

  try {
    if (fs.existsSync(tailwindConfigPath)) {
      const configContent = fs.readFileSync(tailwindConfigPath, 'utf8');

      // Vérifier la configuration content
      if (configContent.includes('content:')) {
        console.log(`${colors.green}✓${colors.reset} Configuration content trouvée`);

        // Vérifier les patterns trop larges
        const broadPatterns = [
          './**/*.{html,js}',
          './**/*.{js,ts,jsx,tsx,mdx}',
          'node_modules'
        ];

        broadPatterns.forEach(pattern => {
          if (configContent.includes(pattern)) {
            console.log(`${colors.yellow}⚠${colors.reset} Pattern trop large détecté: "${pattern}"`);
          }
        });
      } else {
        console.log(`${colors.red}✗${colors.reset} Configuration content manquante`);
      }

      // Vérifier les plugins
      if (configContent.includes('plugins:')) {
        console.log(`${colors.green}✓${colors.reset} Plugins configurés`);
      }
    } else {
      console.log(`${colors.red}✗${colors.reset} Fichier tailwind.config.ts non trouvé`);
    }
  } catch (error) {
    console.error(`${colors.red}Erreur lors de l'analyse de Tailwind:${colors.reset}`, error.message);
  }
}

// Analyse de la configuration Next.js
function analyzeNextConfig() {
  console.log(`\n${colors.cyan}${colors.bold}=== Analyse de la Configuration Next.js ===${colors.reset}\n`);

  const nextConfigPath = path.join(PROJECT_ROOT, 'next.config.ts');

  try {
    if (fs.existsSync(nextConfigPath)) {
      const configContent = fs.readFileSync(nextConfigPath, 'utf8');

      const checks = [
        { pattern: 'removeConsole', description: 'Suppression des console.log en production' },
        { pattern: 'compress: true', description: 'Compression activée' },
        { pattern: 'optimizeCss: true', description: 'Optimisation CSS activée' },
        { pattern: 'styledComponents: true', description: 'Optimisation styled-components' },
      ];

      checks.forEach(check => {
        if (configContent.includes(check.pattern)) {
          console.log(`${colors.green}✓${colors.reset} ${check.description}`);
        } else {
          console.log(`${colors.yellow}⚠${colors.reset} ${check.description} non activée`);
        }
      });
    } else {
      console.log(`${colors.red}✗${colors.reset} Fichier next.config.ts non trouvé`);
    }
  } catch (error) {
    console.error(`${colors.red}Erreur lors de l'analyse de Next.js:${colors.reset}`, error.message);
  }
}

// Vérifier l'utilisation de React.memo et useCallback
function analyzeReactOptimizations() {
  console.log(`\n${colors.cyan}${colors.bold}=== Analyse des Optimisations React ===${colors.reset}\n`);

  const componentsDir = path.join(PROJECT_ROOT, 'src/components');

  try {
    if (fs.existsSync(componentsDir)) {
      const components = [];

      // Parcourir les composants
      function walkDir(dir) {
        const files = fs.readdirSync(dir);

        files.forEach(file => {
          const filePath = path.join(dir, file);
          const stat = fs.statSync(filePath);

          if (stat.isDirectory()) {
            walkDir(filePath);
          } else if (file.endsWith('.tsx') || file.endsWith('.jsx')) {
            components.push(filePath);
          }
        });
      }

      walkDir(componentsDir);

      let memoCount = 0;
      let useCallbackCount = 0;
      let useMemoCount = 0;

      components.forEach(componentPath => {
        const content = fs.readFileSync(componentPath, 'utf8');

        if (content.includes('React.memo')) memoCount++;
        if (content.includes('useCallback')) useCallbackCount++;
        if (content.includes('useMemo')) useMemoCount++;
      });

      console.log(`${colors.white}Composants analysés: ${components.length}${colors.reset}`);
      console.log(`${colors.green}✓${colors.reset} Composants avec React.memo: ${memoCount}`);
      console.log(`${colors.green}✓${colors.reset} Utilisations de useCallback: ${useCallbackCount}`);
      console.log(`${colors.green}✓${colors.reset} Utilisations de useMemo: ${useMemoCount}`);

      // Recommandations
      if (memoCount < components.length * 0.3) {
        console.log(`${colors.yellow}⚠${colors.reset} Seulement ${Math.round((memoCount / components.length) * 100)}% des composants utilisent React.memo`);
        console.log(`${colors.white}  Recommandation: Utiliser React.memo pour les composants purs${colors.reset}`);
      }

    } else {
      console.log(`${colors.red}✗${colors.reset} Répertoire des composants non trouvé: ${componentsDir}`);
    }
  } catch (error) {
    console.error(`${colors.red}Erreur lors de l'analyse React:${colors.reset}`, error.message);
  }
}

// Vérifier les images non optimisées
function analyzeImages() {
  console.log(`\n${colors.cyan}${colors.bold}=== Analyse des Images ===${colors.reset}\n`);

  const publicDir = path.join(PROJECT_ROOT, 'public');

  try {
    if (fs.existsSync(publicDir)) {
      const images = [];

      function walkDir(dir) {
        const files = fs.readdirSync(dir);

        files.forEach(file => {
          const filePath = path.join(dir, file);
          const stat = fs.statSync(filePath);

          if (stat.isDirectory()) {
            walkDir(filePath);
          } else if (/\.(png|jpg|jpeg|gif|webp|avif)$/i.test(file)) {
            images.push({
              path: filePath,
              size: stat.size,
              name: file
            });
          }
        });
      }

      walkDir(publicDir);

      console.log(`${colors.white}Images trouvées: ${images.length}${colors.reset}`);

      if (images.length > 0) {
        let totalSize = 0;
        const largeImages = [];

        images.forEach(img => {
          totalSize += img.size;

          if (img.size > 500 * 1024) { // > 500KB
            largeImages.push(img);
          }
        });

        console.log(`${colors.white}Taille totale des images: ${formatBytes(totalSize)}${colors.reset}`);

        if (largeImages.length > 0) {
          console.log(`${colors.yellow}⚠${colors.reset} Images volumineuses détectées (> 500KB):`);
          largeImages.forEach(img => {
            console.log(`  ${colors.red}✗${colors.reset} ${img.name}: ${formatBytes(img.size)}`);
          });
          console.log(`${colors.white}  Recommandation: Optimiser avec tools.squoosh.app ou ImageOptim${colors.reset}`);
        } else {
          console.log(`${colors.green}✓${colors.reset} Aucune image trop volumineuse détectée`);
        }
      }
    } else {
      console.log(`${colors.red}✗${colors.reset} Répertoire public non trouvé`);
    }
  } catch (error) {
    console.error(`${colors.red}Erreur lors de l'analyse des images:${colors.reset}`, error.message);
  }
}

// Générer un rapport de recommandations
function generateRecommendations() {
  console.log(`\n${colors.magenta}${colors.bold}=== Recommandations d'Optimisation ===${colors.reset}\n`);

  const recommendations = [
    {
      category: 'Bundle Size',
      items: [
        'Utiliser dynamic imports pour les composants lourds (PDF viewer, charts)',
        'Vérifier les dépendances inutiles avec `npm ls --depth=0`',
        'Configurer code splitting avec Next.js dynamic()',
      ]
    },
    {
      category: 'Performance React',
      items: [
        'Utiliser React.memo pour tous les composants purs',
        'Toujours utiliser useCallback pour les event handlers',
        'Utiliser useMemo pour les calculs coûteux',
        'Éviter les re-renders inutiles avec des props stables',
      ]
    },
    {
      category: 'CSS & Tailwind',
      items: [
        'Vérifier la configuration content de Tailwind',
        'Utiliser PurgeCSS en production (automatique avec Tailwind v3+)',
        'Minifier le CSS avec cssnano',
        'Utiliser les CSS custom properties pour les thèmes',
      ]
    },
    {
      category: 'Images & Assets',
      items: [
        'Optimiser toutes les images avec WebP/AVIF format',
        'Utiliser le lazy loading pour les images hors viewport',
        'Implémenter les placeholders pour les images',
        'Utiliser les sprites pour les petites icônes',
      ]
    },
    {
      category: 'Monitoring',
      items: [
        'Configurer les Web Vitals avec next/web-vitals',
        'Implémenter un service de monitoring des performances',
        'Tester régulièrement avec Lighthouse',
        'Configurer des alertes pour les métriques critiques',
      ]
    }
  ];

  recommendations.forEach(rec => {
    console.log(`${colors.cyan}${rec.category}:${colors.reset}`);
    rec.items.forEach(item => {
      console.log(`  ${colors.white}•${colors.reset} ${item}`);
    });
    console.log('');
  });
}

// Fonction principale
function main() {
  console.log(`${colors.bold}${colors.magenta}🔍 Analyse du Bundle Size - Chat Emploi 🔍${colors.reset}\n`);

  analyzeDependencies();
  analyzeTailwindConfig();
  analyzeNextConfig();
  analyzeReactOptimizations();
  analyzeImages();
  generateRecommendations();

  console.log(`${colors.bold}${colors.green}✅ Analyse terminée !${colors.reset}\n`);
  console.log(`${colors.white}Pour optimiser votre application:${colors.reset}`);
  console.log(`${colors.white}1. Exécutez ${colors.yellow}npm run build:analyze${colors.white} pour une analyse détaillée${colors.reset}`);
  console.log(`${colors.white}2. Utilisez ${colors.yellow}@next/bundle-analyzer${colors.white} pour visualiser le bundle${colors.reset}`);
  console.log(`${colors.white}3. Testez avec ${colors.yellow}Lighthouse${colors.white} pour les Web Vitals${colors.reset}`);
}

// Exécution
if (require.main === module) {
  main();
}

module.exports = {
  analyzeDependencies,
  analyzeTailwindConfig,
  analyzeNextConfig,
  analyzeReactOptimizations,
  analyzeImages,
  generateRecommendations
};
