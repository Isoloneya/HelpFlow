/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#F1F3EE',
        surface: '#FFFFFF',
        sunken: '#E7EAE3',
        ink: '#171B1A',
        muted: '#5B665F',
        line: '#D9DFD3',
        bar: '#14181F',
        'bar-ink': '#E7EAEE',
        'bar-muted': '#8891A0',
        'bar-accent': '#5FC9AE',
        accent: '#1F6F5C',
        ok: '#1F6F5C',
        risk: '#B87B22',
        breach: '#B8402F',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
