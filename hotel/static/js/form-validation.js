/**
 * Il Mercato Hotel - Form Validation with Zod
 * Provides client-side form validation for authentication forms
 */

// Check if Zod is loaded
if (typeof z === 'undefined') {
  console.warn('Zod library not loaded. Form validation will be limited.');
}

// Validation schemas
const schemas = {
  email: z.string().email('Please enter a valid email address'),

  password: z.string()
    .min(8, 'Password must be at least 8 characters long')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),

  login: z.object({
    login: z.string().email('Please enter a valid email address'),
    password: z.string().min(1, 'Password is required'),
  }),

  signup: z.object({
    email: z.string().email('Please enter a valid email address'),
    password1: z.string()
      .min(8, 'Password must be at least 8 characters long')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    password2: z.string().min(1, 'Please confirm your password'),
  }).refine((data) => data.password1 === data.password2, {
    message: "Passwords don't match",
    path: ["password2"],
  }),

  passwordReset: z.object({
    email: z.string().email('Please enter a valid email address'),
  }),

  passwordChange: z.object({
    oldpassword: z.string().min(1, 'Current password is required'),
    password1: z.string()
      .min(8, 'Password must be at least 8 characters long')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    password2: z.string().min(1, 'Please confirm your new password'),
  }).refine((data) => data.password1 === data.password2, {
    message: "Passwords don't match",
    path: ["password2"],
  }),
};

/**
 * Display error message for a field
 */
function showError(fieldName, message) {
  const field = document.querySelector(`[name="${fieldName}"]`);
  if (!field) return;

  // Remove existing error
  const existingError = field.parentElement.querySelector('.validation-error');
  if (existingError) {
    existingError.remove();
  }

  // Add new error message
  const errorDiv = document.createElement('div');
  errorDiv.className = 'validation-error mt-2 text-sm text-red-600 dark:text-red-400';
  errorDiv.textContent = message;
  field.parentElement.appendChild(errorDiv);

  // Add error styling to field
  field.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
  field.classList.remove('border-gray-300', 'dark:border-gray-600');
}

/**
 * Clear error message for a field
 */
function clearError(fieldName) {
  const field = document.querySelector(`[name="${fieldName}"]`);
  if (!field) return;

  const errorDiv = field.parentElement.querySelector('.validation-error');
  if (errorDiv) {
    errorDiv.remove();
  }

  // Remove error styling
  field.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
  field.classList.add('border-gray-300', 'dark:border-gray-600');
}

/**
 * Clear all errors in a form
 */
function clearAllErrors(form) {
  const errors = form.querySelectorAll('.validation-error');
  errors.forEach(error => error.remove());

  const fields = form.querySelectorAll('input, textarea');
  fields.forEach(field => {
    field.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
    field.classList.add('border-gray-300', 'dark:border-gray-600');
  });
}

/**
 * Validate form on submit
 */
function validateForm(form, schemaName) {
  if (typeof z === 'undefined') {
    return true; // Skip validation if Zod is not loaded
  }

  const schema = schemas[schemaName];
  if (!schema) {
    console.warn(`Schema "${schemaName}" not found`);
    return true;
  }

  // Get form data
  const formData = new FormData(form);
  const data = {};
  for (const [key, value] of formData.entries()) {
    data[key] = value;
  }

  // Clear previous errors
  clearAllErrors(form);

  // Validate
  try {
    schema.parse(data);
    return true;
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.errors.forEach(err => {
        const fieldName = err.path[0];
        showError(fieldName, err.message);
      });
    }
    return false;
  }
}

/**
 * Real-time validation on input
 */
function setupRealtimeValidation(form, schemaName) {
  if (typeof z === 'undefined') return;

  const schema = schemas[schemaName];
  if (!schema) return;

  const fields = form.querySelectorAll('input, textarea');
  fields.forEach(field => {
    field.addEventListener('blur', () => {
      const fieldName = field.getAttribute('name');
      const value = field.value;

      // Try to validate just this field
      if (schema.shape && schema.shape[fieldName]) {
        try {
          schema.shape[fieldName].parse(value);
          clearError(fieldName);
        } catch (error) {
          if (error instanceof z.ZodError) {
            showError(fieldName, error.errors[0].message);
          }
        }
      }
    });

    // Clear error on input
    field.addEventListener('input', () => {
      const fieldName = field.getAttribute('name');
      clearError(fieldName);
    });
  });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
  // Login form
  const loginForm = document.querySelector('form[action*="login"]');
  if (loginForm) {
    setupRealtimeValidation(loginForm, 'login');
    loginForm.addEventListener('submit', (e) => {
      if (!validateForm(loginForm, 'login')) {
        e.preventDefault();
      }
    });
  }

  // Signup form
  const signupForm = document.querySelector('form[action*="signup"]');
  if (signupForm) {
    setupRealtimeValidation(signupForm, 'signup');
    signupForm.addEventListener('submit', (e) => {
      if (!validateForm(signupForm, 'signup')) {
        e.preventDefault();
      }
    });
  }

  // Password reset form
  const resetForm = document.querySelector('form[action*="password/reset"]');
  if (resetForm && !resetForm.querySelector('[name="password1"]')) {
    setupRealtimeValidation(resetForm, 'passwordReset');
    resetForm.addEventListener('submit', (e) => {
      if (!validateForm(resetForm, 'passwordReset')) {
        e.preventDefault();
      }
    });
  }

  // Password change form
  const changeForm = document.querySelector('form[action*="password/change"]');
  if (changeForm) {
    setupRealtimeValidation(changeForm, 'passwordChange');
    changeForm.addEventListener('submit', (e) => {
      if (!validateForm(changeForm, 'passwordChange')) {
        e.preventDefault();
      }
    });
  }
}

// Initialize on DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initFormValidation);
} else {
  initFormValidation();
}
