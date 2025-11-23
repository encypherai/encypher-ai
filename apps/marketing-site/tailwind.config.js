/** @type {import('tailwindcss').Config} */
const config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '2rem',
        lg: '4rem',
        xl: '5rem',
        '2xl': '6rem',
      },
      screens: {
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
      },
    },
    extend: {
      colors: {
        'delft-blue': {
          DEFAULT: '#1b2f50',
        },
        'blue-ncs': {
          DEFAULT: '#2a87c4',
        },
        'columbia-blue': {
          DEFAULT: '#b7d5ed',
        },
        'rosy-brown': {
          DEFAULT: '#ba8790',
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        "pulse-slow": {
          '0%, 100%': { opacity: 0.4 },
          '50%': { opacity: 0.8 },
        },
        "pulse-slower": {
          '0%, 100%': { opacity: 0.3 },
          '50%': { opacity: 0.6 },
        },
        "data-flow": {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        "data-flow-reverse": {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(-100%)' },
        },
        "fade-in-out": {
          '0%, 100%': { opacity: 0 },
          '50%': { opacity: 0.3 },
        },
        "fade-in-out-delay": {
          '0%, 20%, 80%, 100%': { opacity: 0 },
          '50%': { opacity: 0.3 },
        },
        "border-pulse": {
          '0%, 100%': { opacity: 0.3 },
          '50%': { opacity: 0.6 },
        },
        "shine": {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        "typing": {
          '0%': { width: '0%' },
          '10%': { width: '0%' },
          '40%': { width: '100%' },
          '60%': { width: '100%' },
          '100%': { width: '0%' },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "pulse-slow": "pulse-slow 4s ease-in-out infinite",
        "pulse-slower": "pulse-slower 6s ease-in-out infinite",
        "data-flow": "data-flow 8s linear infinite",
        "data-flow-reverse": "data-flow-reverse 10s linear infinite",
        "fade-in-out": "fade-in-out 8s ease-in-out infinite",
        "fade-in-out-delay": "fade-in-out-delay 12s ease-in-out infinite",
        "border-pulse": "border-pulse 4s ease-in-out infinite",
        "shine": "shine 3s ease-in-out infinite",
        "typing": "typing 10s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

module.exports = config;
