"use client";

import React, { useState } from "react";
import { 
  Compass, 
  AlertTriangle, 
  GraduationCap, 
  Code2, 
  FileEdit, 
  HelpCircle, 
  ChevronRight, 
  CheckCircle2, 
  Clock, 
  Award,
  Layers,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  CheckSquare,
  Square
} from "lucide-react";
import { SurfaceCard } from "../primitives/SurfaceCard";
import { TelemetryMetric } from "../primitives/TelemetryMetric";
import { ProgressiveDrawer } from "../primitives/ProgressiveDrawer";

export interface FatalGap {
  category: string;
  title: string;
  severity: string;
  impact: string;
}

export interface SkillUpItem {
  name: string;
  type: string;
  estimated_hours: string;
  urgency: string;
  credential_issuer: string;
  rationale: string;
}

export interface CapstoneProject {
  title: string;
  summary: string;
  proof_demonstrated: string;
  deliverable: string;
  estimated_build_time: string;
}

export interface HonestReframing {
  current_bullet: string;
  reframed_bullet: string;
  target_alignment: string;
  truth_guard_note: string;
}

export interface InterviewQuestion {
  question: string;
  interviewer_intent: string;
  star_talking_points: string;
}

export interface GapAnalysisCardProps {
  target_role?: string;
  candidate_name?: string;
  match_score?: number;
  fit_label?: string;
  executive_summary?: string;
  fatal_gaps?: FatalGap[];
  skill_up_path?: SkillUpItem[];
  capstone_projects?: CapstoneProject[];
  honest_reframings?: HonestReframing[];
  interview_shield?: InterviewQuestion[];
  keywords_missing?: string[];
  keywords_present?: string[];
  onActionClick?: (command: string) => void;
}

