/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FF6B35',
        'primary-dark': '#E85A2A',
        secondary: '#4ECDC4',
        accent: '#FFD23F',
      },
      animation: {
        'bounce-slow': 'bounce 3s infinite',
        'pulse-ring': 'pulse-ring 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      keyframes: {
        'pulse-ring': {
          '0%': {
            transform: 'scale(1)',
            opacity: '1',
          },
          '100%': {
            transform: 'scale(1.5)',
            opacity: '0',
          },
        },
      },
    },
  },
  plugins: [],
}
