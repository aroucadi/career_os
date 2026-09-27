"use client";

import React from "react";
import { cn } from "@/lib/utils";

/**
 * SurfaceCard Compound Primitive
 * Enforces the Vertical Element Ceiling (Anti-Slop Architecture):
 * 1. Eyebrow / Context
 * 2. Hero / Primary Value
 * 3. Supporting Status or Micro-Action
 * 
 * Uses compound components (zero boolean prop proliferation).
 */

interface SurfaceCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: "default" | "elevated" | "accent";
}

interface SurfaceCardSubProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function SurfaceCardRoot({ children, className, variant = "default", ...props }: SurfaceCardProps) {
  const variantStyles = {
    default: "bg-surface border border-border-subtle shadow-career-card",
    elevated: "bg-surface border border-border-subtle shadow-career-elevated",
    accent: "bg-surface border-l-4 border-l-accent border-y border-r border-border-subtle shadow-career-card",
  };

  return (
    <div
      className={cn(
        "rounded-xl p-4 sm:p-5 transition-all text-content-primary",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      <div className="flex flex-col gap-3">
        {children}
      </div>
    </div>
  );
}

export function SurfaceCardHeader({ children, className, ...props }: SurfaceCardSubProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-between gap-2 text-xs font-medium text-content-muted",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function SurfaceCardHero({ children, className, ...props }: SurfaceCardSubProps) {
  return (
    <div
      className={cn(
        "text-base sm:text-lg font-semibold tracking-tight text-content-primary",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function SurfaceCardBody({ children, className, ...props }: SurfaceCardSubProps) {
  return (
    <div
      className={cn(
        "text-xs sm:text-sm text-content-secondary leading-relaxed",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function SurfaceCardActions({ children, className, ...props }: SurfaceCardSubProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-2 pt-1 border-t border-border-subtle/80 mt-1",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export const SurfaceCard = Object.assign(SurfaceCardRoot, {
  Header: SurfaceCardHeader,
  Hero: SurfaceCardHero,
  Body: SurfaceCardBody,
  Actions: SurfaceCardActions,
});

export default SurfaceCard;
