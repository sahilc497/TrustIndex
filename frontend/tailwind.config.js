/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        trusted: {
          light: '#ecfdf5',
          DEFAULT: '#10b981',
          dark: '#047857',
        },
        uncertain: {
          light: '#fefce8',
          DEFAULT: '#eab308',
          dark: '#a16207',
        },
        hallucinated: {
          light: '#fef2f2',
          DEFAULT: '#ef4444',
          dark: '#b91c1c',
        }
      }
    },
  },
  plugins: [],
}
