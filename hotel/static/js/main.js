/**
 * Il Mercato Hotel - Main Site JavaScript
 * Handles Alpine.js initialization for main site pages
 */

// Initialize scroll progress tracking
document.addEventListener('alpine:init', () => {
  // Track scroll progress
  window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrollProgress = (winScroll / height) * 100;

    // Update scroll progress bar if it exists
    const progressBar = document.querySelector('[data-scroll-progress]');
    if (progressBar) {
      progressBar.style.width = scrollProgress + '%';
    }

    // Show/hide back to top button
    const backToTopBtn = document.querySelector('[data-back-to-top]');
    if (backToTopBtn) {
      if (winScroll > 500) {
        backToTopBtn.classList.remove('hidden');
      } else {
        backToTopBtn.classList.add('hidden');
      }
    }
  });
});
