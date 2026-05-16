import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        muted: "#667085",
        line: "#d7deea",
        panel: "#f6f8fb",
        mist: "#eaf0f7",
        brand: "#2454d6",
        teal: "#0f766e",
        gold: "#b45309",
        coral: "#be3f4f",
        success: "#15803d",
        warning: "#b45309",
        danger: "#b91c1c"
      },
      boxShadow: {
        panel: "0 1px 2px rgba(16, 24, 40, 0.06), 0 8px 24px rgba(16, 24, 40, 0.04)",
        elevated: "0 18px 48px rgba(16, 24, 40, 0.10), 0 2px 6px rgba(16, 24, 40, 0.05)"
      }
    }
  },
  plugins: []
};

export default config;
