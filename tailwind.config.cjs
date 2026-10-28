module.exports = {
  content: ['./templates/**/*.html', './static/js/**/*.js'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        serif: ['Cormorant Garamond', 'Georgia', 'serif'],
      },
      colors: {
        canvas: 'var(--q-bg)', surface: 'var(--q-surface)', ink: 'var(--q-text)',
        muted: 'var(--q-muted)', line: 'var(--q-border)', soft: 'var(--q-soft)',
        accent: 'var(--q-accent-text)', 'accent-line': 'var(--q-accent)',
        'accent-soft': 'var(--q-accent-soft)', action: 'var(--q-action)',
        'action-hover': 'var(--q-action-hover)', 'on-action': 'var(--q-on-action)', 'on-ink': 'var(--q-bg)',
        success: 'var(--q-success)', danger: 'var(--q-danger)',
      },
    },
  },
  plugins: [],
};
