'use client';

import React, { memo, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface OptimizedButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  icon?: React.ReactNode;
}

/**
 * Bouton optimisé avec React.memo et useCallback
 * Réduit les re-renders inutiles
 */
export const OptimizedButton = memo(function OptimizedButton({
  onClick,
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className,
  icon,
}: OptimizedButtonProps) {
  // Utilisation de useCallback pour éviter la création de nouvelles fonctions à chaque render
  const handleClick = useCallback(
    (e: React.MouseEvent<HTMLButtonElement>) => {
      if (disabled || loading) return;
      e.preventDefault();
      onClick();
    },
    [onClick, disabled, loading]
  );

  // Styles variants
  const variantStyles = {
    primary: 'bg-brand-primary text-white hover:bg-brand-primary-light',
    secondary: 'bg-brand-secondary text-white hover:bg-brand-secondary-light',
    outline:
      'border border-[#E2E8F0] bg-transparent hover:bg-accent hover:text-accent-foreground',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    destructive: 'bg-error text-white hover:bg-error/90',
  };

  // Styles sizes
  const sizeStyles = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-4 py-2',
    lg: 'h-12 px-6 text-lg',
    icon: 'h-10 w-10',
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      aria-busy={loading}
    >
      {loading && (
        <span data-testid="loading-spinner" className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
});

// Display name pour le debugging
OptimizedButton.displayName = 'OptimizedButton';
