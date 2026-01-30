/**
 * Tests pour les optimisations de bundle size
 * Module 11 : Cool Down & Polish
 */

import { describe, test, expect } from 'vitest';
import fs from 'fs';
import path from 'path';

// Helper pour obtenir le chemin racine du projet frontend
const projectRoot = path.join(__dirname, '../../..');

describe('Bundle Size Optimization', () => {
  test('package.json should have optimized dependencies', () => {
    const packageJsonPath = path.join(projectRoot, 'package.json');
    expect(fs.existsSync(packageJsonPath), 'package.json should exist').toBe(true);
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));

    const prodDeps = packageJson.dependencies || {};

    const unnecessaryDeps = ['lodash', 'moment', 'jquery'];
    unnecessaryDeps.forEach(dep => {
      expect(prodDeps[dep], `${dep} should not be in production dependencies`).toBeUndefined();
    });

    expect(prodDeps['next']).toBeDefined();
  });

  test('tailwind.config.ts should have proper content configuration', () => {
    const tailwindConfigPath = path.join(projectRoot, 'tailwind.config.ts');
    expect(fs.existsSync(tailwindConfigPath), 'tailwind.config.ts should exist').toBe(true);
    const tailwindConfig = fs.readFileSync(tailwindConfigPath, 'utf-8');

    expect(tailwindConfig).toContain('content:');
    expect(tailwindConfig).toContain('./src/**/*.{js,ts,jsx,tsx,mdx}');
    expect(tailwindConfig).not.toContain('./**/*.{html,js}');
  });

  test('next.config.js or ts should have proper optimization settings', () => {
    const nextConfigTsPath = path.join(projectRoot, 'next.config.ts');
    const nextConfigJsPath = path.join(projectRoot, 'next.config.js');

    const configPath = fs.existsSync(nextConfigTsPath) ? nextConfigTsPath : nextConfigJsPath;
    expect(fs.existsSync(configPath), 'next.config.js or next.config.ts should exist').toBe(true);

    const nextConfig = fs.readFileSync(configPath, 'utf-8');

    expect(nextConfig).toContain('compress: true');
    expect(nextConfig).toContain('removeConsole:');
  });
});


describe('Code Splitting Analysis', () => {
  test('should have proper dynamic imports for large components', () => {
    // Vérifier que les composants lourds utilisent dynamic imports
    const appDir = path.join(__dirname, '../../../src/app');

    // Lire quelques fichiers pour vérifier les patterns
    const filesToCheck = [
      'page.tsx',
      'layout.tsx',
      'components/large/'
    ];

    // Vérifier l'utilisation de dynamic imports
    filesToCheck.forEach(file => {
      const filePath = path.join(appDir, file);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf-8');

        // Vérifier l'utilisation de dynamic imports pour les composants lourds
        if (content.includes('PDF') || content.includes('Chart') || content.includes('Editor')) {
          expect(content).toContain('dynamic(');
          expect(content).toContain('ssr: false');
        }
      }
    });
  });

  test('should use proper React optimization patterns', () => {
    const componentsDir = path.join(__dirname, '../../../src/components');

    // Vérifier quelques composants pour les patterns d'optimisation
    const sampleComponents = [
      'ui/Button.tsx',
      'ui/Card.tsx',
      'chat/ChatMessage.tsx'
    ];

    sampleComponents.forEach(component => {
      const filePath = path.join(componentsDir, component);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf-8');

        // Vérifier l'utilisation de React.memo pour les composants purs
        if (component.includes('Button') || component.includes('Card')) {
          expect(content).toContain('React.memo');
        }

        // Vérifier l'utilisation de useMemo/useCallback
        if (content.includes('useState') || content.includes('useEffect')) {
          expect(content).toContain('useMemo') || expect(content).toContain('useCallback');
        }
      }
    });
  });
});
