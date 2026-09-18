"use client";

import React, { useState, useEffect } from "react";
import { 
  Building2, 
  Search, 
  Sparkles, 
  ShieldCheck, 
  Lock, 
  Unlock, 
  CreditCard, 
  ExternalLink, 
  X, 
  CheckCircle2, 
  Layers, 
  ChevronRight,
  TrendingUp,
  AlertCircle
} from "lucide-react";

interface RecruiterPortalModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RecruiterPortalModal: React.FC<RecruiterPortalModalProps> = ({ isOpen, onClose }) => {
  const [jobTitle, setJobTitle] = useState("Head of AI Adoption & Platform Delivery");
  const [company, setCompany] = useState("Tier-1 Financial Group");
  const [minScore, setMinScore] = useState(60);
  const [jdText, setJdText] = useState(
    "Seeking a Senior Director / Lead to scale enterprise AI adoption and operating models across 7 banking squads. Must enforce EU AI Act governance and agentic SDLC pipelines."
  );
  const [isLoading, setIsLoading] = useState(false);
  const [matches, setMatches] = useState<any[]>([]);
  const [creditsBalance, setCreditsBalance] = useState<number>(500);
  const [orgName, setOrgName] = useState("CareerOS Partner Headhunters");
  const [activeDossier, setActiveDossier] = useState<any | null>(null);
  const [notificationMsg, setNotificationMsg] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchBalance();
    }
  }, [isOpen]);

  const fetchBalance = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recruiter/billing/balance?api_key=cr_live_test123");
      if (res.ok) {
        const data = await res.json();
        setCreditsBalance(data.credits_balance);
        setOrgName(data.name);
      }
    } catch {
      // Fallback
    }
  };

  if (!isOpen) return null;

  const handleSearch = async () => {
    setIsLoading(true);
    setNotificationMsg(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recruiter/match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_title: jobTitle,
          company: company,
          jd_text: jdText,
          min_score: minScore
        })
      });
      if (res.ok) {
        const data = await res.json();
        setMatches(data);
        // Refresh balance
        fetchBalance();
      }
    } catch (e: any) {
      setNotificationMsg(`Error querying candidates: ${e.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRequestIntro = async (matchId: string) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recruiter/request-intro", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          match_id: matchId,
          recruiter_notes: `Urgent requisition for ${company}`
        })
      });
      if (res.ok) {
        const data = await res.json();
        setNotificationMsg(`Warm introduction dispatched to candidate! Double Opt-In token issued: ${data.token?.slice(0, 14)}...`);
        // Update local slate item to pending consent
        setMatches((prev) =>
          prev.map((m) => (m.match_id === matchId ? { ...m, opt_in_status: "PENDING_CONSENT" } : m))
        );
        fetchBalance();
      }
    } catch (e: any) {
      setNotificationMsg(`Error requesting introduction: ${e.message}`);
    }
  };

  const handleViewDossier = async (matchId: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/recruiter/dossier/${matchId}`);
      if (res.ok) {
        const data = await res.json();
        setActiveDossier(data);
      }
    } catch (e: any) {
      setNotificationMsg(`Error fetching dossier: ${e.message}`);
    }
  };

  const handleSimulateConsent = async (matchId: string) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recruiter/opt-in", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ match_id: matchId, decision: "APPROVE" })
      });
      if (res.ok) {
        const data = await res.json();
        setMatches((prev) =>
          prev.map((m) => (m.match_id === matchId ? { ...m, opt_in_status: "APPROVED" } : m))
        );
        setActiveDossier(data.dossier);
        setNotificationMsg("Candidate Double Opt-In Consent Simulated! Executive Dossier UNLOCKED.");
      }
    } catch (e: any) {
      setNotificationMsg(`Simulation error: ${e.message}`);
    }
  };

  const handleTopUp = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/recruiter/billing/checkout?pack=growth", {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        // Simulate automatic fulfillment via webhook for testing
        await fetch("http://127.0.0.1:8000/api/recruiter/billing/webhook", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event: "checkout.session.completed",
            org_id: "org_default_test",
            credits_added: 150
          })
        });
        fetchBalance();
        setNotificationMsg("Successfully topped up 150 credits via Stripe Growth Pack!");
      }
    } catch (e: any) {
      setNotificationMsg(`Checkout error: ${e.message}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/65 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="flex flex-col bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-6xl h-[92vh] overflow-hidden">
        {/* Header */}
        <header className="h-16 shrink-0 border-b border-slate-200 bg-white px-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-600 text-white font-bold text-xs shadow-sm">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-slate-900">B2B Recruiter & Executive Search Portal</h3>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                  ENTERPRISE
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Talent Intelligence Lake • Zero-PII Double Opt-In Protocol
              </p>
            </div>
          </div>

          {/* Org & Credits Badge */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 font-mono text-xs">
              <span className="text-slate-500">{orgName}:</span>
              <span className="font-bold text-amber-700">⚡ {creditsBalance} Credits</span>
            </div>

            <button
              onClick={handleTopUp}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
              title="Top-up credits via Stripe"
            >
              <CreditCard className="h-3.5 w-3.5" />
              <span>Top-up Credits</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Main Content Area */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Panel: Requisition Input */}
          <div className="w-1/3 border-r border-slate-200 p-5 overflow-y-auto space-y-4 bg-slate-50/50">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              1. Requisition Intake
            </h4>

            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-slate-600">Job Title / Mandate</label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                className="w-full text-xs font-mono bg-white border border-slate-300 rounded-lg p-2 text-slate-800 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-slate-600">Client / Company Name</label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full text-xs font-mono bg-white border border-slate-300 rounded-lg p-2 text-slate-800 focus:ring-2 focus:ring-amber-500/20 outline-none"
              />
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-[11px] font-semibold text-slate-600">
                <span>Minimum Match Score</span>
                <span className="font-mono text-amber-700 font-bold">{minScore}%</span>
              </div>
              <input
                type="range"
                min={50}
                max={95}
                step={5}
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-full accent-amber-600 cursor-pointer"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-slate-600">Requisition Specifications / JD Text</label>
              <textarea
                rows={6}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                className="w-full text-xs font-mono bg-white border border-slate-300 rounded-lg p-2 text-slate-800 focus:ring-2 focus:ring-amber-500/20 outline-none resize-none leading-relaxed"
              />
            </div>

            <button
              onClick={handleSearch}
              disabled={isLoading || !jobTitle.trim() || !jdText.trim()}
              className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold shadow-xs disabled:opacity-50 transition-all cursor-pointer"
            >
              {isLoading ? (
                <span>Scoring Talent Lake...</span>
              ) : (
                <>
                  <Search className="h-3.5 w-3.5" />
                  <span>Search Talent Lake (10 Credits)</span>
                </>
              )}
            </button>

            {notificationMsg && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 text-xs flex items-start space-x-2">
                <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                <span className="leading-tight">{notificationMsg}</span>
              </div>
            )}
          </div>

          {/* Right Panel: Matches Slate & Dossier View */}
          <div className="flex-1 p-6 overflow-y-auto space-y-5 bg-white">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  2. Calibrated Candidate Slates ({matches.length} Matches Found)
                </h4>
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                GDPR Double Opt-In Protected • Zero PII Leakage
              </span>
            </div>

            {matches.length === 0 ? (
              <div className="h-72 flex flex-col items-center justify-center text-center text-slate-400 space-y-2">
                <Search className="h-10 w-10 text-slate-300" />
                <p className="text-xs font-medium text-slate-500">
                  Enter your requisition details on the left and click "Search Talent Lake".
                </p>
                <p className="text-[11px] text-slate-400 max-w-sm">
                  Our algorithm will decompose mandatory eliminators and rank verified candidates across domain, scale, governance, and compensation.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {matches.map((item) => {
                  const isApproved = item.opt_in_status === "APPROVED";
                  const isPending = item.opt_in_status === "PENDING_CONSENT";

                  return (
                    <div
                      key={item.match_id}
                      className="p-5 rounded-xl border border-slate-200 bg-white hover:border-amber-300 transition-all shadow-xs space-y-3"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <h5 className="text-sm font-bold text-slate-900">
                              {isApproved ? item.candidate_id : item.anonymized_alias}
                            </h5>
                            <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                              isApproved 
                                ? "bg-emerald-50 text-emerald-800 border-emerald-200" 
                                : isPending
                                ? "bg-amber-50 text-amber-800 border-amber-200"
                                : "bg-slate-100 text-slate-700 border-slate-200"
                            }`}>
                              {item.opt_in_status}
                            </span>
                          </div>
                          <p className="text-xs text-slate-600 mt-0.5">{item.headline}</p>
                        </div>

                        <div className="text-right font-mono">
                          <div className="text-lg font-extrabold text-amber-600">
                            {item.overall_match_score?.toFixed(1)}%
                          </div>
                          <div className="text-[10px] text-slate-400 uppercase">Composite Score</div>
                        </div>
                      </div>

                      {/* Subscores Grid */}
                      <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-100 text-center font-mono">
                        <div className="bg-slate-50 p-1.5 rounded border border-slate-200/60">
                          <div className="text-[9px] text-slate-400 uppercase">Domain</div>
                          <div className="text-xs font-bold text-slate-800">{item.rubric_subscores?.domain_fit?.toFixed(0)}%</div>
                        </div>
                        <div className="bg-slate-50 p-1.5 rounded border border-slate-200/60">
                          <div className="text-[9px] text-slate-400 uppercase">Governance</div>
                          <div className="text-xs font-bold text-slate-800">{item.rubric_subscores?.governance_depth?.toFixed(0)}%</div>
                        </div>
                        <div className="bg-slate-50 p-1.5 rounded border border-slate-200/60">
                          <div className="text-[9px] text-slate-400 uppercase">Scale</div>
                          <div className="text-xs font-bold text-slate-800">{item.rubric_subscores?.scale_telemetry?.toFixed(0)}%</div>
                        </div>
                        <div className="bg-slate-50 p-1.5 rounded border border-slate-200/60">
                          <div className="text-[9px] text-slate-400 uppercase">Comp</div>
                          <div className="text-xs font-bold text-slate-800">{item.rubric_subscores?.compensation_alignment?.toFixed(0)}%</div>
                        </div>
                      </div>

                      {/* Leverage Points */}
                      {item.key_leverage_points && item.key_leverage_points.length > 0 && (
                        <div className="text-xs text-slate-600 space-y-1">
                          <div className="text-[10px] font-bold uppercase text-slate-400">Verified Evidence:</div>
                          <ul className="list-disc list-inside space-y-0.5 text-[11px] text-slate-700">
                            {item.key_leverage_points.map((pt: string, idx: number) => (
                              <li key={idx} className="truncate">{pt}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recruiter Actions */}
                      <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                        <div className="flex items-center space-x-2">
                          {!isApproved && (
                            <button
                              onClick={() => handleRequestIntro(item.match_id)}
                              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
                            >
                              <span>Request Warm Intro</span>
                            </button>
                          )}

                          <button
                            onClick={() => handleViewDossier(item.match_id)}
                            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium transition-colors"
                          >
                            {isApproved ? <Unlock className="h-3.5 w-3.5 text-emerald-600" /> : <Lock className="h-3.5 w-3.5 text-slate-400" />}
                            <span>{isApproved ? "View Full Executive Dossier" : "View Redacted Dossier"}</span>
                          </button>
                        </div>

                        {/* Demo simulator */}
                        {!isApproved && (
                          <button
                            onClick={() => handleSimulateConsent(item.match_id)}
                            className="text-[10px] font-mono text-slate-400 hover:text-indigo-600 underline"
                          >
                            Simulate Candidate Consent
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Active Dossier Drawer */}
            {activeDossier && (
              <div className="mt-6 p-5 rounded-xl border border-indigo-200 bg-indigo-50/40 space-y-4 animate-in fade-in duration-200">
                <div className="flex items-center justify-between border-b border-indigo-200/80 pb-3">
                  <div className="flex items-center space-x-2">
                    <ShieldCheck className="h-5 w-5 text-indigo-600" />
                    <h5 className="text-sm font-bold text-slate-900">
                      Executive Dossier: {activeDossier.access_status === "UNLOCKED" ? activeDossier.unlocked_full_name : activeDossier.anonymized_alias}
                    </h5>
                  </div>
                  <button onClick={() => setActiveDossier(null)} className="text-slate-400 hover:text-slate-700">
                    <X className="h-4 w-4" />
                  </button>
                </div>

                {activeDossier.access_status === "UNLOCKED" ? (
                  <div className="bg-white p-4 rounded-lg border border-emerald-200 space-y-2 text-xs">
                    <div className="font-bold text-emerald-800 flex items-center space-x-1.5">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                      <span>Candidate Identity & Contact Telemetry (UNLOCKED)</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 pt-1">
                      <div>Email: <strong className="font-mono text-slate-900">{activeDossier.unlocked_email || "alaa.roucadi@gmail.com"}</strong></div>
                      <div>Phone: <strong className="font-mono text-slate-900">{activeDossier.unlocked_phone || "+33 6 12 34 56 78"}</strong></div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white p-3 rounded-lg border border-slate-200 text-xs text-slate-500 flex items-center space-x-2">
                    <Lock className="h-4 w-4 text-slate-400" />
                    <span>Contact information blurred until candidate grants Double Opt-In consent.</span>
                  </div>
                )}

                {/* 5-Question Interview Cheatsheet */}
                {activeDossier.hiring_manager_interview_cheatsheet && (
                  <div className="bg-white p-4 rounded-lg border border-indigo-200/80 space-y-2 text-xs">
                    <h6 className="font-bold text-slate-900 text-xs uppercase tracking-wider">
                      Hiring Manager 5-Question Technical Cheatsheet:
                    </h6>
                    <ol className="list-decimal list-inside space-y-1.5 text-slate-700 text-[11px] leading-relaxed">
                      {activeDossier.hiring_manager_interview_cheatsheet.map((q: string, idx: number) => (
                        <li key={idx}>{q}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterPortalModal;
