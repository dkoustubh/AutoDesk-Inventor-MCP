/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          900: "#0b0f19",
          800: "#111827",
          700: "#1f2937",
          600: "#374151",
          accent: "#f59e0b",
          cyan: "#06b6d4",
          success: "#10b981"
        }
      }
    },
  },
  plugins: [],
}
