'use client';

import React, { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';

interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  placeholder?: string;
  blurDataURL?: string;
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * Composant d'image lazy load avec placeholder
 * Optimise le LCP (Largest Contentful Paint) et réduite la CLS (Cumulative Layout Shift)
 */
export function LazyImage({
  src,
  alt,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjRjBGMEYwIi8+PC9zdmc+',
  blurDataURL,
  width,
  height,
  priority = false,
  className,
  onLoad,
  onError,
  ...props
}: LazyImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(placeholder);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    if (!src || hasError) return;

    // Si priorité élevée, charger immédiatement
    if (priority) {
      loadImage();
      return;
    }

    // Sinon, utiliser IntersectionObserver pour lazy loading
    if (!observerRef.current && 'IntersectionObserver' in window) {
      observerRef.current = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              loadImage();
              observerRef.current?.unobserve(entry.target);
            }
          });
        },
        {
          rootMargin: '50px', // Commencer à charger 50px avant d'entrer dans le viewport
          threshold: 0.01,
        }
      );
    }

    if (imgRef.current && observerRef.current) {
      observerRef.current.observe(imgRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [src, priority, hasError]);

  const loadImage = () => {
    if (!src) return;

    const image = new Image();

    image.onload = () => {
      setIsLoaded(true);
      setCurrentSrc(src);
      onLoad?.();
    };

    image.onerror = () => {
      setHasError(true);
      console.error(`Failed to load image: ${src}`);
      onError?.();
    };

    image.src = src;
  };

  // Styles pour le placeholder
  const placeholderStyles = !isLoaded
    ? {
        backgroundImage: blurDataURL ? `url(${blurDataURL})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        filter: blurDataURL ? 'blur(10px)' : undefined,
      }
    : {};

  return (
    <div
      className={cn(
        'relative overflow-hidden',
        !isLoaded && 'animate-pulse',
        className
      )}
      style={{
        width: width ? `${width}px` : '100%',
        height: height ? `${height}px` : 'auto',
        aspectRatio: width && height ? `${width}/${height}` : undefined,
      }}
    >
      {/* Placeholder */}
      {!isLoaded && (
        <div
          className="absolute inset-0 bg-gray-100"
          style={placeholderStyles}
          aria-hidden="true"
        />
      )}

      {/* Image réelle */}
      <img
        ref={imgRef}
        src={currentSrc}
        alt={alt}
        width={width}
        height={height}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
        className={cn(
          'transition-opacity duration-300',
          isLoaded ? 'opacity-100' : 'opacity-0',
          'w-full h-full object-cover'
        )}
        onLoad={() => {
          if (currentSrc === src) {
            setIsLoaded(true);
            onLoad?.();
          }
        }}
        onError={() => {
          setHasError(true);
          onError?.();
        }}
        {...props}
      />

      {/* Indicateur de chargement (optionnel) */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-brand-primary" />
        </div>
      )}

      {/* Indicateur d'erreur (optionnel) */}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center text-gray-400">
            <div className="mb-2 text-2xl">📷</div>
            <div className="text-sm">Image non disponible</div>
          </div>
        </div>
      )}
    </div>
  );
}

// Version mémoïsée pour les images statiques
export const MemoizedLazyImage = React.memo(LazyImage);
