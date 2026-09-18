import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        career: {
          bg: "#F8FAFC",            // Cool, luminous slate canvas (pure light)
          surface: "#FFFFFF",       // Crisp white card & panel surface
          surfaceSubtle: "#F1F5F9", // Recessed panel / subtle container
          card: "#FFFFFF",          // Elevated card surface
          cardHover: "#F8FAFC",     // Light hover state
          border: "#E2E8F0",        // Razor-thin precision border
          borderSubtle: "#F1F5F9",  // Subtle divider
          borderStrong: "#CBD5E1",  // Interactive border
          text: "#0F172A",          // Deep Slate-900 primary text
          textSecondary: "#334155", // Slate-700 secondary text
          textMuted: "#64748B",     // Slate-500 refined muted text
          accent: "#4F46E5",        // Electric Indigo execution vector
          accentHover: "#4338CA",
          accentLight: "#EEF2FF",   // Indigo tint background
          accentGlow: "rgba(79, 70, 229, 0.15)",
          emerald: "#10B981",       // Positive yield / verified fit
          emeraldLight: "#ECFDF5",  // Emerald tint
          emeraldBorder: "#A7F3D0",
          emeraldText: "#065F46",
          rose: "#F43F5E",          // Prosecutor risk / dealbreaker alert
          roseLight: "#FFF1F2",     // Rose tint
          roseBorder: "#FECDD3",
          roseText: "#9F1239",
          amber: "#F59E0B",         // Warning
          amberLight: "#FFFBEB",
          cyan: "#0284C7",          // Active radar / telemetry
          cyanLight: "#F0F9FF",
        },
        claude: {
          bg: "#F8FAFC",
          surface: "#FFFFFF",
          subtle: "#F1F5F9",
          sidebar: "#FFFFFF",
          hover: "#F1F5F9",
          text: "#0F172A",
          muted: "#64748B",
          accent: "#4F46E5",
          accentHover: "#4338CA",
          border: "#E2E8F0",
        }
      },
      fontFamily: {
        sans: ['Inter', 'Geist', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'career-card': '0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)',
        'career-elevated': '0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04)',
        'career-input': '0 4px 20px -2px rgba(15, 23, 42, 0.08), 0 0 0 1px rgba(79, 70, 229, 0.2)',
        'claude-card': '0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)',
        'claude-elevated': '0 10px 25px -5px rgba(15, 23, 42, 0.08), 0 8px 10px -6px rgba(15, 23, 42, 0.04)',
        'claude-input': '0 4px 20px -2px rgba(15, 23, 42, 0.08), 0 0 0 1px rgba(79, 70, 229, 0.2)',
      }
    },
  },
  plugins: [],
};
export default config;