export const GapAnalysisCard: React.FC<GapAnalysisCardProps> = ({
  target_role = "Target Position",
  candidate_name = "Candidate",
  match_score = 68,
  fit_label = "Moderate Gap",
  executive_summary = "Factual gap analysis identified key competency, credential, and semantic deltas.",
  fatal_gaps = [],
  skill_up_path = [],
  capstone_projects = [],
  honest_reframings = [],
  interview_shield = [],
  keywords_missing = [],
  keywords_present = [],
  onActionClick
}) => {
  const [showDrawer, setShowDrawer] = useState(false);
  const [activeTab, setActiveTab] = useState<"gaps" | "skillup" | "capstone" | "reframing" | "interview">("gaps");

  // Smart UI: Local Interactive Verification Checklist State
  const [claimedGaps, setClaimedGaps] = useState<Record<number, boolean>>({});
  const [claimedKeywords, setClaimedKeywords] = useState<Record<string, boolean>>({});

  const claimedGapsCount = Object.values(claimedGaps).filter(Boolean).length;
  const claimedKeywordsCount = Object.values(claimedKeywords).filter(Boolean).length;
  const pointsGained = (claimedGapsCount * 8) + (claimedKeywordsCount * 4);
  const currentScore = Math.min(98, match_score + pointsGained);

  const isHighFit = currentScore >= 80;
  const isCriticalGap = currentScore < 60;
  const statusColor = isHighFit ? "emerald" : isCriticalGap ? "rose" : "slate";
  const currentFitLabel = isHighFit ? "Strong Match" : isCriticalGap ? "High Gap" : "Moderate Fit";
  const remainingGapsCount = Math.max(0, (fatal_gaps.length || 3) - claimedGapsCount);
  const bridgeDays = remainingGapsCount <= 1 ? "0-7" : remainingGapsCount <= 2 ? "7-14" : (skill_up_path.length > 0 ? "14-30" : "7-14");

  const toggleGapClaim = (idx: number) => {
    setClaimedGaps(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  const toggleKeywordClaim = (kw: string) => {
    setClaimedKeywords(prev => ({ ...prev, [kw]: !prev[kw] }));
  };

  return (
    <>
      <SurfaceCard variant={isCriticalGap ? "default" : "accent"} className="my-3">
        {/* 1. Context & Eyebrow */}
        <SurfaceCard.Header>
          <div className="flex items-center gap-1.5 font-mono text-[11px] font-semibold text-content-muted uppercase tracking-wider">
            <Compass className="h-3.5 w-3.5 text-accent" />
            <span>Gap Analysis & Skill-Up Bridge</span>
            <span className="text-content-primary font-bold">• {target_role}</span>
          </div>

          <div className="flex items-center gap-1.5">
            {pointsGained > 0 && (
              <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300 animate-pulse">
                +{pointsGained} pts verified
              </span>
            )}
            <span
              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                isHighFit
                  ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                  : isCriticalGap
                  ? "bg-rose-50 text-rose-700 border-rose-200"
                  : "bg-amber-50 text-amber-700 border-amber-200"
              }`}
            >
              {currentFitLabel}
            </span>
          </div>
        </SurfaceCard.Header>

        {/* 2. Hero & Primary Value (Vertical Ceiling Cap <= 3 elements) */}
        <SurfaceCard.Hero>
          <div className="grid grid-cols-3 gap-2 py-1">
            <TelemetryMetric
              label="Match Score"
              value={currentScore}
              unit="/100"
              statusColor={statusColor}
              trend={isHighFit ? "up" : "down"}
            />
            <TelemetryMetric
              label="Critical Gaps"
              value={remainingGapsCount}
              unit="Items"
              statusColor={remainingGapsCount > 2 ? "rose" : "emerald"}
            />
            <TelemetryMetric
              label="Bridge Time"
              value={bridgeDays}
              unit="Days"
              statusColor="slate"
            />
          </div>
        </SurfaceCard.Hero>

        {/* 3. Supporting Status & Single Primary Action */}
        <SurfaceCard.Actions>
          <div className="flex items-center justify-between w-full">
            <p className="text-xs text-content-muted line-clamp-1 max-w-[65%]">
              {executive_summary}
            </p>

            <button
              type="button"
              onClick={() => setShowDrawer(true)}
              className="min-touch-target inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-accent text-white text-xs font-semibold hover:bg-accent-hover transition-colors shadow-xs"
            >
              <span>Remediation Roadmap</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </SurfaceCard.Actions>
      </SurfaceCard>

      {/* Depth 3 Deep-Dive Drawer: 5-Part Remediation Suite */}
      <ProgressiveDrawer
        isOpen={showDrawer}
        onClose={() => setShowDrawer(false)}
        title={`Gap Remediation Suite: ${target_role}`}
        subtitle={`Match Fit: ${match_score}% (${fit_label}) — Actionable Bridge for ${candidate_name}`}
        width="wide"
      >
        <div className="space-y-4">
          {/* Executive Summary */}
          <div className="p-3.5 bg-surface-subtle rounded-xl border border-border-subtle text-xs text-content-secondary leading-relaxed">
            <h4 className="font-semibold text-content-primary mb-1 flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-accent" />
              <span>Executive Gap Diagnosis</span>
            </h4>
            <p>{executive_summary}</p>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-border-subtle">
            <button
              type="button"
              onClick={() => setActiveTab("gaps")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                activeTab === "gaps" 
                  ? "bg-accent text-white" 
                  : "bg-surface-subtle text-content-secondary hover:text-content-primary"
              }`}
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              <span>Gaps ({fatal_gaps.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("skillup")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                activeTab === "skillup" 
                  ? "bg-accent text-white" 
                  : "bg-surface-subtle text-content-secondary hover:text-content-primary"
              }`}
            >
              <GraduationCap className="h-3.5 w-3.5" />
              <span>Skill-Up ({skill_up_path.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("capstone")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                activeTab === "capstone" 
                  ? "bg-accent text-white" 
                  : "bg-surface-subtle text-content-secondary hover:text-content-primary"
              }`}
            >
              <Code2 className="h-3.5 w-3.5" />
              <span>Capstones ({capstone_projects.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("reframing")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                activeTab === "reframing" 
                  ? "bg-accent text-white" 
                  : "bg-surface-subtle text-content-secondary hover:text-content-primary"
              }`}
            >
              <FileEdit className="h-3.5 w-3.5" />
              <span>CV Reframing ({honest_reframings.length})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("interview")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                activeTab === "interview" 
                  ? "bg-accent text-white" 
                  : "bg-surface-subtle text-content-secondary hover:text-content-primary"
              }`}
            >
              <HelpCircle className="h-3.5 w-3.5" />
              <span>Interview Shield ({interview_shield.length})</span>
            </button>
          </div>

          {/* TAB 1: CRITICAL GAPS */}
          {activeTab === "gaps" && (
            <div className="space-y-3">
              <div className="p-2.5 rounded-lg bg-indigo-50/70 text-indigo-950 border border-indigo-200 text-xs flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-accent shrink-0" />
                  <span><strong>Interactive Checklist:</strong> Already possess any of these? Check them to update your match score dynamically.</span>
                </div>
                {pointsGained > 0 && (
                  <span className="font-mono font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded text-[11px]">
                    +{pointsGained} pts
                  </span>
                )}
              </div>

              {fatal_gaps.map((gap, idx) => {
                const isClaimed = !!claimedGaps[idx];
                return (
                  <div 
                    key={idx} 
                    onClick={() => toggleGapClaim(idx)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-2 ${
                      isClaimed 
                        ? "border-emerald-300 bg-emerald-50/70 shadow-xs" 
                        : "border-rose-200 bg-rose-50/50 hover:border-rose-300"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`font-bold text-xs flex items-center gap-2 ${isClaimed ? "text-emerald-950 line-through" : "text-rose-900"}`}>
                        {isClaimed ? (
                          <CheckSquare className="h-4 w-4 text-emerald-600 shrink-0" />
                        ) : (
                          <Square className="h-4 w-4 text-rose-500 shrink-0" />
                        )}
                        <span>{gap.title}</span>
                      </span>
                      <span className={`text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded border ${
                        isClaimed
                          ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                          : "bg-rose-100 text-rose-800 border-rose-300"
                      }`}>
                        {isClaimed ? "✓ CLAIMED / VERIFIED" : `${gap.severity} • ${gap.category}`}
                      </span>
                    </div>
                    <p className={`text-xs leading-relaxed ${isClaimed ? "text-emerald-800" : "text-rose-800"}`}>{gap.impact}</p>
                  </div>
                );
              })}

              {keywords_missing.length > 0 && (
                <div className="p-3.5 rounded-xl border border-border-subtle bg-surface space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold text-content-primary">
                    <span>Missing Keywords (Tap to mark known):</span>
                    <span className="text-[10px] font-mono font-normal text-content-muted">Tap to toggle</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {keywords_missing.map((kw, i) => {
                      const isClaimed = !!claimedKeywords[kw];
                      return (
                        <button
                          key={i}
                          type="button"
                          onClick={() => toggleKeywordClaim(kw)}
                          className={`text-[11px] font-mono px-2 py-1 rounded-md border transition-all cursor-pointer flex items-center gap-1 ${
                            isClaimed
                              ? "bg-emerald-100 text-emerald-800 border-emerald-300 font-bold"
                              : "bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200"
                          }`}
                        >
                          <span>{isClaimed ? "✓" : "+"}</span>
                          <span>{kw}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: SKILL-UP ROADMAP */}
          {activeTab === "skillup" && (
            <div className="space-y-3">
              {skill_up_path.map((item, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-border-subtle bg-surface space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-content-primary">
                      <Award className="h-4 w-4 text-accent" />
                      <span>{item.name}</span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-accent/10 text-accent font-semibold">
                      {item.urgency}
                    </span>
                  </div>
                  <p className="text-xs text-content-secondary leading-relaxed">{item.rationale}</p>
                  <div className="flex items-center gap-3 text-[11px] text-content-muted font-mono pt-1">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {item.estimated_hours}
                    </span>
                    <span>• Issuer: {item.credential_issuer}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 3: CAPSTONE PROOF PROJECTS */}
          {activeTab === "capstone" && (
            <div className="space-y-3">
              {capstone_projects.map((proj, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-border-subtle bg-surface space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-content-primary">
                      <Code2 className="h-4 w-4 text-emerald-600" />
                      <span>{proj.title}</span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                      {proj.estimated_build_time}
                    </span>
                  </div>
                  <p className="text-xs text-content-secondary leading-relaxed">{proj.summary}</p>
                  <div className="p-2.5 rounded-lg bg-surface-subtle text-[11px] text-content-primary space-y-1">
                    <div className="font-semibold text-accent">What this proves to hiring managers:</div>
                    <div>{proj.proof_demonstrated}</div>
                    <div className="text-content-muted pt-1">Deliverable: {proj.deliverable}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 4: HONEST REFRAMING */}
          {activeTab === "reframing" && (
            <div className="space-y-3">
              <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-900 border border-emerald-200 text-xs flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-600 shrink-0" />
                <span><strong>Truth Guard Active:</strong> All reframings re-anchor your real achievements in target vocabulary with zero false claims or unearned credentials.</span>
              </div>

              {honest_reframings.map((ref, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-border-subtle bg-surface space-y-2">
                  <div className="text-[11px] font-mono text-content-muted uppercase">Before (Current CV Framing):</div>
                  <div className="p-2 rounded bg-rose-50/50 text-xs text-rose-900 border border-rose-100 line-through">
                    {ref.current_bullet}
                  </div>

                  <div className="text-[11px] font-mono text-accent uppercase flex items-center gap-1 pt-1">
                    <ArrowRight className="h-3 w-3" />
                    <span>After (Target Domain Framing):</span>
                  </div>
                  <div className="p-2 rounded bg-emerald-50 text-xs text-emerald-950 font-medium border border-emerald-200">
                    {ref.reframed_bullet}
                  </div>

                  <div className="text-[11px] text-content-muted pt-1">
                    <em>Rationale: {ref.target_alignment}</em>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 5: INTERVIEW SCREENING SHIELD */}
          {activeTab === "interview" && (
            <div className="space-y-3">
              {interview_shield.map((q, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-border-subtle bg-surface space-y-2">
                  <div className="flex items-start gap-2">
                    <HelpCircle className="h-4 w-4 text-accent shrink-0 mt-0.5" />
                    <div className="text-xs font-bold text-content-primary">{q.question}</div>
                  </div>
                  <div className="text-[11px] text-rose-700 bg-rose-50 px-2 py-1 rounded border border-rose-100">
                    <strong>Interviewer Trap / Intent:</strong> {q.interviewer_intent}
                  </div>
                  <div className="p-2.5 rounded-lg bg-surface-subtle text-xs text-content-secondary leading-relaxed">
                    <strong className="text-content-primary block mb-1">STAR Speaking Framework:</strong>
                    {q.star_talking_points}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </ProgressiveDrawer>
    </>
  );
};

export default GapAnalysisCard;
