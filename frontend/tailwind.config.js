/**
 * tailwind.config.js — Tailwind CSS configuration for CodeTrace frontend.
 *
 * - content: tells Tailwind which files to scan for class names
 * - darkMode: 'class' strategy — dark mode is activated by adding
 *   the 'dark' class to <html> (done in main.jsx)
 * - theme.extend.colors: CSS variable-based color tokens used by shadcn/ui
 * - plugins: tailwindcss-animate powers shadcn/ui component animations
 */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],

  // Dark mode via class strategy (we force 'dark' on <html> in main.jsx)
  darkMode: "class",

  theme: {
    extend: {
      // shadcn/ui uses CSS variables for colors — map them here so
      // Tailwind utilities like bg-background, text-foreground work
      colors: {
        border:      "hsl(var(--border))",
        input:       "hsl(var(--input))",
        ring:        "hsl(var(--ring))",
        background:  "hsl(var(--background))",
        foreground:  "hsl(var(--foreground))",
        primary: {
          DEFAULT:    "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT:    "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT:    "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT:    "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT:    "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT:    "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },

        // ── Material Design 3 tokens (Stitch UI design) ──────────────
        "on-surface":               "var(--md-on-surface)",
        "on-surface-variant":       "var(--md-on-surface-variant)",
        "primary-container":        "var(--md-primary-container)",
        "on-primary-container":     "var(--md-on-primary-container)",
        "surface-container-high":   "var(--md-surface-container-high)",
        "surface-container-low":    "var(--md-surface-container-low)",
        "surface-container-lowest": "var(--md-surface-container-lowest)",
        "outline":                  "var(--md-outline)",
        "outline-variant":          "var(--md-outline-variant)",
        "tertiary-fixed-dim":       "var(--md-tertiary-fixed-dim)",
        "primary-fixed":            "var(--md-primary-fixed)",
        "error":                    "var(--md-error)",
      },

      fontFamily: {
        headline: ["Space Grotesk", "JetBrains Mono", "monospace"],
        body:     ["Inter", "sans-serif"],
        mono:     ["JetBrains Mono", "Fira Code", "monospace"],
      },

      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },

  // tailwindcss-animate powers shadcn/ui component enter/exit animations
  plugins: [require("tailwindcss-animate")],
};
