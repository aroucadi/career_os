"use client";

import React, { useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * ProgressiveDrawer Primitive (Depth 3 Deep-Dive Container)
 * Accessible, swipe/dismiss non-blocking drawer for explanations, telemetry, and provenance.
 * Preserves Depth 1 glanceability by isolating dense details.
 */

interface ProgressiveDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  width?: "default" | "wide" | "full";
  className?: string;
}

export const ProgressiveDrawer: React.FC<ProgressiveDrawerProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  width = "default",
  className,
}) => {
  // Handle ESC key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Prevent background scroll when open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const widthClasses = {
    default: "max-w-md md:max-w-lg",
    wide: "max-w-2xl md:max-w-3xl",
    full: "max-w-4xl md:max-w-5xl",
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="drawer-title"
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-slate-950/60 backdrop-blur-xs transition-opacity duration-200"
      onClick={onClose}
    >
      <div
        className={cn(
          "w-full bg-surface rounded-t-2xl sm:rounded-2xl border border-border-subtle shadow-career-elevated flex flex-col max-h-[90vh] sm:max-h-[85vh] animate-in slide-in-from-bottom-6 duration-200",
          widthClasses[width],
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Mobile Swipe Handle Indicator */}
        <div className="sm:hidden flex justify-center pt-3 pb-1">
          <div className="w-12 h-1.5 rounded-full bg-slate-300" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border-subtle shrink-0">
          <div>
            <h2 id="drawer-title" className="text-sm sm:text-base font-bold text-content-primary">
              {title}
            </h2>
            {subtitle && (
              <p className="text-xs text-content-muted font-medium mt-0.5">
                {subtitle}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            aria-label="Close drawer"
            className="min-touch-target flex items-center justify-center rounded-lg text-content-muted hover:text-content-primary hover:bg-surface-subtle transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Content Area */}
        <div className="p-5 overflow-y-auto space-y-4">
          {children}
        </div>
      </div>
    </div>
  );
};

export default ProgressiveDrawer;
