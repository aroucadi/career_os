"use client";

import React from "react";
import { Cpu, ShieldCheck, Zap, Building2, Sliders, X } from "lucide-react";
import { EnergyCreditBadge } from "./EnergyCreditBadge";
import { ProgressiveDrawer } from "../primitives/ProgressiveDrawer";

interface AdminSecretDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  activeModel: string;
  onModelChange: (model: string) => void;
  onOpenRecruiterPortal: () => void;
}

export const AdminSecretDrawer: React.FC<AdminSecretDrawerProps> = ({
  isOpen,
  onClose,
  activeModel,
  onModelChange,
  onOpenRecruiterPortal,
}) => {
  return (
    <ProgressiveDrawer
      isOpen={isOpen}
      onClose={onClose}
      title="Developer & Administrative Telemetry"
      subtitle="Unlocked via 5-Tap Gesture • Protected Diagnostic Suite"
      width="default"
    >
      <div className="space-y-4">
        {/* Model Selector Section */}
        <div className="p-3.5 bg-surface-subtle rounded-xl border border-border-subtle space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-content-primary flex items-center gap-1.5">
              <Cpu className="h-4 w-4 text-accent" />
              <span>Inference Engine Model</span>
            </span>
            <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
              Low-Latency
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-1">
            <button
              type="button"
              onClick={() => onModelChange("gemini-2.5-flash")}
              className={`p-2.5 rounded-lg border text-left text-xs transition-all ${
                activeModel === "gemini-2.5-flash"
                  ? "bg-white border-accent ring-1 ring-accent text-content-primary font-bold shadow-xs"
                  : "bg-surface border-border-subtle text-content-secondary hover:border-border-interactive"
              }`}
            >
              <div>Gemini 2.5 Flash</div>
              <div className="text-[10px] font-normal text-content-muted mt-0.5">
                Sub-second streaming & fast verdicts
              </div>
            </button>

            <button
              type="button"
              onClick={() => onModelChange("gemini-2.5-pro")}
              className={`p-2.5 rounded-lg border text-left text-xs transition-all ${
                activeModel === "gemini-2.5-pro"
                  ? "bg-white border-accent ring-1 ring-accent text-content-primary font-bold shadow-xs"
                  : "bg-surface border-border-subtle text-content-secondary hover:border-border-interactive"
              }`}
            >
              <div>Gemini 2.5 Pro</div>
              <div className="text-[10px] font-normal text-content-muted mt-0.5">
                Deep multi-agent reasoning & arbitration
              </div>
            </button>
          </div>
        </div>

        {/* Compute & Energy Credits */}
        <div className="p-3.5 bg-surface-subtle rounded-xl border border-border-subtle space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-content-primary flex items-center gap-1.5">
              <Zap className="h-4 w-4 text-amber-500" />
              <span>Compute Energy Guard</span>
            </span>
          </div>
          <div className="pt-1">
            <EnergyCreditBadge userId="alaa_roucadi" />
          </div>
        </div>

        {/* Recruiter Portal Switcher */}
        <div className="p-3.5 bg-surface-subtle rounded-xl border border-border-subtle space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-content-primary flex items-center gap-1.5">
              <Building2 className="h-4 w-4 text-indigo-600" />
              <span>B2B Recruiter Portal</span>
            </span>
          </div>
          <p className="text-xs text-content-muted leading-relaxed">
            Switch into the corporate requisition slate workspace to audit incoming candidate matches against active requisitions.
          </p>
          <button
            type="button"
            onClick={() => {
              onClose();
              onOpenRecruiterPortal();
            }}
            className="w-full min-touch-target flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-surface border border-border-interactive hover:bg-slate-100 text-content-primary font-semibold text-xs transition-colors shadow-xs"
          >
            <span>Launch B2B Recruiter Workspace</span>
          </button>
        </div>

        {/* System Diagnostics */}
        <div className="p-3 rounded-xl border border-slate-200 bg-slate-50 text-[11px] font-mono text-content-muted flex items-center justify-between">
          <span>Engine Status: <strong className="text-emerald-600">ONLINE</strong></span>
          <span>Latency: <strong className="text-content-primary tabular-nums">34ms</strong></span>
          <span>Build: <strong className="text-content-primary">v2.0-spec0045</strong></span>
        </div>
      </div>
    </ProgressiveDrawer>
  );
};

export default AdminSecretDrawer;
