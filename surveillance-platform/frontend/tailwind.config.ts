import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Mission-control dark theme
        bg: {
          primary: "#0a0e17",
          secondary: "#111827",
          tertiary: "#1f2937",
          card: "#1a2332",
        },
        accent: {
          blue: "#3b82f6",
          green: "#10b981",
          yellow: "#f59e0b",
          red: "#ef4444",
          purple: "#8b5cf6",
        },
        border: {
          DEFAULT: "#2d3748",
          light: "#374151",
        },
        text: {
          primary: "#f9fafb",
          secondary: "#9ca3af",
          muted: "#6b7280",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "flash-red": "flash-red 0.5s ease-in-out",
      },
      keyframes: {
        "flash-red": {
          "0%, 100%": { backgroundColor: "transparent" },
          "50%": { backgroundColor: "rgba(239, 68, 68, 0.2)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
