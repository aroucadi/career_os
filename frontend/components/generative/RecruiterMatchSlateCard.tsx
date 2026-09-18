"use client";

import React, { useState } from "react";
import { 
  Users, 
  ShieldCheck, 
  CheckCircle2, 
  Lock, 
  Unlock, 
  Sparkles, 
  ChevronRight, 
  AlertCircle,
  Clock,
  Award,
  Send
} from "lucide-react";

interface CandidateItem {
  match_id: string;
  candidate_id: string;
  anonymized_alias: string;
  headline: string;
  seniority: string;
  overall_match_score: number;
  rubric_subscores?: Record<string, number>;
  key_leverage_points?: string[];
  pre_identified_gaps?: string[];
  governance_tags?: string[];
  target_compensation?: Record<string, any>;
  opt_in_status: string;
}

interface RecruiterMatchSlateCardProps {
  job_title: string;
  total_matches: number;
  candidates: CandidateItem[];
}

export default function RecruiterMatchSlateCard({
  job_title,
  total_matches,
  candidates = []
}: RecruiterMatchSlateCardProps) {
  const [items, setItems] = useState<CandidateItem[]>(candidates);
  const [activeDossier, setActiveDossier] = useState<any | null>(null);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const handleRequestIntro = async (matchId: string) => {
    setLoadingId(matchId);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recruiter/request-intro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ match_id: matchId, recruiter_notes: "Strong fit for mandate" })
      });
      if (res.ok) {
        setNotice("Introduction request dispatched to candidate. Awaiting Double Opt-In consent.");
        setItems(prev => prev.map(c => c.match_id === matchId ? { ...c, opt_in_status: "PENDING_CONSENT" } : c));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingId(null);
    }
  };

  const handleSimulateConsent = async (matchId: string) => {
    setLoadingId(matchId);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/candidates/opt-in", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ match_id: matchId, decision: "APPROVE" })
      });
      if (res.ok) {
        const data = await res.json();
        setNotice("Candidate has consented! Executive Dossier & PII unlocked.");
        setItems(prev => prev.map(c => c.match_id === matchId ? { ...c, opt_in_status: "APPROVED" } : c));
        setActiveDossier(data.dossier);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingId(null);
    }
  };

  const handleFetchDossier = async (matchId: string) => {
    setLoadingId(matchId);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/recruiter/dossier/${matchId}`);
      if (res.ok) {
        const data = await res.json();
        setActiveDossier(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="my-4 rounded-xl border border-indigo-200/80 bg-white shadow-md overflow-hidden text-slate-900 font-sans">
      {/* Executive Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-4 sm:p-5">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
          <div className="flex items-center space-x-2.5">
            <div className="h-8 w-8 rounded-lg bg-indigo-500/20 border border-indigo-400/40 flex items-center justify-center text-indigo-300">
              <Users className="h-4 w-4" />
            </div>
            <div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-indigo-300">
                Recruiter Delegation Loop • B2B Requisition Match
              </span>
              <h3 className="text-base font-bold text-white tracking-tight">{job_title}</h3>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-mono font-bold">
              {total_matches || items.length} Pre-Audited Matches
            </span>
          </div>
        </div>

        {/* Double Opt-In Shield Banner */}
        <div className="flex items-center space-x-2 text-xs text-indigo-200 bg-indigo-900/40 border border-indigo-700/50 px-3 py-1.5 rounded-lg">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>
            <strong>EU AI Act Double Opt-In Active:</strong> Candidate PII is cryptographically blurred. Full identity and direct contact details unlock only upon candidate consent.
          </span>
        </div>
      </div>

      {notice && (
        <div className="bg-emerald-50 border-b border-emerald-200 px-4 py-2 text-xs text-emerald-800 font-medium flex items-center justify-between">
          <span>{notice}</span>
          <button onClick={() => setNotice(null)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
        </div>
      )}

      {/* Candidate Slate List */}
      <div className="divide-y divide-slate-100 p-2 sm:p-4 space-y-3">
        {items.map((cand) => {
          const isApproved = cand.opt_in_status === "APPROVED";
          const score = Math.round(cand.overall_match_score);
          const scoreColor = score >= 90 ? "text-emerald-700 bg-emerald-50 border-emerald-300" : "text-indigo-700 bg-indigo-50 border-indigo-300";

          return (
            <div 
              key={cand.match_id}
              className="p-3.5 sm:p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:border-indigo-300 transition shadow-xs"
            >
              <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-slate-900 text-sm">{cand.anonymized_alias}</span>
                    {isApproved ? (
                      <span className="flex items-center space-x-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
                        <Unlock className="w-3 h-3 text-emerald-600" />
                        <span>CONSENTED / UNLOCKED</span>
                      </span>
                    ) : (
                      <span className="flex items-center space-x-1 text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                        <Lock className="w-3 h-3 text-slate-500" />
                        <span>PII BLURRED</span>
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-600 mt-0.5">{cand.headline}</p>
                </div>

                <div className={`px-3 py-1 rounded-lg border font-mono font-bold text-sm ${scoreColor}`}>
                  {score}% Match
                </div>
              </div>

              {/* Subscores */}
              {cand.rubric_subscores && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 my-2.5 font-mono text-[11px]">
                  <div className="bg-white border border-slate-200 rounded p-1.5 text-center">
                    <span className="text-slate-400 block text-[10px]">DOMAIN</span>
                    <span className="font-bold text-slate-800">{Math.round(cand.rubric_subscores.domain || 80)}%</span>
                  </div>
                  <div className="bg-white border border-slate-200 rounded p-1.5 text-center">
                    <span className="text-slate-400 block text-[10px]">GOVERNANCE</span>
                    <span className="font-bold text-slate-800">{Math.round(cand.rubric_subscores.governance || 85)}%</span>
                  </div>
                  <div className="bg-white border border-slate-200 rounded p-1.5 text-center">
                    <span className="text-slate-400 block text-[10px]">SCALE & COE</span>
                    <span className="font-bold text-slate-800">{Math.round(cand.rubric_subscores.scale || 85)}%</span>
                  </div>
                  <div className="bg-white border border-slate-200 rounded p-1.5 text-center">
                    <span className="text-slate-400 block text-[10px]">COMPENSATION</span>
                    <span className="font-bold text-slate-800">{Math.round(cand.rubric_subscores.compensation || 80)}%</span>
                  </div>
                </div>
              )}

              {/* Leverage Points */}
              {cand.key_leverage_points && cand.key_leverage_points.length > 0 && (
                <div className="space-y-1 mb-3">
                  {cand.key_leverage_points.map((lp, idx) => (
                    <div key={idx} className="flex items-start space-x-1.5 text-xs text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{lp}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Governance & Compensation Pills */}
              <div className="flex flex-wrap items-center gap-1.5 mb-3">
                {cand.governance_tags?.map((tag, idx) => (
                  <span key={idx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {tag}
                  </span>
                ))}
                {cand.target_compensation && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    Floor: {cand.target_compensation.freelance_tjm || cand.target_compensation.permanent_salary || cand.target_compensation.monthly_retainer}
                  </span>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/60">
                <span className="text-[11px] text-slate-500 font-mono">
                  Match ID: {cand.match_id}
                </span>

                <div className="flex items-center space-x-2">
                  {!isApproved ? (
                    <>
                      <button
                        onClick={() => handleRequestIntro(cand.match_id)}
                        disabled={loadingId === cand.match_id}
                        className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-xs disabled:opacity-50"
                      >
                        <Send className="w-3 h-3" />
                        <span>Request Warm Intro</span>
                      </button>
                      <button
                        onClick={() => handleSimulateConsent(cand.match_id)}
                        disabled={loadingId === cand.match_id}
                        title="Simulates candidate clicking 'Accept Introduction' in their dashboard"
                        className="px-2.5 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300 font-semibold text-xs transition"
                      >
                        Simulate Consent (Demo)
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleFetchDossier(cand.match_id)}
                      disabled={loadingId === cand.match_id}
                      className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition shadow-xs"
                    >
                      <Unlock className="w-3.5 h-3.5" />
                      <span>View Executive Dossier</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Unlocked Dossier Modal / Drawer */}
      {activeDossier && (
        <div className="border-t-2 border-emerald-500 bg-emerald-50/40 p-4 sm:p-5 text-xs text-slate-800">
          <div className="flex items-center justify-between border-b border-emerald-200 pb-2 mb-3">
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-emerald-600" />
              <h4 className="font-bold text-slate-900 text-sm">
                Executive Dossier (Audit Certainty Package) • {activeDossier.access_status}
              </h4>
            </div>
            <button 
              onClick={() => setActiveDossier(null)}
              className="px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-bold hover:bg-slate-300"
            >
              Close
            </button>
          </div>

          {activeDossier.access_status === "UNLOCKED" ? (
            <div className="space-y-3">
              {/* Unlocked PII */}
              <div className="bg-white p-3 rounded-lg border border-emerald-300 shadow-xs">
                <div className="text-[10px] font-mono uppercase text-emerald-700 font-bold mb-1">
                  Unlocked Contact Information:
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 font-mono text-xs">
                  <div><strong>Name:</strong> {activeDossier.unlocked_full_name}</div>
                  <div><strong>Email:</strong> {activeDossier.unlocked_email}</div>
                  <div><strong>LinkedIn:</strong> <a href={activeDossier.unlocked_linkedin} target="_blank" rel="noreferrer" className="text-indigo-600 underline">Profile Link</a></div>
                </div>
              </div>

              {/* 5-Question Interview Cheatsheet */}
              <div className="bg-white p-3 rounded-lg border border-slate-200">
                <div className="text-[10px] font-mono uppercase text-indigo-700 font-bold mb-2">
                  Tailored Hiring Manager Interview Cheatsheet:
                </div>
                <ul className="space-y-1.5 list-none">
                  {activeDossier.custom_interview_cheatsheet?.map((q: string, idx: number) => (
                    <li key={idx} className="text-slate-700 bg-slate-50 p-2 rounded border border-slate-100">
                      {q}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="bg-amber-50 p-3 rounded-lg border border-amber-300 text-amber-800">
              <AlertCircle className="w-4 h-4 inline mr-1 text-amber-600" />
              Dossier is LOCKED. Awaiting candidate Double Opt-In consent before contact info can be revealed.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
