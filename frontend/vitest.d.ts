/// <reference types="vitest" />

// Déclarations globales pour Vitest
import type { Mock, MockedFunction } from 'vitest';

declare global {
  const vi: typeof import('vitest')['vi'];
  const describe: typeof import('vitest')['describe'];
  const it: typeof import('vitest')['it'];
  const test: typeof import('vitest')['test'];
  const expect: typeof import('vitest')['expect'];
  const beforeEach: typeof import('vitest')['beforeEach'];
  const afterEach: typeof import('vitest')['afterEach'];
  const beforeAll: typeof import('vitest')['beforeAll'];
  const afterAll: typeof import('vitest')['afterAll'];

  // Types pour les mocks
  type ViMock = Mock;
  type ViMockedFunction<T extends (...args: any[]) => any> = MockedFunction<T>;
}

// Export pour les imports
export {};
