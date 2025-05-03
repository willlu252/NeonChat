module.exports = {
  content: [
    "./static/**/*.html",
    "./static/**/*.js"
  ],
  theme: {
    extend: {
      colors: {
        'neon-blue': '#00f0ff',
        'neon-pink': '#ff00ff', 
        'neon-purple': '#9d00ff',
        'neon-green': '#00ff9d',
        'dark-bg': '#0a0a14',
        'darker-bg': '#050508',
        'tron-white': '#f8f8ff',
        'tron-grid': 'rgba(0, 240, 255, 0.1)'
      },
      boxShadow: {
        'neon': '0 0 10px theme("colors.neon-blue"), 0 0 20px theme("colors.neon-blue")',
        'neon-pink': '0 0 10px theme("colors.neon-pink"), 0 0 20px theme("colors.neon-pink")',
        'neon-strong': '0 0 15px theme("colors.neon-blue"), 0 0 30px theme("colors.neon-blue")',
        'neon-inner': 'inset 0 0 10px theme("colors.neon-blue"), inset 0 0 20px rgba(0, 240, 255, 0.5)',
        'hud': '0 0 0 1px theme("colors.neon-blue"), 0 0 15px theme("colors.neon-blue")'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'flow': 'flow 8s linear infinite',
        'typewriter': 'typing 3.5s steps(40, end)',
        'blink-caret': 'blink-caret .75s step-end infinite',
        'border-flow': 'border-flow 4s linear infinite'
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px theme("colors.neon-blue"), 0 0 10px theme("colors.neon-blue")' },
          '100%': { boxShadow: '0 0 15px theme("colors.neon-blue"), 0 0 30px theme("colors.neon-blue")' }
        },
        flow: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' }
        },
        typing: {
          'from': { width: '0' },
          'to': { width: '100%' }
        },
        'blink-caret': {
          'from, to': { borderColor: 'transparent' },
          '50%': { borderColor: 'theme("colors.neon-blue")' }
        },
        'border-flow': {
          '0%': { borderColor: 'theme("colors.neon-blue")' },
          '50%': { borderColor: 'theme("colors.neon-pink")' },
          '100%': { borderColor: 'theme("colors.neon-blue")' }
        }
      },
      backgroundImage: {
        'tron-grid': 'linear-gradient(theme("colors.tron-grid") 1px, transparent 1px), linear-gradient(90deg, theme("colors.tron-grid") 1px, transparent 1px)',
        'neon-gradient': 'linear-gradient(45deg, theme("colors.neon-blue"), theme("colors.neon-pink"), theme("colors.neon-purple"), theme("colors.neon-blue"))'
      },
      backgroundSize: {
        'tron-grid-size': '30px 30px'
      }
    }
  },
  plugins: [],
}
