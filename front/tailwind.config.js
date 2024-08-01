/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    fontFamily: {
      satoshi: ['Satoshi', 'sans-serif']
    },
  },
  plugins: [
    require('daisyui'),
  ]
}
