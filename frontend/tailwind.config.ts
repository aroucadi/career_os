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
        canvas: "var(--surface-canvas)",
        surface: {
          DEFAULT: "var(--surface-card)",
          card: "var(--surface-card)",
          subtle: "var(--surface-subtle)",
          elevated: "var(--surface-elevated)",
        },
        border: {
          subtle: "var(--border-subtle)",
          interactive: "var(--border-interactive)",
          focus: "var(--border-focus)",
        },
        content: {
          primary: "var(--text-primary)",
          secondary: "var(--text-secondary)",
          muted: "var(--text-muted)",
        },
        accent: {
          DEFAULT: "var(--accent-primary)",
          hover: "var(--accent-primary-hover)",
          subtle: "var(--accent-subtle)",
        },
        career: {
          bg: "#F8FAFC",
          surface: "#FFFFFF",
          surfaceSubtle: "#F1F5F9",
          card: "#FFFFFF",
          cardHover: "#F8FAFC",
          border: "#E2E8F0",
          borderSubtle: "#F1F5F9",
          borderStrong: "#CBD5E1",
          text: "#0F172A",
          textSecondary: "#334155",
          textMuted: "#64748B",
          accent: "#4F46E5",
          accentHover: "#4338CA",
          accentLight: "#EEF2FF",
          accentGlow: "rgba(79, 70, 229, 0.15)",
          emerald: "#10B981",
          emeraldLight: "#ECFDF5",
          emeraldBorder: "#A7F3D0",
          emeraldText: "#065F46",
          rose: "#F43F5E",
          roseLight: "#FFF1F2",
          roseBorder: "#FECDD3",
          roseText: "#9F1239",
          amber: "#F59E0B",
          amberLight: "#FFFBEB",
          cyan: "#0284C7",
          cyanLight: "#F0F9FF",
        }
      },
      fontFamily: {
        sans: ['Inter', 'Geist', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      spacing: {
        'touch': '44px',
        'touch-gap': '8px',
      },
      boxShadow: {
        'career-card': '0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)',
        'career-elevated': '0 10px 25px -5px rgba(15, 23, 42, 0.06), 0 8px 10px -6px rgba(15, 23, 42, 0.03)',
        'career-input': '0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 0 0 1px rgba(79, 70, 229, 0.15)',
        'focus-ring': '0 0 0 2px #FFFFFF, 0 0 0 4px #4F46E5',
      }
    },
  },
  plugins: [],
};

export default config;
