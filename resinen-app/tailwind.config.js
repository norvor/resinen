/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'sp-cyan': '#40E0D0',
        'sp-yellow': '#F9F447',
        'sp-red': '#E84A43',
        'sp-green': '#5BC236',
        'sp-orange': '#F3752B',
        'sp-brown': '#7B4C29',
        'sp-blue': '#2D4F8E',
        'sp-paper': '#F5F5F5',
        'sp-paper-dark': '#E5E5E5', // Slightly darker for dashboard bg
      },
      boxShadow: {
        'hard': '4px 4px 0px 0px rgba(0,0,0,1)',
        'hard-lg': '8px 8px 0px 0px rgba(0,0,0,1)',
        'hard-sm': '2px 2px 0px 0px rgba(0,0,0,1)',
      },
      fontFamily: {
        sans: ['Verdana', 'sans-serif'],
      }
    },
  },
  plugins: [],
};