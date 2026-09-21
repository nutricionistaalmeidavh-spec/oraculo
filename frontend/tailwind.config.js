/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        oracle: {
          critical: '#ef4444',
          high: '#f59e0b',
          medium: '#3b82f6',
          observation: '#6b7280',
        }
      }
    },
  },
  plugins: [],
};
