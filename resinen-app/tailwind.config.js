/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      // 1. COLORS (Linked to CSS Variables)
      // The unusual syntax "rgb(var(--x) / <alpha-value>)" allows opacity like bg-skin-fill/50
      colors: {
        skin: {
          fill: 'rgb(var(--color-fill) / <alpha-value>)',
          text: 'rgb(var(--color-text) / <alpha-value>)',
          border: 'rgb(var(--color-border) / <alpha-value>)',
          accent: 'rgb(var(--color-accent) / <alpha-value>)',
          surface: 'rgb(var(--color-surface) / <alpha-value>)',
          muted: 'rgb(var(--color-muted) / <alpha-value>)',
        },
        // Keep your legacy colors for specific overrides if needed
        sp: {
          cyan: '#00FFFF',
          magenta: '#FF00FF',
          yellow: '#FFFF00',
          blue: '#0000FF',
          green: '#00FF00',
        }
      },
      
      // 2. PHYSICS (Linked to CSS Variables)
      borderWidth: {
        DEFAULT: '1px',
        skin: 'var(--border-width)',
      },
      borderRadius: {
        'skin-sm': 'var(--radius-sm)',
        'skin-md': 'var(--radius-md)',
        'skin-lg': 'var(--radius-lg)',
        'skin-full': 'var(--radius-full)',
      },
      boxShadow: {
        'hard': 'var(--shadow-hard)',
      },
      fontFamily: {
        header: ['var(--font-header)'],
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'), // Ensure this is installed if you use it
  ]
};