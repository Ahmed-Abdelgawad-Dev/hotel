/**
 * Il Mercato Hotel - Main Application JavaScript
 * Handles theme management, scroll tracking, and UI interactions
 */

// Alpine.js data initialization
document.addEventListener('alpine:init', () => {
  // You can add global Alpine stores here if needed
  Alpine.store('theme', {
    dark: localStorage.getItem('theme') === 'dark' ||
          (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches),

    toggle() {
      this.dark = !this.dark;
      localStorage.setItem('theme', this.dark ? 'dark' : 'light');
      this.updateDOM();
    },

    updateDOM() {
      if (this.dark) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },

    init() {
      this.updateDOM();
    }
  });
});

// Initialize theme on page load
window.addEventListener('DOMContentLoaded', () => {
  const theme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (theme === 'dark' || (!theme && prefersDark)) {
    document.documentElement.classList.add('dark');
  }
});
