"use client";

import React, { useState } from "react";
import { 
  ShieldCheck, 
  X, 
  Linkedin, 
  Mail, 
  CheckCircle2, 
  ArrowRight, 
  Lock,
  Sparkles,
  ExternalLink
} from "lucide-react";
import { StoredCV } from "@/lib/session";

interface ClaimAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  activeCV: StoredCV | null;
}

export const ClaimAccountModal: React.FC<ClaimAccountModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  activeCV
}) => {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleLinkedInClaim = () => {
    // LinkedIn OAuth claim flow
    // In production, triggers LinkedIn OAuth with state=sessionId
    const clientId = process.env.NEXT_PUBLIC_LINKEDIN_CLIENT_ID || "careeros_auth";
    const redirectUri = typeof window !== "undefined" ? `${window.location.origin}/api/auth/linkedin/callback` : "";
    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&state=${sessionId}&scope=r_liteprofile%20r_emailaddress`;
    
    // For now, simulate claim or open oauth
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
    }, 1200);
  };

  const handleEmailClaim = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes("@")) return;
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
    }, 900);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/65 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="flex flex-col bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-lg max-h-[90vh] overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="h-16 shrink-0 border-b border-slate-200 bg-white px-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xs shadow-sm">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Claim Your CareerOS Account
              </h3>
              <p className="text-xs text-slate-500">
                Preserve your telemetry & debate dossiers across devices
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 overflow-y-auto flex-1">
          {!submitted ? (
            <>
              {/* Session Context Banner */}
              <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-xs">
                <div className="flex items-center justify-between text-slate-600 font-mono text-[11px]">
                  <span>Active Session ID:</span>
                  <span className="font-bold text-indigo-700">{sessionId}</span>
                </div>
                {activeCV && (
                  <div className="flex items-center justify-between text-slate-600 text-[11px]">
                    <span>Linked CV:</span>
                    <span className="font-semibold text-slate-800 truncate max-w-[200px]">
                      {activeCV.filename}
                    </span>
                  </div>
                )}
                <div className="flex items-center space-x-1.5 text-[11px] text-emerald-700 pt-1 border-t border-slate-200/80">
                  <Lock className="h-3 w-3 text-emerald-600 shrink-0" />
                  <span>All your local data, debate records, and ATS scores will be securely synced.</span>
                </div>
              </div>

              {/* 1-Click LinkedIn Claim Button */}
              <div className="space-y-2">
                <button
                  type="button"
                  onClick={handleLinkedInClaim}
                  disabled={isSubmitting}
                  className="w-full flex items-center justify-center space-x-2.5 px-4 py-3 rounded-xl bg-[#0077B5] hover:bg-[#006097] text-white text-xs font-bold transition-all shadow-sm cursor-pointer disabled:opacity-50"
                >
                  <Linkedin className="h-4 w-4 fill-current" />
                  <span>{isSubmitting ? "Connecting to LinkedIn..." : "Continue with LinkedIn (1-Click)"}</span>
                </button>
                <p className="text-[10px] text-center text-slate-500">
                  Instant verification. We never post anything to your LinkedIn profile.
                </p>
              </div>

              {/* Divider */}
              <div className="flex items-center space-x-3 my-2">
                <div className="flex-1 h-px bg-slate-200"></div>
                <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">or with email</span>
                <div className="flex-1 h-px bg-slate-200"></div>
              </div>

              {/* Email Magic Link Form */}
              <form onSubmit={handleEmailClaim} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-700">Work or Personal Email</label>
                  <div className="relative">
                    <Mail className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="email"
                      required
                      placeholder="name@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full text-xs bg-white border border-slate-300 rounded-lg pl-9 pr-3 py-2.5 text-slate-800 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting || !email}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-colors disabled:opacity-50 cursor-pointer"
                >
                  <span>Send Magic Link to Claim</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </form>
            </>
          ) : (
            /* Success confirmation */
            <div className="py-6 space-y-4 text-center animate-in fade-in duration-300">
              <div className="h-12 w-12 rounded-full bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center">
                <CheckCircle2 className="h-7 w-7" />
              </div>
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-slate-900">
                  Account Claim Link Generated!
                </h4>
                <p className="text-xs text-slate-600 max-w-sm mx-auto">
                  Your session <strong>{sessionId}</strong> is securely mapped. When you log in from any device, your custom CV telemetry and debate transcripts will be ready.
                </p>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
                >
                  Return to CareerOS Studio
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="h-12 shrink-0 border-t border-slate-200 bg-slate-50 px-6 flex items-center justify-between text-[11px] text-slate-500">
          <span>CareerOS Local-First Studio</span>
          <span>Zero third-party trackers</span>
        </div>
      </div>
    </div>
  );
};

export default ClaimAccountModal;
