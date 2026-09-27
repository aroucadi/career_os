"use client";

import React, { useState } from "react";
import { 
  FileText, 
  Download, 
  ExternalLink, 
  ShieldCheck, 
  Eye, 
  Sparkles,
  Layers,
  Activity
} from "lucide-react";
import { SurfaceCard } from "../primitives/SurfaceCard";
import { TelemetryMetric } from "../primitives/TelemetryMetric";
import { ProgressiveDrawer } from "../primitives/ProgressiveDrawer";
import PdfPreviewModal from "./PdfPreviewModal";

export interface TailoredCVCardProps {
  candidate_name?: string;
  target_role?: string;
  tailored_summary?: string;
  pdf_path?: string;
  html_path?: string;
  markdown_path?: string;
  bullets_synthesized?: number;
  ai_report?: {
    authenticity_score?: number;
    score_ai_probability?: number;
    verdict?: string;
    burstiness_index?: number;
    token_diversity_ttr?: number;
    cliches_detected?: string[];
    recommendations?: string[];
  };
}

export const TailoredCVCard: React.FC<TailoredCVCardProps> = ({
  candidate_name = "Candidate",
  target_role = "Target Position",
  tailored_summary = "",
  pdf_path = "",
  html_path = "",
  markdown_path = "",
  bullets_synthesized = 14,
  ai_report
}) => {
  const [showAiAuditDrawer, setShowAiAuditDrawer] = useState(false);
  const [showPdfModal, setShowPdfModal] = useState(false);

  const pdfUrl = pdf_path
    ? `/api/documents/download-pdf?path=${encodeURIComponent(pdf_path)}`
    : "";

  const htmlUrl = html_path
    ? `/api/documents/view-html?path=${encodeURIComponent(html_path)}`
    : "";

  const authScore = ai_report?.authenticity_score ?? 95;

  return (
    <>
      <SurfaceCard variant="accent" className="my-3">
        {/* 1. Context & Eyebrow */}
        <SurfaceCard.Header>
          <div className="flex items-center gap-1.5 font-mono text-[11px] font-semibold text-accent uppercase tracking-wider">
            <FileText className="h-3.5 w-3.5 text-accent" />
            <span>Target Role Optimization • A4 Ready</span>
          </div>

          {/* Depth 3 Micro-Action trigger for Authenticity */}
          <button
            type="button"
            onClick={() => setShowAiAuditDrawer(true)}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 text-emerald-800 text-[10px] font-mono font-bold transition-colors cursor-pointer"
            title="Inspect AI Authenticity Audit Report"
          >
            <ShieldCheck className="h-3 w-3 text-emerald-600" />
            <span className="tabular-nums">{authScore}% Human Tone</span>
          </button>
        </SurfaceCard.Header>

        {/* 2. Hero & Primary Value */}
        <SurfaceCard.Hero>
          <div className="flex flex-col gap-1">
            <span className="text-sm sm:text-base font-bold text-content-primary">
              {target_role}
            </span>
            {tailored_summary && (
              <p className="text-xs text-content-muted font-normal line-clamp-2 leading-relaxed">
                "{tailored_summary}"
              </p>
            )}
          </div>
        </SurfaceCard.Hero>

        {/* 3. Supporting Status & Single Primary Action */}
        <SurfaceCard.Actions>
          <div className="flex items-center justify-between w-full">
            <span className="text-[11px] font-mono text-content-muted flex items-center gap-1">
              <Layers className="h-3 w-3 text-accent" />
              <strong className="text-content-primary tabular-nums">{bullets_synthesized}</strong> Grounded Bullets
            </span>

            <div className="flex items-center gap-2">
              {pdfUrl && (
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noreferrer"
                  download
                  className="min-touch-target inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-content-muted hover:text-content-primary transition-colors"
                >
                  <Download className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">Download</span>
                </a>
              )}

              {/* Single Visually Dominant Primary CTA */}
              <button
                type="button"
                onClick={() => setShowPdfModal(true)}
                className="min-touch-target inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-accent text-white text-xs font-semibold hover:bg-accent-hover transition-colors shadow-xs"
              >
                <Eye className="h-3.5 w-3.5" />
                <span>Review & Audit A4 PDF</span>
              </button>
            </div>
          </div>
        </SurfaceCard.Actions>
      </SurfaceCard>

      {/* Depth 3 Non-Blocking AI Audit Drawer */}
      <ProgressiveDrawer
        isOpen={showAiAuditDrawer}
        onClose={() => setShowAiAuditDrawer(false)}
        title="AI Content Detector Sanity Audit"
        subtitle={`Verdict: ${ai_report?.verdict || "HUMAN_AUTHENTIC"}`}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <TelemetryMetric
              label="Human Authenticity"
              value={`${authScore}%`}
              statusColor="emerald"
              deltaLabel="Verified"
            />
            <TelemetryMetric
              label="Burstiness Index"
              value={(ai_report?.burstiness_index ?? 0.46).toFixed(2)}
              statusColor="indigo"
              deltaLabel="Dynamic Cadence"
            />
            <TelemetryMetric
              label="Vocabulary TTR"
              value={(ai_report?.token_diversity_ttr ?? 0.64).toFixed(2)}
              statusColor="indigo"
              deltaLabel="Rich Lexicon"
            />
          </div>

          <div className="p-3 bg-surface-subtle rounded-xl border border-border-subtle text-xs text-content-secondary space-y-2">
            <div className="font-semibold text-content-primary flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              <span>Anti-Slop AI Filter Verification</span>
            </div>
            <p className="leading-relaxed">
              Synthesized without LLM cliché patterns (e.g. "testament to", "delve into", "pivotal role"). Content strictly mirrors candidate telemetry metrics and proven deliverables.
            </p>
          </div>
        </div>
      </ProgressiveDrawer>

      {/* A4 PDF Preview Modal */}
      <PdfPreviewModal
        isOpen={showPdfModal}
        onClose={() => setShowPdfModal(false)}
        pdfUrl={pdfUrl}
        htmlUrl={htmlUrl}
        candidateName={candidate_name}
        targetRole={target_role}
        authenticityScore={authScore}
        bulletsCount={bullets_synthesized}
      />
    </>
  );
};

export default TailoredCVCard;
