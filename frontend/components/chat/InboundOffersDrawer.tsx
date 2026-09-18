"use client";

import React, { useState, useEffect } from "react";
import { Mail, CheckCircle2, XCircle, Shield, Clock, ExternalLink, X } from "lucide-react";

interface InboundRequest {
  token: string;
  match_id: string;
  status: string;
  job_title: string;
  match_score: number;
  expires_at: string;
  created_at: string;
}

export function InboundOffersDrawer({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [requests, setRequests] = useState<InboundRequest[]>([]);
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const fetchInbound = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/candidates/inbound");
      if (res.ok) {
        const data = await res.json();
        setRequests(data);
      }
    } catch {
      // Mock fallback if offline
      setRequests([]);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchInbound();
    }
  }, [isOpen]);

  const handleDecision = async (token: string, decision: "APPROVE" | "DECLINE") => {
    setLoadingId(token);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/candidates/consent-submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, decision })
      });
      if (res.ok) {
        const data = await res.json();
        setNotice(decision === "APPROVE" ? "✓ Introduction Approved! Your contact info was safely shared." : "Introduction declined.");
        await fetchInbound();
        setTimeout(() => setNotice(null), 3500);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col font-sans border-l border-slate-200">
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-100 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Mail className="w-5 h-5 text-indigo-400" />
            <div>
              <h3 className="font-bold text-sm text-white leading-tight">Inbound Headhunter Offers</h3>
              <p className="text-[11px] text-indigo-300">Double Opt-In Consent Portal</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 text-slate-300 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {notice && (
          <div className="bg-emerald-50 border-b border-emerald-200 px-4 py-2 text-xs text-emerald-800 font-medium">
            {notice}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <div className="flex items-center space-x-2 p-3 rounded-lg bg-indigo-50/80 border border-indigo-200 text-xs text-indigo-900">
            <Shield className="w-4 h-4 text-indigo-600 shrink-0" />
            <span>
              <strong>GDPR Shield:</strong> Recruiters only see your anonymized score until you grant consent.
            </span>
          </div>

          {requests.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              <Mail className="w-8 h-8 mx-auto mb-2 text-slate-300 stroke-1" />
              <p className="font-medium text-slate-600">No pending inbound requests</p>
              <p className="text-[11px] mt-1 text-slate-400">When an enterprise matches your profile, it will appear here.</p>
            </div>
          ) : (
            requests.map((req) => {
              const isApproved = req.status === "APPROVED";
              const isDeclined = req.status === "DECLINED";

              return (
                <div 
                  key={req.token}
                  className="p-3.5 rounded-xl border border-slate-200 bg-white hover:border-indigo-300 transition shadow-xs"
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <h4 className="font-bold text-slate-900 text-xs leading-snug">{req.job_title}</h4>
                      <span className="text-[10px] font-mono text-slate-400">Match ID: {req.match_id}</span>
                    </div>
                    <span className="px-2 py-0.5 rounded font-mono font-bold text-xs bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {Math.round(req.match_score)}%
                    </span>
                  </div>

                  <div className="flex items-center space-x-2 text-[11px] text-slate-500 font-mono mb-3">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>Expires in 7 days</span>
                  </div>

                  {/* Actions */}
                  {req.status === "PENDING" ? (
                    <div className="flex items-center space-x-2 pt-2 border-t border-slate-100">
                      <button
                        onClick={() => handleDecision(req.token, "APPROVE")}
                        disabled={loadingId === req.token}
                        className="flex-1 flex items-center justify-center space-x-1 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-xs disabled:opacity-50"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Accept Intro</span>
                      </button>
                      <button
                        onClick={() => handleDecision(req.token, "DECLINE")}
                        disabled={loadingId === req.token}
                        className="flex-1 flex items-center justify-center space-x-1 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition disabled:opacity-50"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Decline</span>
                      </button>
                    </div>
                  ) : (
                    <div className="pt-2 border-t border-slate-100 text-center font-mono text-[11px]">
                      {isApproved && (
                        <span className="text-emerald-700 font-semibold">✓ Introduction Approved</span>
                      )}
                      {isDeclined && (
                        <span className="text-slate-400">✕ Introduction Declined</span>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
