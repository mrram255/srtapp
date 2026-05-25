/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1A1A2E",
          foreground: "#F8F6F0",
          50: "#f0f0f5",
          100: "#d9d9e6",
          200: "#b3b3cd",
          300: "#8c8cb4",
          400: "#66669b",
          500: "#404082",
          600: "#333368",
          700: "#26264e",
          800: "#1A1A2E",
          900: "#0d0d17",
        },
        secondary: {
          DEFAULT: "#16213E",
          foreground: "#F8F6F0",
        },
        accent: {
          DEFAULT: "#E94560",
          foreground: "#FFFFFF",
          50: "#fde8ec",
          100: "#f9b8c4",
          200: "#f5889c",
          300: "#f15874",
          400: "#ed284c",
          500: "#E94560",
          600: "#ba1e3a",
          700: "#8b162b",
          800: "#5c0e1d",
          900: "#2d070e",
        },
        gold: {
          DEFAULT: "#F5A623",
          foreground: "#1A1A2E",
        },
        background: "#F8F6F0",
        surface: "#FFFFFF",
        "surface-mid": "#F3F1EC",
        border: "#E5E1D8",
        success: "#10B981",
        warning: "#F5A623",
        error: "#E94560",
        info: "#8B5CF6",
        muted: {
          DEFAULT: "#F3F1EC",
          foreground: "#6B7280",
        },
        foreground: "#1A1A2E",
        card: {
          DEFAULT: "#FFFFFF",
          foreground: "#1A1A2E",
        },
        destructive: {
          DEFAULT: "#E94560",
          foreground: "#FFFFFF",
        },
        ring: "#E94560",
        input: "#E5E1D8",
      },
      fontFamily: {
        display: ["var(--font-display)", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        numeric: ["var(--font-numeric)", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        lg: "12px",
        md: "8px",
        sm: "6px",
      },
      boxShadow: {
        card: "0 2px 16px rgba(26,26,46,0.08)",
        elevated: "0 8px 32px rgba(26,26,46,0.16)",
        crisp: "0 1px 4px rgba(26,26,46,0.12)",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.3s ease-out",
        "slide-in": "slide-in 0.3s ease-out",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/container-queries"),
    require("tailwindcss-animate"),
  ],
};
