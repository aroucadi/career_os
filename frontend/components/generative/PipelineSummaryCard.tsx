"use client";

import React, { useState } from "react";
import { 
  Briefcase, 
  ChevronRight, 
  MapPin, 
  Euro, 
  Zap, 
  Scale, 
  CheckCircle2, 
  Clock, 
  XCircle,
  Filter,
  Building2,
  Sparkles,
  TrendingUp,
  Layers
} from "lucide-react";

export interface PipelineItem {
  id: string;
  job_title: string;
  company: string;
  tjm_target_eur?: number;
  location?: string;
  fit_score?: number;
  stage?: string;
}

export interface PipelineSummaryCardProps {
  total_count?: number;
  opportunities?: PipelineItem[];
  stages?: Record<string, PipelineItem[]>;
  career_mode?: string;
  onActionClick?: (command: string) => void;
}

const STAGE_LABELS: Record<string, Record<string, string>> = {
  freelance: {
    ALL: "All Mandates",
    DISCOVERED: "Discovered",
    QUALIFIED: "Qualified",
    PITCH_READY: "Pitch Ready",
    INTERVIEWING: "Negotiating",
    OFFERED: "Won",
    REJECTED: "Declined"
  },
  employee: {
    ALL: "All Applications",
    DISCOVERED: "Target Wishlist",
    QUALIFIED: "Matched Roles",
    PITCH_READY: "Ready to Apply",
    INTERVIEWING: "Interviews Active",
    OFFERED: "Offers Received",
    REJECTED: "Archived"
  },
  fulltime_cdi: {
    ALL: "All Applications",
    DISCOVERED: "Target Wishlist",
    QUALIFIED: "Matched Roles",
    PITCH_READY: "Ready to Apply",
    INTERVIEWING: "Interviews Active",
    OFFERED: "Offers Received",
    REJECTED: "Archived"
  },
  fractional: {
    ALL: "All Portfolio Leads",
    DISCOVERED: "Advisory Leads",
    QUALIFIED: "Vetted Scope",
    PITCH_READY: "Proposal Ready",
    INTERVIEWING: "Discovery Calls",
    OFFERED: "Retainer Signed",
    REJECTED: "Declined"
  },
  student: {
    ALL: "All Opportunities",
    DISCOVERED: "Explored Roles",
    QUALIFIED: "Skill Matched",
    PITCH_READY: "Portfolio Ready",
    INTERVIEWING: "Tech Screenings",
    OFFERED: "Job Offers",
    REJECTED: "Archived"
  },
  pivot: {
    ALL: "All Target Roles",
    DISCOVERED: "Bridge Leads",
    QUALIFIED: "Skills Aligned",
    PITCH_READY: "Pitch Ready",
    INTERVIEWING: "Hiring Screen",
    OFFERED: "Placement",
    REJECTED: "Passed"
  }
};

