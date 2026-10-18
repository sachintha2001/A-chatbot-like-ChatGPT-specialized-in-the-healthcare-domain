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
          navy: "#0F172A",
          slate: "#334155",
          muted: "#64748B",
          border: "#E2E8F0",
          surface: "#F8FAFC",
          panel: "#FFFFFF",
          teal: {
            DEFAULT: "#0D9488",
            hover: "#0F766E",
            light: "#F0FDFA",
            border: "#99F6E4"
          }
        },
        severity: {
          routine: {
            text: "#15803D",
            bg: "#F0FDF4",
            border: "#BBF7D0"
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
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Courier New", "monospace"]
      }
    },
  },
  plugins: [],
};
export default config;
