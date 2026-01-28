import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4A90E2',
        'primary-light': '#7BB4F5',
        secondary: '#50C878',
        'secondary-light': '#80E0A7',
        background: '#F8FAFC',
        surface: '#FFFFFF',
        border: '#E2E8F0',
        'text-primary': '#1A202C',
        'text-secondary': '#718096',
        'text-tertiary': '#A0AEC0',
        success: '#38A169',
        warning: '#D69E2E',
        error: '#E53E3E',
        info: '#4299E1',
        'accent-warm': '#FF6B6B',
        'accent-cool': '#9F7AEA',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
export default config