"use client";

import React, { useState } from "react";
import { Check, Clock, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * InteractiveCheckin Primitive
 * 1-tap state toggling with instant tactile feedback (Haptic vibration / micro-spring animation).
 * Enforces Fitts's Law: min 44x44px touch target on mobile, >= 8px separation.
 */

export type CheckinStatus = "pending" | "completed" | "in_review" | "skipped";

interface InteractiveCheckinProps {
  id: string;
  label: string;
  initialStatus?: CheckinStatus;
  sublabel?: string;
  onStatusChange?: (newStatus: CheckinStatus) => void;
  className?: string;
}

export const InteractiveCheckin: React.FC<InteractiveCheckinProps> = ({
  id,
  label,
  initialStatus = "pending",
  sublabel,
  onStatusChange,
  className,
}) => {
  const [status, setStatus] = useState<CheckinStatus>(initialStatus);
  const [animating, setAnimating] = useState(false);

  const toggle = () => {
    // Provide lightweight browser haptic feedback where supported
    if (typeof window !== "undefined" && "vibrate" in navigator) {
      try {
        navigator.vibrate(10);
      } catch (e) {
        // Ignore fallback
      }
    }

    setAnimating(true);
    setTimeout(() => setAnimating(false), 120);

    const nextStatus: CheckinStatus = status === "completed" ? "pending" : "completed";
    setStatus(nextStatus);
    onStatusChange?.(nextStatus);
  };

  const isCompleted = status === "completed";

  return (
    <div
      role="checkbox"
      aria-checked={isCompleted}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === " " || e.key === "Enter") {
          e.preventDefault();
          toggle();
        }
      }}
      onClick={toggle}
      className={cn(
        "min-touch-target group flex items-center justify-between gap-3 p-3 rounded-xl border transition-transform duration-[120ms] ease-[cubic-bezier(0.22,1,0.36,1)] cursor-pointer select-none",
        isCompleted
          ? "bg-emerald-50/70 border-emerald-200/80 text-emerald-950"
          : "bg-surface border-border-subtle hover:border-border-interactive text-content-primary",
        animating ? "scale-[0.97]" : "scale-100",
        className
      )}
    >
      <div className="flex items-center gap-3">
        {/* Fitts's law compliant 28px visual checkbox inside 44px touch container */}
        <div
          className={cn(
            "h-6 w-6 rounded-lg flex items-center justify-center border transition-all shrink-0",
            isCompleted
              ? "bg-emerald-600 border-emerald-600 text-white shadow-xs"
              : "border-slate-300 bg-white group-hover:border-indigo-500"
          )}
        >
          {isCompleted && <Check className="h-4 w-4 stroke-[2.5]" />}
        </div>

        <div className="flex flex-col text-left">
          <span
            className={cn(
              "text-xs sm:text-sm font-medium transition-all",
              isCompleted && "line-through text-slate-500 font-normal"
            )}
          >
            {label}
          </span>
          {sublabel && (
            <span className="text-[11px] text-content-muted font-normal">
              {sublabel}
            </span>
          )}
        </div>
      </div>

      <div className="shrink-0">
        <span
          className={cn(
            "text-[10px] font-mono uppercase px-2 py-0.5 rounded-full font-semibold border",
            isCompleted
              ? "bg-emerald-100 text-emerald-800 border-emerald-300/60"
              : "bg-slate-100 text-slate-600 border-slate-200"
          )}
        >
          {isCompleted ? "Verified" : "1-Tap Fix"}
        </span>
      </div>
    </div>
  );
};

export default InteractiveCheckin;
