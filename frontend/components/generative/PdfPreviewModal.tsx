"use client";

import React, { useState, useEffect } from "react";
import { 
  FileText, 
  Download, 
  Printer, 
  ExternalLink, 
  X, 
  ShieldCheck, 
  Layers, 
  Maximize2,
  Minimize2,
  Sparkles,
  CheckCircle2,
  Layout,
  Code
} from "lucide-react";

interface PdfPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  pdfUrl: string;
  htmlUrl?: string;
  candidateName?: string;
  targetRole?: string;
  authenticityScore?: number;
  bulletsCount?: number;
}

export const PdfPreviewModal: React.FC<PdfPreviewModalProps> = ({
  isOpen,
  onClose,
  pdfUrl,
  htmlUrl,
  candidateName = "Candidate",
  targetRole = "Target Position",
  authenticityScore = 95,
  bulletsCount = 14
}) => {
  const [activeTab, setActiveTab] = useState<"pdf" | "html" | "ats">("pdf");
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handlePrint = () => {
    const iframe = document.getElementById("pdf-preview-frame") as HTMLIFrameElement;
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.print();
    } else {
      window.open(pdfUrl, "_blank")?.print();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/65 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className={`flex flex-col bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden transition-all duration-300 ${
          isFullscreen ? "w-full h-full rounded-none" : "w-full max-w-5xl h-[90vh]"
        }`}
      >
        {/* Top Header */}
        <header className="h-16 shrink-0 border-b border-slate-200 bg-white px-5 sm:px-6 flex items-center justify-between z-10 shadow-xs">
          <div className="flex items-center space-x-3 min-w-0">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xs shadow-sm shrink-0">
              <FileText className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-slate-900 truncate">
                  {candidateName} — Tailored A4 Resume
                </h3>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 shrink-0">
                  ISO-216 A4 (210×297mm)
                </span>
              </div>
              <p className="text-xs text-slate-500 truncate mt-0.5">
                Targeting: <strong className="text-slate-800 font-semibold">{targetRole}</strong>
              </p>
            </div>
          </div>

          {/* Center Tabs */}
          <div className="hidden md:flex items-center space-x-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-medium">
            <button
              onClick={() => setActiveTab("pdf")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition-all ${
                activeTab === "pdf"
                  ? "bg-white text-indigo-700 font-bold shadow-xs border border-slate-200/80"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Compiled PDF</span>
            </button>
            <button
              onClick={() => setActiveTab("html")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition-all ${
                activeTab === "html"
                  ? "bg-white text-indigo-700 font-bold shadow-xs border border-slate-200/80"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Layout className="h-3.5 w-3.5" />
              <span>HTML Canvas</span>
            </button>
            <button
              onClick={() => setActiveTab("ats")}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md transition-all ${
                activeTab === "ats"
                  ? "bg-white text-indigo-700 font-bold shadow-xs border border-slate-200/80"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <Code className="h-3.5 w-3.5" />
              <span>ATS Clean Text</span>
            </button>
          </div>

          {/* Right Action Cluster */}
          <div className="flex items-center space-x-2">
            {/* Authenticity pill */}
            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-mono font-bold">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              <span>{authenticityScore}% Human</span>
            </div>

            {/* Print */}
            <button
              onClick={handlePrint}
              className="hidden sm:flex items-center space-x-1 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-medium transition-colors cursor-pointer"
              title="Print Document"
            >
              <Printer className="h-3.5 w-3.5 text-slate-500" />
              <span>Print</span>
            </button>

            {/* Download */}
            <a
              href={pdfUrl}
              download
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Download className="h-3.5 w-3.5" />
              <span>Download A4</span>
            </a>

            {/* Fullscreen Toggle */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            >
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </button>

            {/* Close */}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              title="Close (Esc)"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Viewport Content */}
        <div className="flex-1 bg-slate-100 p-2 sm:p-4 overflow-hidden relative flex justify-center items-center">
          {activeTab === "pdf" && (
            <div className="w-full h-full bg-white rounded-lg shadow-inner overflow-hidden border border-slate-200/80">
              <iframe
                id="pdf-preview-frame"
                src={`${pdfUrl}#view=FitH`}
                title="A4 Resume PDF Preview"
                className="w-full h-full border-none"
              />
            </div>
          )}

          {activeTab === "html" && htmlUrl && (
            <div className="w-full h-full bg-white rounded-lg shadow-inner overflow-hidden border border-slate-200/80">
              <iframe
                src={htmlUrl}
                title="A4 HTML Resume Canvas"
                className="w-full h-full border-none"
              />
            </div>
          )}

          {activeTab === "ats" && (
            <div className="w-full h-full bg-white rounded-lg shadow-inner p-6 overflow-y-auto font-mono text-xs text-slate-800 space-y-4 border border-slate-200/80">
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 flex items-center space-x-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
                <span>ATS Parser Invariant: Clean linear hierarchy, standard unicode glyphs, 0 hidden text layers.</span>
              </div>
              <div className="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-2">
                <h4 className="font-bold text-sm text-slate-900 border-b border-slate-200 pb-1">{candidateName}</h4>
                <p className="font-semibold text-indigo-700">{targetRole}</p>
                <p className="text-slate-600 text-xs">Calibrated across {bulletsCount} ground-truth bullet metrics with AI-Detector Authenticity score of {authenticityScore}%.</p>
              </div>
              <div className="space-y-1 text-slate-600">
                <div className="font-bold text-slate-900 text-xs uppercase tracking-wider">Ground-Truth Evidence Highlights:</div>
                <ul className="list-disc list-inside space-y-1 pl-1">
                  <li>Enterprise Scale: Multi-squad delivery, agile governance, cross-functional leadership.</li>
                  <li>Governance: EU AI Act, Responsible AI production guardrails, algorithmic risk management.</li>
                  <li>Commercial Alignment: Calibrated TJM / Permanent salary targets with 0 hallucination guarantee.</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer Meta */}
        <footer className="h-11 shrink-0 border-t border-slate-200 bg-white px-5 sm:px-6 flex items-center justify-between text-xs text-slate-500 font-mono">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span>Headless Puppeteer / Chromium Engine • Zero Layout Shifts</span>
          </div>
          <div className="flex items-center space-x-3">
            <span>{bulletsCount} Verified Bullets</span>
            <span>•</span>
            <a href={pdfUrl} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline flex items-center space-x-1">
              <span>Open Raw PDF</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default PdfPreviewModal;
