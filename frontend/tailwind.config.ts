import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1b1e24",
        muted: "#6b7280",
        faint: "#9aa1ac",
        line: "#e8eaef",
        panel: "#f4f5f8",
        mist: "#eef1f6",
        canvas: "#f7f8fa",
        brand: "#2454d6",
        "brand-soft": "#eef2fe",
        teal: "#0f766e",
        gold: "#b45309",
        coral: "#be3f4f",
        success: "#15803d",
        "success-soft": "#e9f6ec",
        warning: "#b45309",
        "warning-soft": "#faf1e2",
        danger: "#b91c1c",
        "danger-soft": "#fbecec"
      },
      borderRadius: {
        xl: "14px",
        "2xl": "18px"
      },
      boxShadow: {
        card: "0 1px 2px rgba(16, 24, 40, 0.04)",
        panel: "0 1px 2px rgba(16, 24, 40, 0.05)",
        elevated: "0 10px 30px rgba(16, 24, 40, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
