/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#081018',
        'brand-slate': '#e5edf4',
        'brand-cyan': '#0ea5e9',
        'brand-lime': '#84cc16',
      },
      fontFamily: {
        display: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
