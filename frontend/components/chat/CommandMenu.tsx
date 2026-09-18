"use client";

import React from "react";
import { 
  Sparkles, 
  Scale, 
  FileText, 
  Search, 
  HelpCircle, 
  Globe, 
  Briefcase,
  Zap
} from "lucide-react";

export interface SlashCommand {
  cmd: string;
  description: string;
  example: string;
  category: string;
  icon: any;
}

export const CANDIDATE_COMMANDS: SlashCommand[] = [
  {
    cmd: "/evaluate",
    description: "Dual-agent dialectic debate (Prosecutor traps vs Advocate levers)",
    example: "/evaluate JD_34",
    category: "Strategic",
    icon: Scale
  },
  {
    cmd: "/tailor",
    description: "Compile tailored resume to A4 PDF with AI Sanity guardrail",
    example: "/tailor JD_34",
    category: "Resumes",
    icon: FileText
  },
  {
    cmd: "/pipeline",
    description: "Explore all tracked target mandates matching €950/d & remote",
    example: "/pipeline",
    category: "Pipeline",
    icon: Briefcase
  },
  {
    cmd: "/ingest",
    description: "Scrape and register live job posting URL into CRM",
    example: "/ingest https://...",
    category: "Pipeline",
    icon: Globe
  },
  {
    cmd: "/profile",
    description: "Inspect candidate proof telemetry, rate target, and constraints",
    example: "/profile",
    category: "Candidate",
    icon: Sparkles
  },
  {
    cmd: "/help",
    description: "Display command shortcuts and available agentic tools",
    example: "/help",
    category: "System",
    icon: HelpCircle
  },
];

interface CommandMenuProps {
  filterText: string;
  onSelectCommand: (cmd: SlashCommand) => void;
  onClose: () => void;
}

export const CommandMenu: React.FC<CommandMenuProps> = ({
  filterText,
  onSelectCommand,
  onClose
}) => {
  const query = filterText.replace("/", "").toLowerCase();
  const filtered = CANDIDATE_COMMANDS.filter(c => 
    c.cmd.toLowerCase().includes(query) || 
    c.description.toLowerCase().includes(query)
  );

  if (filtered.length === 0) return null;

  return (
    <div className="absolute bottom-full mb-2 left-0 right-0 max-h-64 overflow-y-auto rounded-xl border border-slate-200 bg-white shadow-career-elevated p-2 z-50">
      <div className="px-3 py-1.5 text-[10px] font-mono font-semibold text-indigo-700 uppercase tracking-wider flex items-center justify-between border-b border-slate-100 mb-1">
        <span>Candidate Commands</span>
        <span className="text-slate-400">Press Enter to select</span>
      </div>
      {filtered.map((cmd) => {
        const Icon = cmd.icon;
        return (
          <button
            key={cmd.cmd}
            type="button"
            onClick={() => onSelectCommand(cmd)}
            className="w-full text-left px-3 py-2 rounded-lg hover:bg-slate-50 flex items-center justify-between group transition-colors"
          >
            <div className="flex items-center space-x-2.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-50 text-indigo-600 border border-indigo-200/80 group-hover:bg-indigo-100 transition-colors">
                <Icon className="h-3.5 w-3.5" />
              </div>
              <div>
                <span className="text-xs font-mono font-bold text-slate-900">{cmd.cmd}</span>
                <span className="text-xs text-slate-500 ml-2">{cmd.description}</span>
              </div>
            </div>
            <span className="text-[10px] font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
              {cmd.example}
            </span>
          </button>
        );
      })}
    </div>
  );
};
