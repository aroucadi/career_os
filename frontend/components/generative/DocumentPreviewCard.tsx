"use client";

import React, { useState } from "react";
import { FileText, ChevronDown, ChevronRight, Eye, Check } from "lucide-react";

export interface DocumentPreviewCardProps {
  title?: string;
  category?: string;
  content_snippet?: string;
  rate?: string;
  source?: string;
}

export const DocumentPreviewCard: React.FC<DocumentPreviewCardProps> = ({
  title = "Document",
  category = "Job Mandate",
  content_snippet = "",
  rate,
  source
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="my-3 rounded-xl border border-slate-200 bg-white p-4 shadow-career-card">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-600">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <h5 className="text-xs font-bold text-slate-900">{title}</h5>
            <div className="flex items-center space-x-2 text-[11px] text-slate-500 font-mono mt-0.5">
              <span>{category}</span>
              {rate && <span>• <strong className="text-emerald-700 font-semibold">{rate}</strong></span>}
            </div>
          </div>
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-800 transition-colors"
        >
          {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </button>
      </div>

      {expanded && content_snippet && (
        <div className="mt-3 pt-2.5 border-t border-slate-100 text-xs text-slate-700 leading-relaxed font-mono bg-slate-50 p-3 rounded-lg border border-slate-200/80">
          {content_snippet}
        </div>
      )}
    </div>
  );
};

export default DocumentPreviewCard;
