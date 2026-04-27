/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B0F17",
        card: "#111827",
        border: "#1F2937",
        primary: "#3B82F6",
        danger: "#EF4444",
        success: "#22C55E",
        warning: "#F59E0B",
        muted: "#94A3B8",
      },
      fontFamily: {
        sans: ["Inter", "Satoshi", "sans-serif"],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
