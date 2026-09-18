"use client";

import React, { useState } from "react";
import { 
  AlertTriangle, 
  CheckCircle2, 
  Scale, 
  ChevronDown, 
  ChevronRight,
  ShieldAlert,
  Zap,
  TrendingUp,
  MessageSquare,
  Copy,
  Check,
  FileText,
  SendHorizontal,
  Briefcase,
  Mail,
  ExternalLink,
  AtSign
} from "lucide-react";

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
  const [showPitch, setShowPitch] = useState(false);
  const [showEmailComposer, setShowEmailComposer] = useState(false);
  const [pitchCopied, setPitchCopied] = useState(false);
  const [fullDraftCopied, setFullDraftCopied] = useState(false);
  const [recipientEmail, setRecipientEmail] = useState(recruiter_email);

  const isPositive = verdict.includes("ENGAGE") || verdict.includes("GO") || verdict.includes("TOLERATE");
  const isHardNo = verdict.includes("NO-GO") || verdict.includes("REJECT");

  const effectivePitch = recruiter_pitch || (
    isHardNo
      ? `Bonjour, merci pour votre proposition concernant le rôle de ${target_role}. Après analyse de mes critères d'alignement stratégique (notamment le travail 100% remote et mon seuil tarifaire), cette opportunité ne correspond pas à mes priorités actuelles. Restons en contact pour de futures collaborations adaptées.`
      : `Bonjour, merci pour votre prise de contact. Le périmètre de la mission "${target_role}" correspond étroitement à mes réalisations en pilotage de CoE IA et déploiement de produits à fort impact. Mon cadre d'intervention habituel s'articule en full remote (avec déplacements exécutifs ponctuels si nécessaire) pour un TJM indicatif de 950€ HT. Seriez-vous disponible cette semaine pour un court échange afin d'aborder vos enjeux prioritaires ?`
  );

  const emailSubject = `Candidature / Positionnement Stratégique — ${target_role} — Alaa Eddine Roucadi`;

  const mailtoHref = `mailto:${encodeURIComponent(recipientEmail.trim())}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(effectivePitch)}`;

  const handleCopyPitch = () => {
    navigator.clipboard.writeText(effectivePitch);
    setPitchCopied(true);
    setTimeout(() => setPitchCopied(false), 2000);
  };

  const handleCopyFullDraft = () => {
    const fullDraft = `À : ${recipientEmail || "[Email Recruteur]"}\nObjet : ${emailSubject}\n\n${effectivePitch}`;
    navigator.clipboard.writeText(fullDraft);
    setFullDraftCopied(true);
    setTimeout(() => setFullDraftCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-xl border border-slate-200 bg-white p-5 shadow-career-card">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg border ${
            isHardNo
              ? "bg-rose-50 text-rose-600 border-rose-200"
              : "bg-emerald-50 text-emerald-600 border-emerald-200"
          }`}>
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] font-mono font-semibold text-slate-400 uppercase tracking-wider">
              Strategic Mandate Arbitration
            </div>
            <div className="text-base font-bold text-slate-900 flex items-center space-x-2 mt-0.5">
              <span>Arbitration Verdict:</span>
              <span className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${
                isHardNo
                  ? "bg-rose-50 text-rose-700 border-rose-200"
                  : "bg-emerald-50 text-emerald-700 border-emerald-200"
              }`}>
                {verdict}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="text-right">
            <span className="text-slate-400 text-[10px] block uppercase font-semibold">Candidate Fit</span>
            <span className="font-bold text-emerald-600 text-sm">{quality_score}%</span>
          </div>
          <div className="text-right border-l border-slate-200 pl-4">
            <span className="text-slate-400 text-[10px] block uppercase font-semibold">Trap Score</span>
            <span className="font-bold text-rose-600 text-sm">{trap_score}%</span>
          </div>
        </div>
      </div>

      {/* Rationale */}
      <div className="mt-3.5 text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-slate-200/80">
        <span className="font-bold text-indigo-700 mr-1.5 font-mono text-[10px] uppercase tracking-wide">ARBITER SYNTHESIS:</span>
        {decision_rationale}
      </div>

      {/* Dual Debate Columns */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {/* Advocate Strengths */}
        <div className="p-3.5 rounded-lg bg-emerald-50/40 border border-emerald-200 text-xs">
          <div className="font-bold text-emerald-800 flex items-center space-x-1.5 mb-2.5">
            <TrendingUp className="h-4 w-4 text-emerald-600" />
            <span className="font-mono text-[10px] uppercase tracking-wide">Advocate Value Levers</span>
          </div>
          <ul className="space-y-2 text-emerald-950">
            {advocate_points.length > 0 ? (
              advocate_points.slice(0, 3).map((pt, i) => (
                <li key={i} className="flex items-start space-x-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span className="leading-snug">{pt}</span>
                </li>
              ))
            ) : (
              <li className="text-emerald-700">High strategic match with candidate telemetry.</li>
            )}
          </ul>
        </div>

        {/* Prosecutor Friction / Dealbreakers */}
        <div className="p-3.5 rounded-lg bg-rose-50/40 border border-rose-200 text-xs">
          <div className="font-bold text-rose-800 flex items-center space-x-1.5 mb-2.5">
            <ShieldAlert className="h-4 w-4 text-rose-600" />
            <span className="font-mono text-[10px] uppercase tracking-wide">Prosecutor Traps & Friction</span>
          </div>
          <ul className="space-y-2 text-rose-950">
            {dealbreakers.length > 0 ? (
              dealbreakers.slice(0, 3).map((db, i) => (
                <li key={i} className="flex items-start space-x-2">
                  <AlertTriangle className="h-3.5 w-3.5 text-rose-600 shrink-0 mt-0.5" />
                  <span className="leading-snug">{db}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-500">Zero fatal dealbreaking constraints detected.</li>
            )}
          </ul>
        </div>
      </div>

      {/* Binding Conditions */}
      {binding_conditions.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100 text-xs">
          <span className="font-mono text-[10px] uppercase text-slate-500 font-bold block mb-1.5">
            Non-Negotiable Candidate Conditions:
          </span>
          <div className="flex flex-wrap gap-2">
            {binding_conditions.map((c, i) => (
              <span key={i} className="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-800 text-xs font-mono font-medium">
                ✓ {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Hick's Law 1-Click Action Bar */}
      <div className="mt-4 pt-3.5 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex items-center space-x-2">
          {isPositive ? (
            <button
              onClick={() => onActionClick?.(`/tailor ${jd_id || target_role}`)}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition-all shadow-xs hover:shadow cursor-pointer"
            >
              <Zap className="h-3.5 w-3.5" />
              <span>Compile Tailored CV & PDF</span>
            </button>
          ) : (
            <button
              onClick={() => onActionClick?.(`/archive ${jd_id || target_role}`)}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-rose-50 border border-rose-200 hover:bg-rose-100 text-rose-700 font-semibold text-xs transition-all cursor-pointer"
            >
              <ShieldAlert className="h-3.5 w-3.5 text-rose-600" />
              <span>Archive Mandate (Hard Pass)</span>
            </button>
          )}

          <button
            onClick={() => {
              setShowEmailComposer(!showEmailComposer);
              if (!showEmailComposer) setShowPitch(true);
            }}
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-emerald-50 border border-emerald-300 hover:bg-emerald-100 text-emerald-800 font-medium text-xs transition-all cursor-pointer shadow-2xs"
            title="1-Click Recruiter Email Composer (mailto:)"
          >
            <Mail className="h-3.5 w-3.5 text-emerald-600" />
            <span>Email Recruiter (1-Click)</span>
          </button>

          <button
            onClick={() => setShowPitch(!showPitch)}
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 font-medium text-xs transition-all cursor-pointer"
          >
            <MessageSquare className="h-3.5 w-3.5 text-slate-500" />
            <span>{showPitch ? "Hide Recruiter Pitch" : isHardNo ? "View Decline Pitch" : "Recruiter Counter-Pitch"}</span>
            {showPitch ? <ChevronDown className="h-3.5 w-3.5 text-slate-400" /> : <ChevronRight className="h-3.5 w-3.5 text-slate-400" />}
          </button>

          <button
            onClick={() => onActionClick?.("/pipeline")}
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 font-medium text-xs transition-all cursor-pointer"
            title="View mandate in Freelance Pipeline CRM"
          >
            <Briefcase className="h-3.5 w-3.5 text-blue-600" />
            <span>Pipeline CRM</span>
          </button>
        </div>

        <div className="text-[10px] font-mono text-slate-400">
          Target: <span className="font-bold text-slate-600">{jd_id || target_role}</span>
        </div>
      </div>

      {/* Recruiter Pitch & 1-Click Email Composer Drawer */}
      {(showPitch || showEmailComposer) && (
        <div className="mt-3 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs animate-in fade-in duration-200">
          {/* Recruiter & Mailto Toolbar */}
          <div className="mb-3 p-3 rounded-lg bg-white border border-slate-200 shadow-2xs">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <div className="flex items-center space-x-2">
                <div className="p-1 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <Mail className="h-3.5 w-3.5" />
                </div>
                <div>
                  <span className="font-mono text-[10px] uppercase font-bold text-slate-500">
                    1-Click Executive Recruiter Email
                  </span>
                  {recruiter_name && (
                    <div className="text-xs font-semibold text-slate-800">
                      Target Contact: <span className="text-indigo-600">{recruiter_name}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <a
                  href={mailtoHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition-all shadow-xs hover:shadow cursor-pointer"
                  title="Open default email client with pre-filled subject and pitch"
                >
                  <Mail className="h-3.5 w-3.5" />
                  <span>Launch Mail Client (mailto:)</span>
                  <ExternalLink className="h-3 w-3 opacity-70" />
                </a>

                <button
                  onClick={handleCopyFullDraft}
                  className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 hover:border-slate-300 text-slate-700 text-xs font-medium transition-all cursor-pointer shadow-2xs"
                  title="Copy complete email draft including subject and recipient"
                >
                  {fullDraftCopied ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-emerald-600" />
                      <span className="text-emerald-700 font-bold">Draft Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span>Copy Full Draft</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Recruiter Email Input & Subject Line */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-100 text-[11px]">
              <div className="flex items-center space-x-1.5 bg-slate-50 px-2.5 py-1.5 rounded border border-slate-200">
                <AtSign className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                <input
                  type="email"
                  value={recipientEmail}
                  onChange={(e) => setRecipientEmail(e.target.value)}
                  placeholder="Recruiter email (e.g. dave.scott@welovesalt.com)..."
                  className="bg-transparent text-slate-800 placeholder-slate-400 focus:outline-none w-full font-mono text-[11px]"
                />
              </div>
              <div className="flex items-center space-x-1.5 bg-slate-50 px-2.5 py-1.5 rounded border border-slate-200 text-slate-600 overflow-hidden text-ellipsis whitespace-nowrap font-mono">
                <span className="font-semibold text-slate-400 shrink-0">Subj:</span>
                <span className="truncate" title={emailSubject}>{emailSubject}</span>
              </div>
            </div>
          </div>

          {/* Message Body Header & Quick Copy */}
          <div className="flex items-center justify-between mb-1.5">
            <span className="font-mono text-[10px] uppercase font-bold text-slate-500 flex items-center space-x-1.5">
              <SendHorizontal className="h-3 w-3 text-indigo-600" />
              <span>{isHardNo ? "Strategic Polite Decline Pitch:" : "Battle-Tested Recruiter Outreach Pitch:"}</span>
            </span>
            <button
              onClick={handleCopyPitch}
              className="inline-flex items-center space-x-1 px-2 py-1 rounded bg-white border border-slate-200 hover:border-indigo-400 text-slate-700 hover:text-indigo-600 text-[11px] font-mono transition-all cursor-pointer shadow-2xs"
            >
              {pitchCopied ? (
                <>
                  <Check className="h-3 w-3 text-emerald-600" />
                  <span className="text-emerald-700 font-bold">Body Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>Copy Body Only</span>
                </>
              )}
            </button>
          </div>

          <p className="text-slate-800 leading-relaxed font-sans bg-white p-3 rounded-lg border border-slate-200/80 whitespace-pre-wrap selection:bg-indigo-100">
            {effectivePitch}
          </p>
        </div>
      )}
    </div>
  );
};

export default DebateVerdictCard;
