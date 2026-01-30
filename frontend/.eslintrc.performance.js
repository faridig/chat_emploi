/**
 * Configuration ESLint pour les règles de performance
 * Module 11 : Cool Down & Polish
 */

export default {
  extends: [
    'next/core-web-vitals',
  ],
  plugins: ['react-hooks', 'react-perf'],
  rules: {
    // Règles React Hooks pour la performance
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'error',

    // Règles de performance React
    'react/jsx-no-bind': ['warn', {
      ignoreDOMComponents: true,
      ignoreRefs: true,
      allowArrowFunctions: false,
      allowFunctions: false,
      allowBind: false,
    }],

    'react/jsx-no-constructed-context-values': 'warn',
    'react/jsx-no-useless-fragment': 'warn',
    'react/no-unstable-nested-components': 'warn',

    // Préférer les fonctions nommées pour le debugging
    'react/function-component-definition': ['warn', {
      namedComponents: 'function-declaration',
      unnamedComponents: 'arrow-function',
    }],

    // Éviter les props inline
    'react/jsx-curly-brace-presence': ['warn', {
      props: 'never',
      children: 'never',
    }],

    // Optimisation des re-renders
    'react/require-optimization': 'off', // Trop strict, mais bon à savoir

    // Règles générales de performance
    'no-console': process.env.NODE_ENV === 'production' ? ['warn', { allow: ['warn', 'error'] }] : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',

    // Éviter les fonctions anonymes dans les props
    'react/jsx-handler-names': ['warn', {
      eventHandlerPrefix: 'handle',
      eventHandlerPropPrefix: 'on',
    }],

    // Utiliser des keys stables pour les listes
    'react/jsx-key': ['error', {
      checkFragmentShorthand: true,
      checkKeyMustBeforeSpread: true,
    }],

    // Éviter les spreads inutiles
    'react/jsx-props-no-spreading': 'off', // Désactivé car utile avec les design systems

    // Préférer les fragments courts
    'react/jsx-fragments': ['warn', 'syntax'],
  },
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
      rules: {
        'react/jsx-no-bind': 'off',
        'react-hooks/exhaustive-deps': 'off',
        'no-console': 'off',
      },
    },
    {
      files: ['**/components/**/*.tsx', '**/components/**/*.jsx'],
      rules: {
        'react/require-optimization': 'warn',
      },
    },
  ],
};
