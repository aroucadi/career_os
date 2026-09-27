"use client";

import React, { useState } from "react";
import { 
  Scale, 
  ShieldAlert, 
  TrendingUp, 
  Copy, 
  Check, 
  Mail, 
  AlertTriangle, 
  CheckCircle2,
  ChevronRight,
  ExternalLink
} from "lucide-react";
import { SurfaceCard } from "../primitives/SurfaceCard";
import { TelemetryMetric } from "../primitives/TelemetryMetric";
import { ProgressiveDrawer } from "../primitives/ProgressiveDrawer";

export interface DebateVerdictCardProps {
  verdict?: string;
  quality_score?: number;
  trap_score?: number;
  advocate_points?: string[];
  dealbreakers?: string[];
  decision_rationale?: string;
  binding_conditions?: string[];
  target_role?: string;
  jd_id?: string;
  recruiter_pitch?: string;
  recruiter_name?: string;
  recruiter_email?: string;
  onActionClick?: (command: string) => void;
}

export const DebateVerdictCard: React.FC<DebateVerdictCardProps> = ({
  verdict = "ENGAGE",
  quality_score = 88,
  trap_score = 15,
  advocate_points = [],
  dealbreakers = [],
  decision_rationale = "Strategic alignment is strong based on candidate leadership history.",
  binding_conditions = [],
  target_role = "AI Mandate",
  jd_id = "",
  recruiter_pitch = "",
  recruiter_name = "",
  recruiter_email = "",
  onActionClick
}) => {
  const [showDrawer, setShowDrawer] = useState(false);
  const [pitchCopied, setPitchCopied] = useState(false);
  const [recipientEmail, setRecipientEmail] = useState(recruiter_email);

  const isPositive = verdict.includes("ENGAGE") || verdict.includes("GO") || verdict.includes("TOLERATE");
  const isHardNo = verdict.includes("NO-GO") || verdict.includes("REJECT");

  const effectivePitch = recruiter_pitch || (
    isHardNo
      ? `Bonjour, merci pour votre proposition concernant le rôle de ${target_role}. Après analyse de mes critères d'alignement stratégique (notamment le travail 100% remote et mon seuil tarifaire), cette opportunité ne correspond pas à mes priorités actuelles. Restons en contact pour de futures collaborations adaptées.`
      : `Bonjour, merci pour votre prise de contact. Le périmètre de la mission "${target_role}" correspond étroitement à mes réalisations en pilotage de CoE IA et déploiement de produits à fort impact. Mon cadre d'intervention habituel s'articule en full remote pour un TJM indicatif de 950€ HT. Seriez-vous disponible cette semaine pour un court échange afin d'aborder vos enjeux prioritaires ?`
  );

  const emailSubject = `Positionnement Stratégique — ${target_role} — Alaa Eddine Roucadi`;
  const mailtoHref = `mailto:${encodeURIComponent(recipientEmail.trim())}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(effectivePitch)}`;

  const handleCopyPitch = () => {
    navigator.clipboard.writeText(effectivePitch);
    setPitchCopied(true);
    setTimeout(() => setPitchCopied(false), 2000);
  };

  return (
    <>
      <SurfaceCard variant={isHardNo ? "default" : "accent"} className="my-3">
        {/* 1. Context & Eyebrow */}
        <SurfaceCard.Header>
          <div className="flex items-center gap-1.5 font-mono text-[11px] font-semibold text-content-muted uppercase tracking-wider">
            <Scale className="h-3.5 w-3.5 text-accent" />
            <span>Adversarial Dialectic Arbitration</span>
            {jd_id && <span className="text-content-primary font-bold">• {jd_id}</span>}
          </div>

          <span
            className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
              isHardNo
                ? "bg-rose-50 text-rose-700 border-rose-200"
                : "bg-emerald-50 text-emerald-700 border-emerald-200"
            }`}
          >
            {verdict}
          </span>
        </SurfaceCard.Header>

        {/* 2. Hero & Primary Value (Vertical Ceiling Cap = 3 elements) */}
        <SurfaceCard.Hero>
          <div className="grid grid-cols-2 gap-3 py-1">
            <TelemetryMetric
              label="Quality Score"
              value={quality_score}
              unit="/100"
              statusColor={isHardNo ? "rose" : "emerald"}
              trend={isHardNo ? "down" : "up"}
            />
            <TelemetryMetric
              label="Trap Risk"
              value={trap_score}
              unit="%"
              statusColor={trap_score > 30 ? "rose" : "slate"}
            />
          </div>
        </SurfaceCard.Hero>

        {/* 3. Supporting Status & Single Primary Action */}
        <SurfaceCard.Actions>
          <div className="flex items-center justify-between w-full">
            <p className="text-xs text-content-muted line-clamp-1 max-w-[65%]">
              {decision_rationale}
            </p>

            <button
              type="button"
              onClick={() => setShowDrawer(true)}
              className="min-touch-target inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-accent text-white text-xs font-semibold hover:bg-accent-hover transition-colors shadow-xs"
            >
              <span>Examine Verdict</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </SurfaceCard.Actions>
      </SurfaceCard>

      {/* Depth 3 Deep-Dive Drawer: Prosecutor Traps + Advocate Levers + Recruiter Outreach */}
      <ProgressiveDrawer
        isOpen={showDrawer}
        onClose={() => setShowDrawer(false)}
        title={`Dialectic Arbitration: ${target_role}`}
        subtitle={`Final Recommendation: ${verdict} (Fit: ${quality_score}%, Trap: ${trap_score}%)`}
        width="wide"
      >
        <div className="space-y-4">
          {/* Executive Rationale */}
          <div className="p-3.5 bg-surface-subtle rounded-xl border border-border-subtle text-xs text-content-secondary leading-relaxed">
            <h4 className="font-semibold text-content-primary mb-1">
              Arbitration Rationale
            </h4>
            <p>{decision_rationale}</p>
          </div>

          {/* Side-by-Side Adversarial Panels */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {/* Prosecutor Traps */}
            <div className="p-3.5 rounded-xl border border-rose-200 bg-rose-50/50 space-y-2">
              <div className="flex items-center gap-1.5 font-bold text-rose-900">
                <ShieldAlert className="h-4 w-4 text-rose-600" />
                <span>Prosecutor Traps & Dealbreakers</span>
              </div>
              {dealbreakers.length > 0 ? (
                <ul className="space-y-1.5 pt-1">
                  {dealbreakers.map((db, idx) => (
                    <li key={idx} className="flex items-start gap-1.5 text-rose-800">
                      <AlertTriangle className="h-3.5 w-3.5 text-rose-600 shrink-0 mt-0.5" />
                      <span>{db}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-rose-700 italic">No fatal dealbreakers identified.</p>
              )}
            </div>

            {/* Advocate Levers */}
            <div className="p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/50 space-y-2">
              <div className="flex items-center gap-1.5 font-bold text-emerald-900">
                <TrendingUp className="h-4 w-4 text-emerald-600" />
                <span>Advocate Value Levers & Moat</span>
              </div>
              {advocate_points.length > 0 ? (
                <ul className="space-y-1.5 pt-1">
                  {advocate_points.map((pt, idx) => (
                    <li key={idx} className="flex items-start gap-1.5 text-emerald-800">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{pt}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-emerald-700 italic">Alignment standard.</p>
              )}
            </div>
          </div>

          {/* Outbound Strategy & Pitch */}
          <div className="p-4 rounded-xl border border-border-subtle bg-surface space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-content-primary flex items-center gap-1.5">
                <Mail className="h-4 w-4 text-accent" />
                <span>Pre-Drafted Recruiter Response</span>
              </span>
              <button
                type="button"
                onClick={handleCopyPitch}
                className="text-xs font-medium text-accent hover:text-accent-hover inline-flex items-center gap-1"
              >
                {pitchCopied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
                <span>{pitchCopied ? "Copied" : "Copy Response"}</span>
              </button>
            </div>

            <textarea
              readOnly
              rows={4}
              value={effectivePitch}
              className="w-full text-xs font-mono bg-surface-subtle p-3 rounded-lg border border-border-subtle text-content-secondary leading-relaxed resize-none focus:outline-none"
            />

            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-2">
                {jd_id && onActionClick && (
                  <button
                    type="button"
                    onClick={() => {
                      setShowDrawer(false);
                      onActionClick(`/tailor ${jd_id}`);
                    }}
                    className="min-touch-target px-3 py-1.5 rounded-lg border border-border-subtle hover:bg-surface-subtle text-xs font-medium text-content-primary transition-colors"
                  >
                    Compile Tailored CV
                  </button>
                )}
              </div>

              <a
                href={mailtoHref}
                target="_blank"
                rel="noreferrer"
                className="min-touch-target inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-accent text-white text-xs font-semibold hover:bg-accent-hover transition-colors shadow-xs"
              >
                <Mail className="h-3.5 w-3.5" />
                <span>Open in Email Client</span>
              </a>
            </div>
          </div>
        </div>
      </ProgressiveDrawer>
    </>
  );
};

export default DebateVerdictCard;
