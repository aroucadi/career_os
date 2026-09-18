"use client";

import React, { useState, useEffect } from "react";
import { Zap, Info, PlusCircle, CheckCircle } from "lucide-react";

interface TokenBalance {
  user_id: string;
  balance_credits: number;
  max_credits: number;
  total_consumed: number;
  cost_matrix: Record<string, number>;
}

export function EnergyCreditBadge({ userId = "alaa_roucadi" }: { userId?: string }) {
  const [balance, setBalance] = useState<TokenBalance | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const [isClaiming, setIsClaiming] = useState(false);
  const [claimedNotice, setClaimedNotice] = useState<string | null>(null);

  const fetchBalance = async () => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/tokens/balance?user_id=${userId}`);
      if (res.ok) {
        const data = await res.json();
        setBalance(data);
      }
    } catch {
      // Offline fallback
      setBalance({
        user_id: userId,
        balance_credits: 100,
        max_credits: 100,
        total_consumed: 0,
        cost_matrix: {
          deterministic_check: 0,
          fast_heuristic_debate: 5,
          radar_scan: 5,
          deep_llm_debate: 20,
          tailor_resume: 25,
        }
      });
    }
  };

  useEffect(() => {
    fetchBalance();
    const interval = setInterval(fetchBalance, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, [userId]);

  const handleClaim = async () => {
    setIsClaiming(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/tokens/claim-daily?user_id=${userId}`, {
        method: "POST"
      });
      if (res.ok) {
        const data = await res.json();
        setClaimedNotice("+10 EC Claimed!");
        await fetchBalance();
        setTimeout(() => setClaimedNotice(null), 3000);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsClaiming(false);
    }
  };

  const current = balance?.balance_credits ?? 100;
  const max = balance?.max_credits ?? 100;
  const isLow = current <= 20;

  return (
    <div className="relative">
      <button
        onClick={() => setShowTooltip(!showTooltip)}
        onMouseEnter={() => setShowTooltip(true)}
        className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono transition-all shadow-xs ${
          isLow
            ? "bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100"
            : "bg-emerald-50/80 text-emerald-800 border-emerald-200 hover:bg-emerald-100"
        }`}
        title="Energy Credits compute balance"
      >
        <Zap className={`w-3.5 h-3.5 ${isLow ? "text-amber-600 animate-pulse" : "text-emerald-600"}`} />
        <span className="font-bold">{current}</span>
        <span className="text-slate-400">/{max}</span>
        <span className="text-[10px] font-semibold tracking-tight text-slate-500">EC</span>
      </button>

      {/* Tooltip Card */}
      {showTooltip && (
        <div
          onMouseLeave={() => setShowTooltip(false)}
          className="absolute right-0 mt-2 w-72 bg-white rounded-xl border border-slate-200 p-3.5 shadow-xl z-50 text-xs text-slate-800 font-sans"
        >
          <div className="flex items-center justify-between pb-2 border-b border-slate-100 mb-2">
            <div className="flex items-center space-x-1.5">
              <Zap className="w-4 h-4 text-emerald-600" />
              <span className="font-bold text-slate-900">Energy Credits (Anti-Burn)</span>
            </div>
            <span className="font-mono text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              {current} EC
            </span>
          </div>

          <p className="text-[11px] text-slate-500 mb-3 leading-relaxed">
            Guarantees free candidate utility while protecting LLM compute bandwidth. Deterministic analysis is always free.
          </p>

          <div className="space-y-1.5 mb-3 bg-slate-50 p-2.5 rounded-lg border border-slate-100 font-mono text-[11px]">
            <div className="flex justify-between text-slate-600">
              <span>Deterministic / ATS Check</span>
              <span className="font-bold text-emerald-600">0 EC (FREE)</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Fast Heuristic Debate</span>
              <span className="font-bold text-slate-800">5 EC</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Radar Market Scan</span>
              <span className="font-bold text-slate-800">5 EC</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Tailor CV & 1-Page PDF</span>
              <span className="font-bold text-slate-800">25 EC</span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] text-slate-500 flex items-center gap-1">
              <Info className="w-3 h-3 text-slate-400" /> Resets monthly
            </span>
            <button
              onClick={handleClaim}
              disabled={isClaiming}
              className="flex items-center space-x-1 px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-[11px] transition shadow-xs disabled:opacity-50"
            >
              {claimedNotice ? (
                <>
                  <CheckCircle className="w-3 h-3 text-emerald-300" />
                  <span>{claimedNotice}</span>
                </>
              ) : (
                <>
                  <PlusCircle className="w-3 h-3" />
                  <span>{isClaiming ? "Claiming..." : "+10 Daily Check-In"}</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
