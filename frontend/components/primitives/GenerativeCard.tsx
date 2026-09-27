"use client";

import React, { useState } from "react";
import { Sparkles, Check, HelpCircle, ArrowRight, ShieldCheck, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";
import { ProgressiveDrawer } from "./ProgressiveDrawer";

/**
 * GenerativeCard Primitive (Phase 3 Generative UI Engine)
 * Enforces:
 * 1. State Triad: Resolving Skeleton (CLS=0) -> Interactive Proposal -> Committed Morph
 * 2. Confidence-Driven Progressive UI: >= 90% direct apply, < 90% binary fork (Option A vs B)
 * 3. Non-Blocking Provenance Drawer: Micro-pill to inspect prompt rationale and sources
 */

export type GenerativeState = "resolving" | "proposal" | "committed";

export interface GenerativeForkOption {
  id: string;
  label: string;
  desc: string;
  confidenceScore: number;
}

interface GenerativeCardProps {
  id: string;
  title: string;
  category: string;
  confidence: number; // 0 to 100
  initialState?: GenerativeState;
  suggestedActionLabel?: string;
  onCommit?: (selectedOptionId?: string) => void;
  // Binary fork options when confidence < 90%
  forkOptions?: [GenerativeForkOption, GenerativeForkOption];
  provenance?: {
    model: string;
    reasoning: string;
    sources: string[];
  };
  children?: React.ReactNode;
  committedContent?: React.ReactNode;
  className?: string;
}

export const GenerativeCard: React.FC<GenerativeCardProps> = ({
  id,
  title,
  category,
  confidence,
  initialState = "proposal",
  suggestedActionLabel = "Apply Proposal",
  onCommit,
  forkOptions,
  provenance,
  children,
  committedContent,
  className,
}) => {
  const [state, setState] = useState<GenerativeState>(initialState);
  const [selectedFork, setSelectedFork] = useState<string | null>(
    forkOptions ? forkOptions[0].id : null
  );
  const [showProvenance, setShowProvenance] = useState(false);

  const isLowConfidence = confidence < 90 && !!forkOptions;

  const handleApply = () => {
    setState("committed");
    onCommit?.(selectedFork || undefined);
  };

  // State A: Resolving / Streaming Skeleton (Exact Dimensions, CLS = 0)
  if (state === "resolving") {
    return (
      <div
        className={cn(
          "w-full rounded-xl p-5 border border-border-subtle bg-surface animate-pulse flex flex-col gap-3 min-h-[160px]",
          className
        )}
      >
        <div className="flex items-center justify-between">
          <div className="h-4 w-28 bg-slate-200 rounded" />
          <div className="h-4 w-16 bg-slate-200 rounded-full" />
        </div>
        <div className="h-6 w-3/4 bg-slate-200 rounded" />
        <div className="h-10 w-full bg-slate-100 rounded-lg" />
        <div className="h-9 w-32 bg-slate-200 rounded-lg self-end" />
      </div>
    );
  }

  // State C: Morph to Committed State
  if (state === "committed") {
    return (
      <div
        className={cn(
          "w-full rounded-xl p-4 sm:p-5 border border-emerald-200 bg-emerald-50/40 transition-all duration-300",
          className
        )}
      >
        <div className="flex items-center justify-between pb-2 border-b border-emerald-200/60">
          <div className="flex items-center gap-2 text-emerald-800 text-xs font-semibold">
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
            <span>Committed & Verified in Profile</span>
          </div>
          <span className="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold border border-emerald-200">
            Active
          </span>
        </div>

        <div className="mt-3 text-xs sm:text-sm text-slate-800">
          {committedContent || children}
        </div>
      </div>
    );
  }

  // State B: Interactive Proposal Card
  return (
    <>
      <div
        className={cn(
          "w-full rounded-xl p-4 sm:p-5 border border-border-subtle bg-surface shadow-career-card transition-all flex flex-col gap-3.5",
          className
        )}
      >
        {/* Card Eyebrow */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5 font-mono text-[11px] font-semibold text-accent uppercase tracking-wider">
            <Sparkles className="h-3.5 w-3.5 text-accent" />
            <span>{category}</span>
          </div>

          <div className="flex items-center gap-2">
            {/* Confidence Pill */}
            <span
              className={cn(
                "text-[10px] font-mono font-bold px-2 py-0.5 rounded border tabular-nums",
                confidence >= 90
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : "bg-amber-50 text-amber-700 border-amber-200"
              )}
            >
              {confidence}% Confidence
            </span>

            {/* Non-Blocking Provenance Pill Trigger */}
            {provenance && (
              <button
                type="button"
                onClick={() => setShowProvenance(true)}
                className="text-[11px] text-content-muted hover:text-content-primary inline-flex items-center gap-1 transition-colors px-1.5 py-0.5 rounded hover:bg-surface-subtle"
                title="Inspect AI generation reasoning and sources"
              >
                <HelpCircle className="h-3 w-3" />
                <span className="hidden sm:inline">Why?</span>
              </button>
            )}
          </div>
        </div>

        {/* Hero Title */}
        <h3 className="text-sm sm:text-base font-bold text-content-primary tracking-tight">
          {title}
        </h3>

        {/* Binary Fork (If Low Confidence < 90%) */}
        {isLowConfidence && forkOptions && (
          <div className="flex flex-col gap-2 p-3 bg-surface-subtle rounded-xl border border-border-subtle">
            <span className="text-[11px] font-semibold text-content-muted">
              Select desired strategic framing before applying:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {forkOptions.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setSelectedFork(opt.id)}
                  className={cn(
                    "text-left p-2.5 rounded-lg border transition-all text-xs flex flex-col gap-1 min-touch-target",
                    selectedFork === opt.id
                      ? "bg-white border-accent shadow-xs text-content-primary ring-1 ring-accent"
                      : "bg-surface border-border-subtle text-content-secondary hover:border-border-interactive"
                  )}
                >
                  <div className="flex items-center justify-between font-semibold">
                    <span>{opt.label}</span>
                    <span className="text-[10px] font-mono text-content-muted tabular-nums">
                      {opt.confidenceScore}%
                    </span>
                  </div>
                  <span className="text-[11px] text-content-muted leading-tight">
                    {opt.desc}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Proposal Body */}
        <div className="text-xs sm:text-sm text-content-secondary leading-relaxed">
          {children}
        </div>

        {/* Single Primary Dominant CTA per Viewport */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-border-subtle">
          <button
            type="button"
            onClick={handleApply}
            className="min-touch-target inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-lg bg-accent text-white font-medium text-xs sm:text-sm hover:bg-accent-hover transition-colors shadow-xs"
          >
            <Check className="h-4 w-4" />
            <span>{suggestedActionLabel}</span>
          </button>
        </div>
      </div>

      {/* Non-Blocking Provenance Drawer (Depth 3) */}
      {provenance && (
        <ProgressiveDrawer
          isOpen={showProvenance}
          onClose={() => setShowProvenance(false)}
          title="AI Synthesis Provenance"
          subtitle={`Model: ${provenance.model} • ${confidence}% Confidence`}
        >
          <div className="space-y-4 text-xs sm:text-sm text-content-secondary">
            <div>
              <h4 className="font-semibold text-content-primary mb-1">
                Strategic Rationale
              </h4>
              <p className="bg-surface-subtle p-3 rounded-lg border border-border-subtle leading-relaxed">
                {provenance.reasoning}
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-content-primary mb-1">
                Grounded Ground-Truth Sources
              </h4>
              <ul className="list-disc pl-4 space-y-1 text-content-muted text-xs">
                {provenance.sources.map((src, idx) => (
                  <li key={idx} className="font-mono">{src}</li>
                ))}
              </ul>
            </div>
          </div>
        </ProgressiveDrawer>
      )}
    </>
  );
};

export default GenerativeCard;
