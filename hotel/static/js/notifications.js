/**
 * Il Mercato Hotel - Notification System
 * Modern toast notifications positioned at bottom-left
 */

class NotificationManager {
  constructor() {
    this.container = null;
    this.notifications = [];
    this.init();
  }

  init() {
    // Create notification container
    this.container = document.createElement('div');
    this.container.id = 'notification-container';
    this.container.className = 'fixed bottom-6 left-6 z-50 space-y-3 max-w-sm w-full pointer-events-none';
    this.container.setAttribute('aria-live', 'polite');
    this.container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(this.container);
  }

  /**
   * Show a notification
   * @param {string} message - The message to display
   * @param {string} type - Type: 'success', 'error', 'warning', 'info'
   * @param {number} duration - Duration in milliseconds (default: 5000)
   */
  show(message, type = 'info', duration = 5000) {
    const notification = this.createNotification(message, type, duration);
    this.container.appendChild(notification);
    this.notifications.push(notification);

    // Animate in
    setTimeout(() => {
      notification.classList.remove('translate-x-[-120%]', 'opacity-0');
      notification.classList.add('translate-x-0', 'opacity-100');
    }, 10);

    // Auto dismiss
    if (duration > 0) {
      setTimeout(() => {
        this.dismiss(notification);
      }, duration);
    }

    return notification;
  }

  createNotification(message, type, duration) {
    const notification = document.createElement('div');
    notification.className = `
      transform transition-all duration-300 ease-out
      translate-x-[-120%] opacity-0
      pointer-events-auto
      flex items-start p-4 rounded-xl shadow-2xl backdrop-blur-md border-l-4
      ${this.getTypeClasses(type)}
    `.trim().replace(/\s+/g, ' ');

    const icon = this.getIcon(type);
    const closeButton = this.createCloseButton(notification);

    notification.innerHTML = `
      <div class="flex-shrink-0">
        ${icon}
      </div>
      <div class="ml-3 flex-1">
        <p class="text-sm font-medium">${this.escapeHtml(message)}</p>
      </div>
      ${closeButton}
    `;

    // Add close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.dismiss(notification));
    }

    // Add progress bar if duration is set
    if (duration > 0) {
      const progressBar = document.createElement('div');
      progressBar.className = 'absolute bottom-0 left-0 h-1 bg-current opacity-30 rounded-bl-xl transition-all';
      progressBar.style.width = '100%';
      progressBar.style.transitionDuration = `${duration}ms`;
      progressBar.style.transitionProperty = 'width';
      notification.style.position = 'relative';
      notification.appendChild(progressBar);

      setTimeout(() => {
        progressBar.style.width = '0%';
      }, 10);
    }

    return notification;
  }

  getTypeClasses(type) {
    const classes = {
      success: 'bg-green-50/95 dark:bg-green-900/80 text-green-800 dark:text-green-100 border-green-500',
      error: 'bg-red-50/95 dark:bg-red-900/80 text-red-800 dark:text-red-100 border-red-500',
      warning: 'bg-yellow-50/95 dark:bg-yellow-900/80 text-yellow-800 dark:text-yellow-100 border-yellow-500',
      info: 'bg-blue-50/95 dark:bg-blue-900/80 text-blue-800 dark:text-blue-100 border-blue-500',
    };
    return classes[type] || classes.info;
  }

  getIcon(type) {
    const icons = {
      success: `
        <svg class="h-6 w-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      `,
      error: `
        <svg class="h-6 w-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      `,
      warning: `
        <svg class="h-6 w-6 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      `,
      info: `
        <svg class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      `,
    };
    return icons[type] || icons.info;
  }

  createCloseButton(notification) {
    return `
      <button type="button" class="notification-close ml-3 flex-shrink-0 inline-flex text-current hover:opacity-70 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current rounded-lg transition-opacity">
        <span class="sr-only">Close</span>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    `;
  }

  dismiss(notification) {
    notification.classList.add('translate-x-[-120%]', 'opacity-0');
    notification.classList.remove('translate-x-0', 'opacity-100');

    setTimeout(() => {
      if (notification.parentElement) {
        notification.parentElement.removeChild(notification);
      }
      const index = this.notifications.indexOf(notification);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    }, 300);
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Convenience methods
  success(message, duration = 5000) {
    return this.show(message, 'success', duration);
  }

  error(message, duration = 5000) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration = 5000) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration = 5000) {
    return this.show(message, 'info', duration);
  }
}

// Initialize notification manager
const notifications = new NotificationManager();

// Make it globally available
window.notifications = notifications;

// Auto-convert Django messages to notifications
document.addEventListener('DOMContentLoaded', () => {
  // Find Django message elements
  const messageElements = document.querySelectorAll('[role="alert"]');

  messageElements.forEach((element) => {
    const message = element.textContent.trim();
    const classList = element.className;

    // Determine type based on classes
    let type = 'info';
    if (classList.includes('success') || classList.includes('green')) {
      type = 'success';
    } else if (classList.includes('error') || classList.includes('red') || classList.includes('danger')) {
      type = 'error';
    } else if (classList.includes('warning') || classList.includes('yellow')) {
      type = 'warning';
    }

    // Show notification
    notifications.show(message, type);

    // Hide original message element
    element.style.display = 'none';
  });
});
