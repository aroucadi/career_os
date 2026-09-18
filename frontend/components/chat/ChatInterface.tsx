"use client";

import React, { useState, useRef, useEffect } from "react";
import { useChat } from "@ai-sdk/react";
import { 
  Send, 
  Sparkles, 
  Terminal, 
  FileText, 
  Scale, 
  Paperclip, 
  ArrowUp, 
  RotateCcw, 
  Briefcase, 
  Layers, 
  ChevronDown,
  Building2,
  GraduationCap,
  Shuffle
} from "lucide-react";
import MessageItem from "./MessageItem";
import { CommandMenu, CANDIDATE_COMMANDS, SlashCommand } from "./CommandMenu";
import { EnergyCreditBadge } from "./EnergyCreditBadge";
import { InboundOffersDrawer } from "./InboundOffersDrawer";
import { UploadCVModal } from "./UploadCVModal";
import { RecruiterPortalModal } from "../recruiter/RecruiterPortalModal";

export type CareerMode = "freelance" | "employee" | "fractional" | "student" | "pivot";

interface ModeConfig {
  label: string;
  badge1: string;
  badge2: string;
  starters: Array<{
    label: string;
    desc: string;
    cmd: string;
    icon: any;
    color: string;
  }>;
}

const CAREER_MODES: Record<CareerMode, ModeConfig> = {
  freelance: {
    label: "Freelance / Contractor",
    badge1: "100% Remote",
    badge2: "Floor: €950/d",
    starters: [
      {
        label: "Evaluate Mandate #34",
        desc: "Launch dialectic debate: Prosecutor traps vs Advocate value levers for SCC AI Lead.",
        cmd: "/evaluate JD_34",
        icon: Scale,
        color: "text-emerald-700 hover:border-emerald-500"
      },
      {
        label: "Compile Tailored CV & PDF",
        desc: "Synthesize ground-truth A4 PDF with AI content detector sanity guardrail.",
        cmd: "/tailor JD_34",
        icon: FileText,
        color: "text-indigo-700 hover:border-indigo-500"
      },
      {
        label: "Review Mandate Pipeline",
        desc: "Inspect all tracked freelance mandates matching €950/d & 100% remote.",
        cmd: "/pipeline",
        icon: Briefcase,
        color: "text-blue-700 hover:border-blue-500"
      }
    ]
  },
  employee: {
    label: "Full-Time (CDI / Perm)",
    badge1: "Hybrid / Remote",
    badge2: "Target: €115k/yr",
    starters: [
      {
        label: "Multi-JD Gap Analysis",
        desc: "Audit your CV against target market requirements to unlock senior salary bands.",
        cmd: "/gap",
        icon: Layers,
        color: "text-indigo-700 hover:border-indigo-500"
      },
      {
        label: "Evaluate Target Opportunity",
        desc: "Debate permanent compensation, equity, career ladder, and promotion velocity.",
        cmd: "/evaluate JD_30",
        icon: Scale,
        color: "text-emerald-700 hover:border-emerald-500"
      },
      {
        label: "Track Interview Pipeline",
        desc: "Monitor active recruitment stages and salary benchmark offers.",
        cmd: "/pipeline",
        icon: Building2,
        color: "text-blue-700 hover:border-blue-500"
      }
    ]
  },
  fractional: {
    label: "Fractional / Portfolio",
    badge1: "1-2 Days / Week",
    badge2: "Retainer: €1,100/d",
    starters: [
      {
        label: "Audit Fractional Scope",
        desc: "Prosecutor checks for operational trap creep masquerading as strategic advisory.",
        cmd: "/evaluate JD_34",
        icon: Scale,
        color: "text-emerald-700 hover:border-emerald-500"
      },
      {
        label: "Draft Retainer Proposal",
        desc: "Generate an Asynchronous Governance Rider for fractional leadership.",
        cmd: "/tailor JD_34",
        icon: FileText,
        color: "text-indigo-700 hover:border-indigo-500"
      },
      {
        label: "Client Capacity Pipeline",
        desc: "Inspect current multi-client allocation and retainer commitments.",
        cmd: "/pipeline",
        icon: Briefcase,
        color: "text-blue-700 hover:border-blue-500"
      }
    ]
  },
  student: {
    label: "Student / Career Starter",
    badge1: "Top 5% Graduate",
    badge2: "Target: €48k - €55k",
    starters: [
      {
        label: "Extract Project Proof Points",
        desc: "Convert thesis, capstone, and GitHub projects into quantified enterprise metrics.",
        cmd: "/enrich",
        icon: Sparkles,
        color: "text-indigo-700 hover:border-indigo-500"
      },
      {
        label: "Evaluate Graduate Mandate",
        desc: "Audit candidate fit against junior engineering & product mandates.",
        cmd: "/evaluate JD_01",
        icon: Scale,
        color: "text-emerald-700 hover:border-emerald-500"
      },
      {
        label: "Compile 1-Page A4 Resume",
        desc: "Generate clean resume with guaranteed 95%+ human tone AI bypass.",
        cmd: "/tailor JD_01",
        icon: FileText,
        color: "text-emerald-700 hover:border-emerald-500"
      }
    ]
  },
  pivot: {
    label: "Career Pivoter",
    badge1: "Target: AI Lead",
    badge2: "Skill Transfer Mode",
    starters: [
      {
        label: "Extract Leadership Signals",
        desc: "Extract quantifiable accomplishments and management signals from master CV.",
        cmd: "/enrich",
        icon: Sparkles,
        color: "text-indigo-700 hover:border-indigo-500"
      },
      {
        label: "Domain Transfer Gap Report",
        desc: "Map transferable delivery assets to AI operating model requirements.",
        cmd: "/gap",
        icon: Layers,
        color: "text-emerald-700 hover:border-emerald-500"
      },
      {
        label: "Compile Reframed Tailored CV",
        desc: "Reframe past delivery experience into modern agentic architecture.",
        cmd: "/tailor JD_34",
        icon: FileText,
        color: "text-blue-700 hover:border-blue-500"
      }
    ]
  }
};