export const PipelineSummaryCard: React.FC<PipelineSummaryCardProps> = ({
  total_count = 0,
  opportunities = [],
  stages = {},
  career_mode = "freelance",
  onActionClick
}) => {
  const [selectedStage, setSelectedStage] = useState<string>("ALL");

  const modeKey = career_mode.toLowerCase();
  const stageLabels = STAGE_LABELS[modeKey] || STAGE_LABELS.freelance;

  const getStageLabel = (stageKey: string) => {
    return stageLabels[stageKey.toUpperCase()] || stageKey;
  };

  const getModeMeta = () => {
    switch (modeKey) {
      case "employee":
      case "fulltime_cdi":
        return {
          crmTitle: "Executive Career & Applications CRM",
          countSuffix: "Applications",
          badge1Label: "Target Base",
          badge1Val: "€115k - €135k",
          badge2Label: "Work Mode",
          badge2Val: "Hybrid / Remote",
          Icon: Building2,
          iconBg: "bg-emerald-50 text-emerald-600 border-emerald-200"
        };
      case "fractional":
        return {
          crmTitle: "Fractional Advisory Portfolio CRM",
          countSuffix: "Advisory Mandates",
          badge1Label: "Target Retainer",
          badge1Val: "€4,200/mo",
          badge2Label: "Commitment",
          badge2Val: "1-2 Days / Wk",
          Icon: Layers,
          iconBg: "bg-purple-50 text-purple-600 border-purple-200"
        };
      case "student":
        return {
          crmTitle: "Early Career & Placement CRM",
          countSuffix: "Opportunities",
          badge1Label: "Target Salary",
          badge1Val: "€48k - €55k",
          badge2Label: "Readiness",
          badge2Val: "High Velocity",
          Icon: Sparkles,
          iconBg: "bg-amber-50 text-amber-600 border-amber-200"
        };
      case "pivot":
      case "career_pivot":
        return {
          crmTitle: "Strategic Career Pivot CRM",
          countSuffix: "Target Roles",
          badge1Label: "Bridge Focus",
          badge1Val: "AI Operating Model",
          badge2Label: "Transfer Match",
          badge2Val: "92% Fit",
          Icon: TrendingUp,
          iconBg: "bg-teal-50 text-teal-600 border-teal-200"
        };
      default:
        return {
          crmTitle: "Freelance Mandates CRM",
          countSuffix: "Mandates",
          badge1Label: "TJM Anchor",
          badge1Val: "€950/d",
          badge2Label: "Remote Req",
          badge2Val: "100%",
          Icon: Briefcase,
          iconBg: "bg-blue-50 text-blue-600 border-blue-200"
        };
    }
  };

  const meta = getModeMeta();
  const ModeIcon = meta.Icon;

  const allItems: PipelineItem[] = opportunities.length > 0 
    ? opportunities 
    : Object.entries(stages).flatMap(([stageName, items]) => 
        items.map(it => ({ ...it, stage: it.stage || stageName }))
      );

  const stageKeys = ["ALL", ...Array.from(new Set(allItems.map(i => i.stage || "TRIAGED")))];

  const filteredItems = selectedStage === "ALL" 
    ? allItems 
    : allItems.filter(i => (i.stage || "TRIAGED").toUpperCase() === selectedStage.toUpperCase());

  const getStageBadgeStyle = (stage: string = "TRIAGED") => {
    switch (stage.toUpperCase()) {
      case "TRIAGED":
      case "DISCOVERED":
        return "bg-indigo-50 text-indigo-700 border-indigo-200";
      case "PITCHED":
      case "PITCH_READY":
      case "QUALIFIED":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "INTERVIEWING":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "OFFERED":
      case "WON":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "REJECTED":
        return "bg-rose-50 text-rose-700 border-rose-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  const formatRate = (tjm?: number) => {
    if (!tjm) return null;
    switch (modeKey) {
      case "employee":
      case "fulltime_cdi":
        return `${Math.round(tjm * 125)} €/an`;
      case "fractional":
        return `${Math.round(tjm * 4)} €/mois`;
      case "student":
        return `€48k - €55k`;
      case "pivot":
      case "career_pivot":
        return `${tjm} €/j | ${Math.round(tjm * 120)} €/an`;
      default:
        return `${tjm} €/j`;
    }
  };

  return (
    <div className="my-4 rounded-xl border border-slate-200 bg-white p-5 shadow-career-card">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-lg border ${meta.iconBg}`}>
            <ModeIcon className="h-5 w-5" />
          </div>
          <div>
            <div className="text-[10px] font-mono font-semibold text-slate-400 uppercase tracking-wider">
              {meta.crmTitle}
            </div>
            <h4 className="text-base font-bold text-slate-900 flex items-center space-x-2 mt-0.5">
              <span>Tracked Opportunities</span>
              <span className="px-2 py-0.5 rounded font-mono text-xs font-bold bg-slate-100 text-slate-800 border border-slate-200">
                {allItems.length} {meta.countSuffix}
              </span>
            </h4>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="text-right">
            <span className="text-slate-400 text-[10px] block uppercase font-semibold">{meta.badge1Label}</span>
            <span className="font-bold text-indigo-600 text-sm">{meta.badge1Val}</span>
          </div>
          <div className="text-right border-l border-slate-200 pl-3">
            <span className="text-slate-400 text-[10px] block uppercase font-semibold">{meta.badge2Label}</span>
            <span className="font-bold text-emerald-600 text-sm">{meta.badge2Val}</span>
          </div>
        </div>
      </div>

      {/* Stage Filter Tabs (Dynamic Hick's Law Taxonomy) */}
      <div className="mt-3.5 flex items-center space-x-1.5 overflow-x-auto no-scrollbar pb-1">
        {stageKeys.map((st) => (
          <button
            key={st}
            onClick={() => setSelectedStage(st)}
            className={`px-3 py-1 rounded-full text-xs font-mono font-medium transition-all shrink-0 cursor-pointer ${
              selectedStage === st
                ? "bg-slate-900 text-white shadow-xs"
                : "bg-slate-100 hover:bg-slate-200/80 text-slate-600"
            }`}
          >
            {getStageLabel(st)} {st !== "ALL" ? `(${allItems.filter(i => (i.stage || "TRIAGED").toUpperCase() === st.toUpperCase()).length})` : `(${allItems.length})`}
          </button>
        ))}
      </div>

      {/* Mandate Cards Grid */}
      <div className="mt-4 space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
        {filteredItems.length > 0 ? (
          filteredItems.map((opp) => (
            <div 
              key={opp.id}
              className="p-3.5 rounded-lg border border-slate-200 hover:border-indigo-300 bg-slate-50/60 hover:bg-white transition-all shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getStageBadgeStyle(opp.stage)}`}>
                    {getStageLabel(opp.stage || "TRIAGED")}
                  </span>
                  <span className="font-mono text-xs text-slate-500 font-semibold">{opp.id}</span>
                </div>
                <div className="text-sm font-bold text-slate-900 leading-snug">
                  {opp.job_title}
                </div>
                <div className="flex items-center space-x-3 text-xs text-slate-500 font-medium">
                  <span className="text-slate-700 font-semibold">{opp.company}</span>
                  {opp.location && (
                    <span className="flex items-center space-x-1">
                      <MapPin className="h-3 w-3 text-slate-400" />
                      <span>{opp.location}</span>
                    </span>
                  )}
                  {opp.tjm_target_eur && (
                    <span className="flex items-center space-x-1 font-mono text-indigo-700 font-semibold">
                      <span>{formatRate(opp.tjm_target_eur)}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* 1-Click Action Buttons for each mandate */}
              <div className="flex items-center space-x-2 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                <button
                  onClick={() => onActionClick?.(`/tailor ${opp.id}`)}
                  className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
                  title="Compile tailored CV for this mandate"
                >
                  <Zap className="h-3 w-3" />
                  <span>Tailor CV</span>
                </button>
                <button
                  onClick={() => onActionClick?.(`/evaluate ${opp.id}`)}
                  className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium shadow-2xs transition-colors cursor-pointer"
                  title="Run dialectic debate for this mandate"
                >
                  <Scale className="h-3 w-3 text-slate-500" />
                  <span>Debate</span>
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="py-8 text-center text-xs text-slate-400 font-mono">
            No opportunities in stage `{getStageLabel(selectedStage)}`.
          </div>
        )}
      </div>
    </div>
  );
};

export default PipelineSummaryCard;
