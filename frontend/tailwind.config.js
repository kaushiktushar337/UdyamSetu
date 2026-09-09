/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        udyam: {
          50: '#f1f8ee',
          100: '#e0f0d9',
          200: '#c5dfbb',
          300: '#a2c890',
          400: '#7eaf68',
          500: '#5f944d',
          600: '#47783a',
          700: '#3b6033',
          800: '#324d2d',
        }
      },
      boxShadow: {
        soft: '0 10px 30px rgba(37, 70, 31, 0.08)',
        card: '0 4px 20px rgba(37, 70, 31, 0.06)',
      },
      backgroundImage: {
        'page-glow': 'radial-gradient(circle at 15% 20%, rgba(177,216,157,.18), transparent 30%), radial-gradient(circle at 90% 15%, rgba(218,236,203,.24), transparent 34%)',
      }
    },
  },
  plugins: [],
}