export const ChatInterface: React.FC = () => {
  const [showCommands, setShowCommands] = useState(false);
  const [showInbound, setShowInbound] = useState(false);
  const [showUploadCV, setShowUploadCV] = useState(false);
  const [showRecruiterPortal, setShowRecruiterPortal] = useState(false);
  const [activeModel, setActiveModel] = useState("gemini-2.5-flash");
  const [careerMode, setCareerMode] = useState<CareerMode>("freelance");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-detect magic-link Double Opt-In token on page load (SPEC-0045)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("consent_token") || params.get("match_id")) {
        setShowInbound(true);
      }
    }
  }, []);

  const activeConfig = CAREER_MODES[careerMode];

  const {
    messages,
    input,
    setInput,
    append,
    isLoading,
    reload,
    setMessages
  } = useChat({
    api: "/api/chat",
    body: {
      profileId: "alaa_roucadi",
      persona: "candidate",
      model: activeModel,
      career_mode: careerMode
    },
    initialMessages: [
      {
        id: "intro-1",
        role: "assistant",
        content: "👋 **Welcome back, Alaa.** I am your Universal CareerOS Strategic Agent.\n\nI am connected to your master profile telemetry, target market JDs, adversarial debates, and headless A4 PDF compiler.\n\nYou can paste any job URL or text, switch career modes above, or use commands like `/tailor JD_34`, `/evaluate JD_34`, or `/pipeline` to drive actions."
      }
    ]
  });

  // Auto scroll to bottom smoothly
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Adjust textarea height automatically
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setInput(val);
    if (val.startsWith("/")) {
      setShowCommands(true);
    } else {
      setShowCommands(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!input.trim() || isLoading) return;
      setShowCommands(false);
      append({ role: "user", content: input.trim() });
      setInput("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleSelectCommand = (cmd: SlashCommand) => {
    setInput(cmd.cmd + " ");
    setShowCommands(false);
    textareaRef.current?.focus();
  };

  const handleQuickAction = (actionText: string) => {
    append({ role: "user", content: actionText });
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50/70 text-slate-900 font-sans">
      {/* Top Executive Header (Stitch MCP Executive Pure Light) */}
      <header className="h-14 shrink-0 border-b border-slate-200 bg-white/95 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between z-20 shadow-xs">
        {/* Left Brand Cluster */}
        <div className="flex items-center space-x-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xs shadow-sm">
            OS
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-sm font-bold text-slate-900 leading-tight tracking-tight">CareerOS 2.0</h1>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200/80">
                UNIVERSAL
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">Strategic Career Agent</p>
          </div>
        </div>

        {/* Center/Right Career Track & Telemetry Cluster */}
        <div className="flex items-center space-x-2.5">
          {/* Universal Career Track Switcher */}
          <div className="flex items-center space-x-1.5 bg-slate-100/90 p-1 rounded-lg border border-slate-200 text-xs font-mono">
            <span className="text-[10px] uppercase text-slate-400 font-bold px-1.5 hidden md:inline">Track:</span>
            <select
              value={careerMode}
              onChange={(e) => setCareerMode(e.target.value as CareerMode)}
              className="bg-white border border-slate-200 rounded-md px-2 py-1 text-slate-800 font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer text-xs"
            >
              <option value="freelance">💼 Freelance / Contractor</option>
              <option value="employee">🏢 Full-Time (CDI / Perm)</option>
              <option value="fractional">🧩 Fractional / Portfolio</option>
              <option value="student">🎓 Student / Graduate</option>
              <option value="pivot">🔄 Career Pivoter</option>
            </select>
          </div>

          {/* Energy Credit Compute Guard (SPEC-0042) */}
          <EnergyCreditBadge userId="alaa_roucadi" />

          {/* Inbound Direct Recruiter Offers Drawer Trigger (SPEC-0042 / SPEC-0043) */}
          <button
            onClick={() => setShowInbound(true)}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-amber-50 hover:bg-amber-100/80 text-amber-800 border border-amber-200/80 text-xs font-mono font-semibold transition-colors cursor-pointer shadow-xs"
            title="Review Inbound Recruiter Introductions (Double Opt-In Gate)"
          >
            <span className="text-sm">📬</span>
            <span className="hidden sm:inline">Inbound</span>
          </button>

          {/* Self-Serve Candidate CV Ingestion (SPEC-0045) */}
          <button
            onClick={() => setShowUploadCV(true)}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 hover:bg-indigo-100/80 text-indigo-700 border border-indigo-200/80 text-xs font-mono font-semibold transition-colors cursor-pointer shadow-xs"
            title="Import Your Candidate CV (.pdf, .docx, text)"
          >
            <span className="text-sm">📄</span>
            <span className="hidden md:inline">Import CV</span>
          </button>

          {/* Dedicated B2B Recruiter Portal (SPEC-0045) */}
          <button
            onClick={() => setShowRecruiterPortal(true)}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200/80 text-slate-800 border border-slate-300 text-xs font-mono font-semibold transition-colors cursor-pointer shadow-xs"
            title="Open B2B Recruiter Requisition Matching Workspace"
          >
            <span className="text-sm">🏢</span>
            <span className="hidden lg:inline">Recruiter Portal</span>
          </button>

          {/* Dynamic Telemetry Pill */}
          <div className="hidden xl:flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-100/80 border border-slate-200 text-xs font-mono">
            <div className="h-5 w-5 rounded-full bg-indigo-600 text-white text-[10px] font-bold flex items-center justify-center">
              AR
            </div>
            <span className="font-semibold text-slate-800">Alaa</span>
            <span className="text-slate-400">•</span>
            <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold border border-emerald-200 text-[11px]">
              {activeConfig.badge1}
            </span>
            <span className="text-slate-400">•</span>
            <span className="text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded font-semibold border border-indigo-200 text-[11px]">
              {activeConfig.badge2}
            </span>
          </div>

          {/* AI Model Selector */}
          <select
            value={activeModel}
            onChange={(e) => setActiveModel(e.target.value)}
            className="text-xs font-mono bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 cursor-pointer shadow-xs"
          >
            <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
            <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
          </select>
        </div>
      </header>

      {/* Main Conversational Stream Area */}
      <main className="flex-1 overflow-y-auto">
        <div className="py-5 space-y-1">
          {messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} career_mode={careerMode} onActionClick={handleQuickAction} />
          ))}

          {/* Hick's Law Primary Action Starters (Dynamic per Career Track) */}
          {messages.length <= 1 && (
            <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-2 pb-6">
              <div className="flex items-center justify-between mb-3">
                <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                  Suggested Actions for {activeConfig.label} (1-Click):
                </div>
                <span className="text-[10px] font-mono text-indigo-600 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded font-medium">
                  {activeConfig.badge2}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {activeConfig.starters.map((starter, idx) => {
                  const Icon = starter.icon;
                  return (
                    <button
                      key={idx}
                      onClick={() => handleQuickAction(starter.cmd)}
                      className={`text-left p-4 rounded-xl bg-white border border-slate-200 ${starter.color} hover:shadow-sm transition-all group cursor-pointer`}
                    >
                      <div className="flex items-center space-x-2 font-bold text-xs mb-1.5">
                        <Icon className="h-4 w-4 group-hover:scale-110 transition-transform shrink-0" />
                        <span>{starter.label}</span>
                      </div>
                      <p className="text-xs text-slate-500 leading-snug">
                        {starter.desc}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Loading indicator */}
          {isLoading && (
            <div className="py-4 bg-slate-50/50">
              <div className="max-w-4xl mx-auto flex items-start space-x-4 px-4 sm:px-6">
                <div className="h-8 w-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center animate-pulse shadow-sm">
                  <Sparkles className="h-4 w-4" />
                </div>
                <div className="flex items-center space-x-2 text-xs text-slate-500 font-mono pt-1.5">
                  <div className="h-1.5 w-1.5 bg-indigo-600 rounded-full animate-bounce"></div>
                  <div className="h-1.5 w-1.5 bg-indigo-600 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="h-1.5 w-1.5 bg-indigo-600 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                  <span className="text-indigo-900 font-medium">Synthesizing adversarial dialectic & compiling telemetry...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Bottom Fixed Input Deck (Stitch MCP Executive Floating Container) */}
      <footer className="shrink-0 p-4 pb-6 bg-gradient-to-t from-slate-50 via-slate-50/90 to-transparent">
        <div className="max-w-4xl mx-auto space-y-2.5">
          {/* Quick Action Presets */}
          <div className="flex items-center space-x-2 overflow-x-auto no-scrollbar py-0.5 text-xs">
            <span className="text-slate-400 text-[10px] font-mono uppercase font-semibold tracking-wider shrink-0">Presets:</span>
            <button
              onClick={() => handleQuickAction("/evaluate JD_34")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-emerald-500 hover:bg-emerald-50/50 hover:text-emerald-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer"
            >
              <Scale className="h-3 w-3 text-emerald-600" />
              <span>/evaluate JD_34</span>
            </button>
            <button
              onClick={() => handleQuickAction("/tailor JD_34")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-indigo-500 hover:bg-indigo-50/50 hover:text-indigo-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer"
            >
              <FileText className="h-3 w-3 text-indigo-600" />
              <span>/tailor JD_34</span>
            </button>
            <button
              onClick={() => handleQuickAction("/pipeline")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-blue-500 hover:bg-blue-50/50 hover:text-blue-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer"
            >
              <Briefcase className="h-3 w-3 text-blue-600" />
              <span>/pipeline</span>
            </button>
            <button
              onClick={() => handleQuickAction("/gap")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-purple-500 hover:bg-purple-50/50 hover:text-purple-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer"
            >
              <Layers className="h-3 w-3 text-purple-600" />
              <span>/gap</span>
            </button>
            <button
              onClick={() => handleQuickAction("/enrich")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 text-slate-700 hover:border-amber-500 hover:bg-amber-50/50 hover:text-amber-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer"
            >
              <Sparkles className="h-3 w-3 text-amber-600" />
              <span>/enrich</span>
            </button>
          </div>

          {/* Slash Command Autocomplete Popover */}
          {showCommands && (
            <div className="relative">
              <CommandMenu
                filterText={input.slice(1)}
                onSelectCommand={handleSelectCommand}
                onClose={() => setShowCommands(false)}
              />
            </div>
          )}

          {/* Stitch MCP Input Container */}
          <div className="relative rounded-2xl border border-slate-200 bg-white shadow-career-elevated focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Paste any job URL, drop a recruiter email, or type a command (/evaluate, /tailor, /pipeline)..."
              className="w-full resize-none bg-transparent px-4 pt-3.5 pb-12 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
            />

            {/* Input Action Cluster */}
            <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCommands(!showCommands)}
                  className="inline-flex items-center space-x-1 rounded-md px-2 py-1 text-xs font-mono text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors cursor-pointer border border-slate-200"
                  title="Slash Commands Menu"
                >
                  <Terminal className="h-3.5 w-3.5 text-indigo-600" />
                  <span>Commands</span>
                </button>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => {
                    if (!input.trim() || isLoading) return;
                    setShowCommands(false);
                    append({ role: "user", content: input.trim() });
                    setInput("");
                  }}
                  disabled={!input.trim() || isLoading}
                  className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-xs cursor-pointer"
                >
                  <ArrowUp className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between px-1 text-[11px] text-slate-400 font-mono">
            <div>
              <span>CareerOS Super-Agent • </span>
              <span className="text-indigo-600 font-medium">B2C Free / Enterprise Powered</span>
            </div>
            <div>
              <span>Press </span>
              <kbd className="px-1 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 font-semibold">Enter</kbd>
              <span> to send, </span>
              <kbd className="px-1 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 font-semibold">/</kbd>
              <span> for commands</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Slide-over Inbound Recruiter Offers Drawer */}
      <InboundOffersDrawer isOpen={showInbound} onClose={() => setShowInbound(false)} />

      {/* Candidate Self-Serve CV Ingestion Modal */}
      <UploadCVModal isOpen={showUploadCV} onClose={() => setShowUploadCV(false)} />

      {/* B2B Recruiter Requisition Matching Workspace */}
      <RecruiterPortalModal isOpen={showRecruiterPortal} onClose={() => setShowRecruiterPortal(false)} />
    </div>
  );
};

export default ChatInterface;
