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
        page: "var(--bg-page)",
        stage: {
          DEFAULT: "var(--bg-stage)",
          border: "var(--border-stage)",
        },
        border: {
          subtle: "var(--border-subtle)",
          hairline: "var(--border-hairline)",
        },
        slate: {
          950: "#0F172A",
          900: "#1E293B",
          600: "#475569",
          500: "#64748B",
          400: "#94A3B8",
        },
        primary: {
          DEFAULT: "var(--primary)",
          bevel: "var(--primary-bevel)",
          hover: "var(--primary-hover)",
        },
        pill: {
          purple: "var(--accent-pill-text)",
          "purple-bg": "var(--accent-pill-bg)",
        },
        dark: {
          footer: "var(--bg-footer)",
        },
      },
      borderRadius: {
        sm: "var(--radius-sm)", // 6px
        btn: "var(--radius-btn)", // 8px
        card: "var(--radius-card)", // 12px
        stage: "var(--radius-stage)", // 14px
        pill: "var(--radius-pill)", // 9999px
      },
      boxShadow: {
        "btn-bevel": "var(--shadow-btn)",
        "btn-active": "var(--shadow-btn-active)",
        card: "var(--shadow-card)",
        stage: "var(--shadow-stage)",
        "floating-preview": "var(--shadow-floating-preview)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "-apple-system", "sans-serif"],
        heading: ["var(--font-heading)", "var(--font-sans)", "system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
