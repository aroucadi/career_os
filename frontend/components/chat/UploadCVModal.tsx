"use client";

import React, { useState, useRef } from "react";
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  X, 
  Sparkles, 
  Layers, 
  ArrowRight,
  ShieldCheck,
  Building2,
  FileCheck
} from "lucide-react";

interface UploadCVModalProps {
  isOpen: boolean;
  onClose: () => void;
  onProfileActivated?: (profileId: string) => void;
}

export const UploadCVModal: React.FC<UploadCVModalProps> = ({ isOpen, onClose, onProfileActivated }) => {
  const [activeTab, setActiveTab] = useState<"upload" | "paste">("upload");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState("");
  const [preferredMode, setPreferredMode] = useState("freelance");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [parsedResult, setParsedResult] = useState<any | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      if (activeTab === "upload") {
        if (!selectedFile) {
          setError("Please select a PDF, DOCX, or text resume file.");
          setIsSubmitting(false);
          return;
        }
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("preferred_mode", preferredMode);

        const res = await fetch("http://127.0.0.1:8000/api/candidates/upload-cv", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Upload failed with status ${res.status}`);
        }

        const data = await res.json();
        setParsedResult(data);
      } else {
        if (!pastedText.trim() || pastedText.trim().length < 50) {
          setError("Please paste comprehensive resume text (minimum 50 characters).");
          setIsSubmitting(false);
          return;
        }

        const res = await fetch("http://127.0.0.1:8000/api/candidates/upload-cv-json", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: pastedText.trim(),
            filename: "pasted_resume.txt",
            preferred_mode: preferredMode
          })
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Ingestion failed with status ${res.status}`);
        }

        const data = await res.json();
        setParsedResult(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to process resume. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleActivate = () => {
    if (parsedResult?.profile_id && onProfileActivated) {
      onProfileActivated(parsedResult.profile_id);
    }
    onClose();
    window.location.reload();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/65 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="flex flex-col bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-xl overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="h-16 shrink-0 border-b border-slate-200 bg-white px-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xs shadow-sm">
              <Upload className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Import Your Candidate Profile
              </h3>
              <p className="text-xs text-slate-500">
                Universal telemetry ingestion • Any persona or career track
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

        {/* Body */}
        <div className="p-6 space-y-5">
          {!parsedResult ? (
            <>
              {/* Career Track Selector */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-700">Primary Career Goal / Track</label>
                <select
                  value={preferredMode}
                  onChange={(e) => setPreferredMode(e.target.value)}
                  className="w-full text-xs font-mono bg-white border border-slate-300 rounded-lg p-2.5 text-slate-800 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
                >
                  <option value="freelance">💼 Freelance / Contractor (Target TJM €800 - €1,200/d)</option>
                  <option value="employee">🏢 Full-Time (CDI / Perm Package)</option>
                  <option value="fractional">🧩 Fractional / Portfolio Executive</option>
                  <option value="student">🎓 Student / Graduate Entry</option>
                  <option value="pivot">🔄 Career Pivoter (AI Specialization)</option>
                </select>
              </div>

              {/* Mode Tabs */}
              <div className="flex items-center space-x-2 border-b border-slate-200 pb-2 text-xs font-medium">
                <button
                  onClick={() => { setActiveTab("upload"); setError(null); }}
                  className={`pb-1.5 px-2.5 border-b-2 font-semibold transition-colors ${
                    activeTab === "upload"
                      ? "border-indigo-600 text-indigo-700"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  Upload File (PDF / DOCX)
                </button>
                <button
                  onClick={() => { setActiveTab("paste"); setError(null); }}
                  className={`pb-1.5 px-2.5 border-b-2 font-semibold transition-colors ${
                    activeTab === "paste"
                      ? "border-indigo-600 text-indigo-700"
                      : "border-transparent text-slate-500 hover:text-slate-800"
                  }`}
                >
                  Paste Plain Text
                </button>
              </div>

              {/* Upload Drop Zone */}
              {activeTab === "upload" ? (
                <div
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                    selectedFile
                      ? "border-emerald-400 bg-emerald-50/40"
                      : "border-slate-300 hover:border-indigo-400 bg-slate-50/60"
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.doc,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  {selectedFile ? (
                    <div className="space-y-2">
                      <FileCheck className="h-10 w-10 text-emerald-600 mx-auto" />
                      <div className="text-xs font-bold text-slate-800">{selectedFile.name}</div>
                      <div className="text-[11px] font-mono text-slate-500">
                        {(selectedFile.size / 1024).toFixed(1)} KB • Ready for extraction
                      </div>
                      <span className="inline-block text-[10px] text-indigo-600 font-semibold underline mt-1">
                        Click to change file
                      </span>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="h-10 w-10 text-slate-400 mx-auto" />
                      <div className="text-xs font-semibold text-slate-700">
                        Drag and drop your CV here, or browse
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono">
                        Supports PDF, Word (.docx), or plain text. Zero hallucination extraction.
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-1.5">
                  <textarea
                    rows={7}
                    value={pastedText}
                    onChange={(e) => setPastedText(e.target.value)}
                    placeholder="Paste full resume text or LinkedIn profile summary here..."
                    className="w-full text-xs font-mono bg-white border border-slate-300 rounded-xl p-3 text-slate-800 focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none resize-none leading-relaxed"
                  />
                </div>
              )}

              {error && (
                <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs flex items-center space-x-2">
                  <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
                  <span>{error}</span>
                </div>
              )}
            </>
          ) : (
            /* Parsed Success View */
            <div className="space-y-4 animate-in fade-in duration-300">
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center space-x-3">
                <CheckCircle2 className="h-6 w-6 text-emerald-600 shrink-0" />
                <div>
                  <h4 className="text-xs font-bold text-emerald-900">Profile Parsed & Indexed in Talent Lake</h4>
                  <p className="text-[11px] text-emerald-700">Calibrated into SQLite database with full privacy protection.</p>
                </div>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2 text-xs">
                <div className="flex justify-between border-b border-slate-200 pb-2">
                  <span className="text-slate-500">Candidate Name:</span>
                  <strong className="text-slate-900 font-semibold">{parsedResult.full_name}</strong>
                </div>
                <div className="flex justify-between border-b border-slate-200 pb-2">
                  <span className="text-slate-500">Detected Headline:</span>
                  <span className="text-slate-800 font-medium truncate max-w-[280px]">{parsedResult.headline}</span>
                </div>
                <div className="flex justify-between border-b border-slate-200 pb-2">
                  <span className="text-slate-500">Contact Email:</span>
                  <span className="font-mono text-slate-700">{parsedResult.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Proof Metrics:</span>
                  <span className="font-mono font-bold text-indigo-700">{parsedResult.proof_metrics_count} Grounded Points</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="h-16 shrink-0 border-t border-slate-200 bg-slate-50 px-6 flex items-center justify-end space-x-3">
          {!parsedResult ? (
            <>
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-100 text-slate-700 text-xs font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting || (activeTab === "upload" && !selectedFile) || (activeTab === "paste" && !pastedText.trim())}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-xs disabled:opacity-50 transition-all cursor-pointer"
              >
                {isSubmitting ? (
                  <>
                    <span className="animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full"></span>
                    <span>Extracting Telemetry...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>Ingest & Build Profile</span>
                  </>
                )}
              </button>
            </>
          ) : (
            <button
              type="button"
              onClick={handleActivate}
              className="flex items-center space-x-2 px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <span>Activate as My CareerOS Profile</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadCVModal;
