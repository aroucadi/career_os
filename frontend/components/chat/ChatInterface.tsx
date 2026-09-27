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
  Shuffle,
  UploadCloud,
  Mail
} from "lucide-react";
import MessageItem from "./MessageItem";
import { CommandMenu, CANDIDATE_COMMANDS, SlashCommand } from "./CommandMenu";
import { InboundOffersDrawer } from "./InboundOffersDrawer";
import { UploadCVModal } from "./UploadCVModal";
import { RecruiterPortalModal } from "../recruiter/RecruiterPortalModal";
import { AdminSecretDrawer } from "./AdminSecretDrawer";
import { ClaimAccountModal } from "./ClaimAccountModal";
import { useAnonymousSession } from "@/lib/session";

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
  const { sessionId, activeCV, saveCV, removeCV, isHydrated } = useAnonymousSession();
  const [showCommands, setShowCommands] = useState(false);
  const [showInbound, setShowInbound] = useState(false);
  const [showUploadCV, setShowUploadCV] = useState(false);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [showRecruiterPortal, setShowRecruiterPortal] = useState(false);
  const [showAdminDrawer, setShowAdminDrawer] = useState(false);
  const [activeModel, setActiveModel] = useState("gemini-2.5-flash");
  const [careerMode, setCareerMode] = useState<CareerMode>("freelance");
  
  // 5-Tap Gesture Detection State for Admin Controls (Phase 0 / Question 7)
  const [tapCount, setTapCount] = useState(0);
  const tapTimerRef = useRef<NodeJS.Timeout | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const mainScrollRef = useRef<HTMLElement>(null);

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
      profileId: activeCV?.profileId || sessionId,
      persona: "candidate",
      model: activeModel,
      career_mode: careerMode
    },
    initialMessages: [
      {
        id: "intro-1",
        role: "assistant",
        content: "👋 **Welcome to CareerOS.** I am your Universal Strategic Career Agent.\n\nDrop your CV (PDF or Markdown) and paste any target Job Description or desired role to instantly calculate your ATS match score, skill-up path, and tailored resume — completely anonymous, zero sign-up required.\n\nWhat role would you like to explore today?"
      }
    ]
  });

  // Dynamic welcome message based on active anonymous session
  useEffect(() => {
    if (isHydrated && activeCV) {
      setMessages((prev) => {
        if (prev.length === 1 && prev[0].id === "intro-1") {
          return [
            {
              id: "intro-1",
              role: "assistant",
              content: `👋 **Welcome back.** Your active CV (**${activeCV.filename}**) is loaded in your private local session.\n\nI am connected to your profile telemetry, target market JDs, gap remediation, and adversarial debates.\n\nWhat role or job description are we targeting today?`
            }
          ];
        }
        return prev;
      });
    }
  }, [isHydrated, activeCV, setMessages]);

  // Auto-detect magic-link Double Opt-In token or test demo fixture on page load (SPEC-0045)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("consent_token") || params.get("match_id")) {
        setShowInbound(true);
      }
      if (params.get("demo") === "generative") {
        setMessages([
          {
            id: "intro-1",
            role: "assistant",
            content: "👋 **Welcome back, Alaa.** Here is your latest strategic mandate evaluation:"
          },
          {
            id: "demo-eval-1",
            role: "assistant",
            content: "I have completed the dialectic arbitration for **Mandate #JD_34: Lead AI Delivery Architect (SCC)**:",
            toolInvocations: [
              {
                state: "result",
                toolCallId: "call_eval_34",
                toolName: "DebateVerdictCard",
                args: {
                  verdict: "ENGAGE & EXPLOIT FIT",
                  quality_score: 92,
                  trap_score: 12,
                  target_role: "Lead AI Delivery Architect (SCC)",
                  jd_id: "JD_34",
                  decision_rationale: "Strong alignment with candidate multi-agent AI CoE leadership. Rate floor exceeded (€950/d vs budget €1,050/d). Remote leverage confirmed.",
                  advocate_points: [
                    "Candidate architected production multi-agent system matching 100% of tech stack.",
                    "Target TJM €950/d is well within the hiring manager budget cap (€1,100/d).",
                    "100% asynchronous delivery model matches candidate operating preferences."
                  ],
                  dealbreakers: [
                    "Commute clause requires 1 quarterly onsite executive meeting in Paris (acceptable)."
                  ]
                },
                result: { success: true }
              },
              {
                state: "result",
                toolCallId: "call_tailor_34",
                toolName: "TailoredCVCard",
                args: {
                  candidate_name: "Alaa Eddine Roucadi",
                  target_role: "Lead AI Delivery Architect (SCC)",
                  tailored_summary: "Principal AI Delivery Manager & Solutions Architect with 10+ years driving enterprise AI operating models, LLM orchestration, and multi-agent platforms.",
                  bullets_synthesized: 14,
                  pdf_path: "Alaa_Eddine_Roucadi_Resume_v12.pdf",
                  ai_report: {
                    authenticity_score: 98,
                    verdict: "HUMAN_AUTHENTIC",
                    burstiness_index: 0.52,
                    token_diversity_ttr: 0.68
                  }
                },
                result: { success: true }
              }
            ]
          }
        ]);
      }
    }
  }, [setMessages]);

  // Auto scroll main container smoothly (only when user interacts or multiple messages exist, never on initial glance)
  useEffect(() => {
    if (messages.length > 2 || isLoading) {
      if (mainScrollRef.current) {
        mainScrollRef.current.scrollTo({
          top: mainScrollRef.current.scrollHeight,
          behavior: "smooth"
        });
      }
    }
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

  // 5-Tap Gesture Handler on Version Label
  const handleVersionTap = () => {
    const newCount = tapCount + 1;
    setTapCount(newCount);

    if (tapTimerRef.current) {
      clearTimeout(tapTimerRef.current);
    }

    if (newCount >= 5) {
      setTapCount(0);
      setShowAdminDrawer(true);
      if (typeof window !== "undefined" && "vibrate" in navigator) {
        try { navigator.vibrate([15, 30, 15]); } catch (e) {}
      }
    } else {
      tapTimerRef.current = setTimeout(() => {
        setTapCount(0);
      }, 2500);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-canvas text-content-primary font-sans">
      {/* Top Executive Header (Clean, 60-30-10 Balanced, Zero Clutter) */}
      <header className="h-14 shrink-0 border-b border-border-subtle bg-surface/90 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between z-20 shadow-career-card">
        {/* Left Brand Cluster */}
        <div className="flex items-center space-x-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white font-bold text-xs shadow-xs">
            OS
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-sm font-bold text-content-primary leading-tight tracking-tight">CareerOS</h1>
              <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-accent-subtle text-accent border border-indigo-200/60">
                v2.0
              </span>
            </div>
            <p className="text-[11px] text-content-muted font-medium">Strategic Career Agent</p>
          </div>
        </div>

        {/* Center / Right Functional Actions */}
        <div className="flex items-center space-x-2">
          {/* Anonymous Session Pill & Claim Account Trigger */}
          <button
            type="button"
            onClick={() => setShowClaimModal(true)}
            className="min-touch-target flex items-center space-x-1.5 px-2 sm:px-2.5 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100/80 border border-emerald-200/80 text-emerald-800 text-xs font-mono transition-colors cursor-pointer shadow-xs"
            title="Anonymous local session. Click to save across devices."
          >
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="font-semibold hidden sm:inline">{activeCV ? "Session Active" : "Guest Mode"}</span>
            {activeCV ? (
              <span className="text-[11px] text-emerald-700 max-w-[100px] truncate hidden lg:inline">
                ({activeCV.filename})
              </span>
            ) : null}
            <span className="text-[10px] text-emerald-600 bg-emerald-100/60 px-1 py-0.5 rounded font-sans font-medium">Save →</span>
          </button>

          {/* Universal Career Track Switcher */}
          <div className="flex items-center space-x-1.5 bg-surface-subtle p-1 rounded-lg border border-border-subtle text-xs font-mono">
            <span className="text-[10px] uppercase text-content-muted font-bold px-1 hidden md:inline">Track:</span>
            <select
              value={careerMode}
              onChange={(e) => setCareerMode(e.target.value as CareerMode)}
              className="bg-surface border border-border-subtle rounded-md px-2 py-1 text-content-primary font-semibold focus:outline-none focus:ring-2 focus:ring-accent/20 cursor-pointer text-xs"
              aria-label="Select Career Track"
            >
              <option value="freelance">💼 Freelance / Contractor</option>
              <option value="employee">🏢 Full-Time (CDI / Perm)</option>
              <option value="fractional">🧩 Fractional / Portfolio</option>
              <option value="student">🎓 Student / Graduate</option>
              <option value="pivot">🔄 Career Pivoter</option>
            </select>
          </div>

          {/* Inbound Direct Offers Trigger */}
          <button
            type="button"
            onClick={() => setShowInbound(true)}
            className="min-touch-target flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100/80 text-amber-800 border border-amber-200/80 text-xs font-mono font-semibold transition-colors cursor-pointer shadow-xs"
            title="Review Inbound Recruiter Introductions (Double Opt-In Gate)"
          >
            <Mail className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Inbound</span>
          </button>

          {/* Self-Serve Candidate CV Import */}
          <button
            type="button"
            onClick={() => setShowUploadCV(true)}
            className="min-touch-target flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-accent text-white hover:bg-accent-hover text-xs font-semibold transition-colors cursor-pointer shadow-xs"
            title="Import Your Candidate CV (.pdf, .docx, text)"
          >
            <UploadCloud className="h-3.5 w-3.5" />
            <span className="hidden md:inline">Import CV</span>
          </button>
        </div>
      </header>

      {/* Main Conversational Stream Area */}
      <main ref={mainScrollRef} className="flex-1 overflow-y-auto">
        <div className="py-5 space-y-1">
          {messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} career_mode={careerMode} onActionClick={handleQuickAction} />
          ))}

          {/* Hick-Hyman Law Primary Action Starters (Glance -> Act) */}
          {messages.length <= 1 && (
            <div className="max-w-4xl mx-auto px-4 sm:px-6 pt-2 pb-6">
              <div className="flex items-center justify-between mb-3">
                <div className="text-[11px] font-mono uppercase tracking-wider text-content-muted font-bold">
                  Recommended Actions for {activeConfig.label} (1-Tap):
                </div>
                <span className="text-[10px] font-mono text-accent bg-accent-subtle border border-indigo-200/60 px-2 py-0.5 rounded font-medium">
                  {activeConfig.badge2}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {activeConfig.starters.map((starter, idx) => {
                  const Icon = starter.icon;
                  return (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleQuickAction(starter.cmd)}
                      className={`min-touch-target text-left p-4 rounded-xl bg-surface border border-border-subtle ${starter.color} hover:shadow-career-card transition-all group cursor-pointer`}
                    >
                      <div className="flex items-center space-x-2 font-bold text-xs mb-1.5">
                        <Icon className="h-4 w-4 group-hover:scale-110 transition-transform shrink-0" />
                        <span>{starter.label}</span>
                      </div>
                      <p className="text-xs text-content-muted leading-snug">
                        {starter.desc}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Streaming Skeleton Indicator (Exact Dimensions, CLS = 0) */}
          {isLoading && (
            <div className="py-4 bg-surface-subtle/50">
              <div className="max-w-4xl mx-auto flex items-start space-x-4 px-4 sm:px-6">
                <div className="h-8 w-8 rounded-lg bg-accent text-white flex items-center justify-center animate-pulse shadow-xs">
                  <Sparkles className="h-4 w-4" />
                </div>
                <div className="flex items-center space-x-2 text-xs text-content-muted font-mono pt-1.5">
                  <div className="h-1.5 w-1.5 bg-accent rounded-full animate-bounce"></div>
                  <div className="h-1.5 w-1.5 bg-accent rounded-full animate-bounce [animation-delay:0.2s]"></div>
                  <div className="h-1.5 w-1.5 bg-accent rounded-full animate-bounce [animation-delay:0.4s]"></div>
                  <span className="text-content-primary font-medium">Synthesizing adversarial dialectic & compiling telemetry...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Bottom Fixed Input Deck (Thumb-Zone Natural Reach, pb-safe) */}
      <footer className="shrink-0 p-4 pb-safe bg-gradient-to-t from-canvas via-canvas/95 to-transparent">
        <div className="max-w-4xl mx-auto space-y-2.5">
          {/* Quick Action Presets (1-Tap execution) */}
          <div className="flex items-center space-x-2 overflow-x-auto no-scrollbar py-0.5 text-xs">
            <span className="text-content-muted text-[10px] font-mono uppercase font-semibold tracking-wider shrink-0">Presets:</span>
            <button
              type="button"
              onClick={() => handleQuickAction("/evaluate JD_34")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-surface border border-border-subtle text-content-primary hover:border-emerald-500 hover:bg-emerald-50 hover:text-emerald-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer min-h-[32px]"
            >
              <Scale className="h-3 w-3 text-emerald-600" />
              <span>/evaluate JD_34</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickAction("/tailor JD_34")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-surface border border-border-subtle text-content-primary hover:border-indigo-500 hover:bg-indigo-50 hover:text-indigo-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer min-h-[32px]"
            >
              <FileText className="h-3 w-3 text-indigo-600" />
              <span>/tailor JD_34</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickAction("/pipeline")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-surface border border-border-subtle text-content-primary hover:border-blue-500 hover:bg-blue-50 hover:text-blue-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer min-h-[32px]"
            >
              <Briefcase className="h-3 w-3 text-blue-600" />
              <span>/pipeline</span>
            </button>
            <button
              type="button"
              onClick={() => handleQuickAction("/gap")}
              className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-surface border border-border-subtle text-content-primary hover:border-purple-500 hover:bg-purple-50 hover:text-purple-900 transition-all shrink-0 font-mono text-xs shadow-xs cursor-pointer min-h-[32px]"
            >
              <Layers className="h-3 w-3 text-purple-600" />
              <span>/gap</span>
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

          {/* Input Box with Fitts's Law Target Size */}
          <div className="relative rounded-2xl border border-border-subtle bg-surface shadow-career-elevated focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/20 transition-all">
            <textarea
              ref={textareaRef}
              rows={1}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Paste any job URL, drop a recruiter email, or type a command (/evaluate, /tailor, /pipeline)..."
              className="w-full resize-none bg-transparent px-4 pt-3.5 pb-12 text-sm text-content-primary placeholder:text-content-muted focus:outline-none"
              aria-label="CareerOS Prompt Input"
            />

            {/* Input Action Controls */}
            <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setShowCommands(!showCommands)}
                className="inline-flex items-center space-x-1 rounded-md px-2 py-1 text-xs font-mono text-content-muted hover:bg-surface-subtle hover:text-content-primary transition-colors cursor-pointer border border-border-subtle"
                title="Slash Commands Menu"
              >
                <Terminal className="h-3.5 w-3.5 text-accent" />
                <span>Commands</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  if (!input.trim() || isLoading) return;
                  setShowCommands(false);
                  append({ role: "user", content: input.trim() });
                  setInput("");
                }}
                disabled={!input.trim() || isLoading}
                aria-label="Send prompt to CareerOS"
                className="min-touch-target flex h-10 w-10 items-center justify-center rounded-xl bg-accent text-white hover:bg-accent-hover transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-xs cursor-pointer"
              >
                <ArrowUp className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Footer with 5-Tap Gesture on Version Label (Per Phase 0/7) */}
          <div className="flex items-center justify-between px-1 text-[11px] text-content-muted font-mono select-none">
            <button
              type="button"
              onClick={handleVersionTap}
              className="text-left hover:text-content-primary transition-colors cursor-pointer"
              title="CareerOS Version (Tap 5 times for Developer Telemetry)"
            >
              <span>CareerOS Super-Agent v2.0</span>
              {tapCount > 1 && (
                <span className="ml-1 text-[10px] text-accent font-bold">
                  ({tapCount}/5 taps)
                </span>
              )}
            </button>

            <div className="hidden sm:block">
              <span>Press </span>
              <kbd className="px-1 py-0.5 rounded bg-surface-subtle border border-border-subtle text-content-secondary font-semibold">Enter</kbd>
              <span> to send, </span>
              <kbd className="px-1 py-0.5 rounded bg-surface-subtle border border-border-subtle text-content-secondary font-semibold">/</kbd>
              <span> for commands</span>
            </div>
          </div>
        </div>
      </footer>

      {/* Hidden Secret Admin & Telemetry Drawer (Opened via 5-Tap Gesture) */}
      <AdminSecretDrawer
        isOpen={showAdminDrawer}
        onClose={() => setShowAdminDrawer(false)}
        activeModel={activeModel}
        onModelChange={(m) => setActiveModel(m)}
        onOpenRecruiterPortal={() => setShowRecruiterPortal(true)}
      />

      {/* Slide-over Inbound Recruiter Offers Drawer */}
      <InboundOffersDrawer isOpen={showInbound} onClose={() => setShowInbound(false)} />

      {/* Candidate Self-Serve CV Ingestion Modal */}
      <UploadCVModal isOpen={showUploadCV} onClose={() => setShowUploadCV(false)} />

      {/* B2B Recruiter Requisition Matching Workspace */}
      <RecruiterPortalModal isOpen={showRecruiterPortal} onClose={() => setShowRecruiterPortal(false)} />

      {/* Claim Anonymous Account Modal */}
      <ClaimAccountModal 
        isOpen={showClaimModal} 
        onClose={() => setShowClaimModal(false)} 
        sessionId={sessionId}
        activeCV={activeCV}
      />
    </div>
  );
};

export default ChatInterface;
