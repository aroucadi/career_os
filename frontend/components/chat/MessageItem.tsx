"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { 
  User, 
  Sparkles, 
  Copy, 
  Check, 
  Terminal, 
  ShieldAlert, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle2,
  Scale
} from "lucide-react";
import TailoredCVCard from "../generative/TailoredCVCard";
import DebateVerdictCard from "../generative/DebateVerdictCard";
import DocumentPreviewCard from "../generative/DocumentPreviewCard";
import PipelineSummaryCard from "../generative/PipelineSummaryCard";
import RecruiterMatchSlateCard from "../generative/RecruiterMatchSlateCard";

interface MessageItemProps {
  message: {
    id: string;
    role: string;
    content: string;
    toolInvocations?: Array<{
      toolCallId: string;
      toolName: string;
      args: any;
    }>;
  };
  career_mode?: string;
  onActionClick?: (command: string) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, career_mode = "freelance", onActionClick }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`py-5 transition-colors ${isUser ? "bg-transparent" : "bg-white/80 border-y border-slate-200/60"}`}>
      <div className="max-w-4xl mx-auto flex items-start space-x-4 px-4 sm:px-6">
        {/* Avatar */}
        <div className="shrink-0 mt-0.5">
          {isUser ? (
            <div className="h-8 w-8 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 shadow-xs">
              <span className="font-mono text-xs font-bold text-slate-800">AR</span>
            </div>
          ) : (
            <div className="h-8 w-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-xs border border-indigo-700/20">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 min-w-0 space-y-2.5">
          {/* Role label & Actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-900 tracking-tight">
                {isUser ? "Alaa Roucadi (Candidate)" : "CareerOS Strategic Agent"}
              </span>
              {!isUser && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold">
                  AUTONOMOUS
                </span>
              )}
            </div>

            {!isUser && message.content && (
              <button
                onClick={handleCopy}
                className="text-slate-400 hover:text-slate-700 p-1.5 rounded-md hover:bg-slate-100 transition-colors text-xs flex items-center space-x-1"
                title="Copy response"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5" />}
              </button>
            )}
          </div>

          {/* Markdown Content */}
          {message.content && (
            <div className="text-sm text-slate-800 leading-relaxed font-sans prose prose-slate max-w-none prose-p:my-2 prose-headings:my-3 prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-code:text-indigo-600 prose-code:bg-slate-100 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Generative UI Components rendered inline seamlessly */}
          {message.toolInvocations && message.toolInvocations.length > 0 && (
            <div className="mt-4 space-y-3">
              {message.toolInvocations.map((inv) => {
                const { toolName, args, toolCallId } = inv;

                if (toolName === "TailoredResumeViewer") {
                  return <TailoredCVCard key={toolCallId} {...args} />;
                }
                if (toolName === "DebateVerdictCard" || toolName === "ArbiterScorecard") {
                  return <DebateVerdictCard key={toolCallId} {...args} onActionClick={onActionClick} />;
                }
                if (toolName === "ProsecutorIndictmentCard") {
                  return (
                    <div key={toolCallId} className="rounded-xl border border-rose-200 bg-rose-50/60 p-4 shadow-xs">
                      <div className="flex items-center justify-between border-b border-rose-200/80 pb-2.5 mb-3">
                        <div className="flex items-center space-x-2 text-rose-900 font-bold text-xs">
                          <ShieldAlert className="h-4 w-4 text-rose-600" />
                          <span>Prosecutor Indictment • Stance: {args.verdict || "SCRUTINIZE"}</span>
                        </div>
                        <div className="text-xs font-mono text-rose-700 font-bold bg-rose-100/80 px-2 py-0.5 rounded border border-rose-200">
                          Trap Score: {args.trap_score ?? 15}%
                        </div>
                      </div>
                      <p className="text-xs text-rose-900 mb-2 leading-relaxed">{args.stance}</p>
                      {args.fatal_dealbreakers && args.fatal_dealbreakers.length > 0 && (
                        <div className="space-y-1">
                          <div className="text-[10px] font-mono uppercase text-rose-700 font-bold">Dealbreakers & Commute Traps:</div>
                          {args.fatal_dealbreakers.map((db: string, idx: number) => (
                            <div key={idx} className="flex items-center space-x-1.5 text-xs text-rose-800">
                              <AlertTriangle className="h-3.5 w-3.5 text-rose-600 shrink-0" />
                              <span>{db}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                }
                if (toolName === "AdvocateDefenseCard") {
                  return (
                    <div key={toolCallId} className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4 shadow-xs">
                      <div className="flex items-center justify-between border-b border-emerald-200/80 pb-2.5 mb-3">
                        <div className="flex items-center space-x-2 text-emerald-900 font-bold text-xs">
                          <TrendingUp className="h-4 w-4 text-emerald-600" />
                          <span>Advocate Defense • Stance: {args.stance || "EXPLOIT_FIT"}</span>
                        </div>
                      </div>
                      <p className="text-xs text-emerald-900 mb-2 leading-relaxed font-medium">{args.strategic_positioning}</p>
                      {args.leverage_points && args.leverage_points.length > 0 && (
                        <div className="space-y-1">
                          <div className="text-[10px] font-mono uppercase text-emerald-700 font-bold">Value Levers & Moat:</div>
                          {args.leverage_points.map((lp: string, idx: number) => (
                            <div key={idx} className="flex items-start space-x-1.5 text-xs text-emerald-800">
                              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                              <span>{lp}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                }
                if (toolName === "DocumentPreview" || toolName === "DocumentIngestionCard") {
                  return <DocumentPreviewCard key={toolCallId} {...args} />;
                }
                if (toolName === "PipelineSummaryCard" || toolName === "PipelineViewer") {
                  return <PipelineSummaryCard key={toolCallId} career_mode={args.career_mode || career_mode} {...args} onActionClick={onActionClick} />;
                }
                if (toolName === "RecruiterMatchSlateCard" || toolName === "CandidateMatchSlate") {
                  return <RecruiterMatchSlateCard key={toolCallId} {...args} />;
                }

                // Fallback tool badge
                return (
                  <div key={toolCallId} className="my-2 rounded-lg bg-slate-50 border border-slate-200 p-3 text-xs font-mono text-slate-600 flex items-center space-x-2">
                    <Terminal className="h-3.5 w-3.5 text-indigo-600" />
                    <span>Tool executed: <strong className="text-slate-900">{toolName}</strong></span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageItem;
