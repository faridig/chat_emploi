'use client';

import { useReportWebVitals } from 'next/web-vitals';

/**
 * Composant pour le monitoring des Web Vitals
 * Enregistre les métriques de performance dans la console en développement
 * et pourrait être étendu pour envoyer à un service d'analytics en production
 */
export function WebVitals() {
  useReportWebVitals((metric) => {
    // En développement, on log les métriques dans la console
    if (process.env.NODE_ENV === 'development') {
      console.log(metric);
    }

    // En production, on pourrait envoyer les métriques à un service d'analytics
    // Exemple: Google Analytics, Sentry, ou un endpoint backend
    if (process.env.NODE_ENV === 'production') {
      // TODO: Implémenter l'envoi des métriques en production
      // sendToAnalytics(metric);
    }
  });

  // Ce composant ne rend rien visuellement
  return null;
}
