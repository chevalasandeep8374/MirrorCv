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
        paper: {
          DEFAULT: "var(--bg-paper)",
          surface: "var(--bg-surface)",
          border: "var(--border-hairline)",
        },
        ink: {
          DEFAULT: "var(--ink-heading)",
          body: "var(--ink-body)",
          muted: "var(--ink-muted)",
        },
        accent: {
          DEFAULT: "var(--color-accent)",
          subtle: "var(--color-accent-subtle)",
        },
        navy: {
          sidebar: "var(--navy-sidebar)",
        },
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      borderRadius: {
        sm: "var(--radius-sm)", // 10px
        card: "var(--radius-card)", // 14px
        pill: "var(--radius-pill)", // 9999px
      },
      boxShadow: {
        "floating-preview": "var(--shadow-floating-preview)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "-apple-system", "sans-serif"],
      },
      letterSpacing: {
        tighter: "-0.03em",
      },
      lineHeight: {
        headline: "1.02",
        body: "1.6",
      },
      spacing: {
        30: "7.5rem", // 120px
        35: "8.75rem", // 140px
        40: "10rem", // 160px
      },
    },
  },
  plugins: [],
};

export default config;
