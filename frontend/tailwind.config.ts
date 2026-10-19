import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        clinical: {
          navy: "#0A2540",
          navyLight: "#10375C",
          slate: "#2C4257",
          muted: "#5A7184",
          border: "#D5E6EC",
          surface: "#F2F8FA",
          ice: "#EBF5F8",
          panel: "#FFFFFF",
          teal: {
            DEFAULT: "#0D9488",
            hover: "#0F766E",
            light: "#F0FDFA",
            border: "#99F6E4",
            deep: "#115E59"
          },
          cerulean: {
            DEFAULT: "#0284C7",
            hover: "#0369A1",
            light: "#F0F9FF",
            border: "#BAE6FD"
          }
        },
        severity: {
          routine: {
            text: "#047857",
            bg: "#ECFDF5",
            border: "#A7F3D0"
          },
          urgent: {
            text: "#B45309",
            bg: "#FFFBEB",
            border: "#FDE68A"
          },
          emergency: {
            text: "#B91C1C",
            bg: "#FEF2F2",
            border: "#FECACA"
          }
        }
      },
      boxShadow: {
        "clinical-card": "0 4px 20px -2px rgba(10, 37, 64, 0.06), 0 2px 6px -1px rgba(13, 148, 136, 0.04)",
        "clinical-elevated": "0 12px 32px -4px rgba(10, 37, 64, 0.12), 0 4px 12px -2px rgba(13, 148, 136, 0.08)",
        "clinical-glow": "0 0 0 3px rgba(13, 148, 136, 0.18)"
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"]
      }
    },
  },
  plugins: [],
};
export default config;

