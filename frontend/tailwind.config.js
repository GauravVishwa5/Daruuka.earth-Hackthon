/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Forest — primary brand
        forest: {
          950: '#050f09',
          900: '#092e1a',
          800: '#0d3b24',
          700: '#145a35',
          600: '#197044',
          500: '#238653',
        },
        // Nature accent
        nature: {
          600: '#078a4b',
          500: '#0a9f57',
          400: '#35b978',
          300: '#79d49d',
          200: '#b5eacc',
        },
        // Canvas / natural neutrals
        canvas: '#f5f7f3',
        mist: '#e3ece7',
        surface: '#ffffff',
        'soft-surface': '#eef3ee',
        // Semantic environmental states
        state: {
          healthy: '#2e8b57',
          watch: '#c28a2c',
          'high-risk': '#c96a32',
          critical: '#b64040',
          info: '#477c86',
        },
        // Text neutrals (warm)
        ink: {
          900: '#12251b',
          700: '#2c4438',
          500: '#4a6456',
          300: '#65736b',
          100: '#a8b9b0',
        },
        // Border
        line: {
          strong: '#c5d2cb',
          DEFAULT: '#d5ded8',
          soft: '#e3ece7',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['IBM Plex Mono', 'Menlo', 'Consolas', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1rem' }],
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(9,46,26,0.06), 0 1px 2px -1px rgba(9,46,26,0.04)',
        panel: '0 4px 16px 0 rgba(9,46,26,0.08)',
        modal: '0 20px 60px -12px rgba(9,46,26,0.28)',
      },
    },
  },
  plugins: [],
}
