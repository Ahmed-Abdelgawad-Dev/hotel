# Il Mercato Hotel - Static Assets Setup

This document provides instructions for setting up local static assets (JavaScript libraries, CSS frameworks, and fonts) to replace CDN dependencies.

## Overview

The project now uses local static files instead of CDN links for:
- **Alpine.js** - JavaScript framework for interactivity
- **Tailwind CSS** - Utility-first CSS framework
- **Zod** - TypeScript-first schema validation
- **Google Fonts** - Inter and Playfair Display fonts

## Quick Start

### 1. Install Dependencies

```bash
cd /run/media/sonto/Storage/Projects/hotel
npm install
```

This will automatically:
- Install all npm packages
- Copy Alpine.js and Zod to `hotel/static/js/`
- Install Tailwind CSS and plugins

### 2. Build Tailwind CSS

```bash
npm run build
```

This compiles the Tailwind CSS from `hotel/static/css/input.css` to `hotel/static/css/tailwind.css` with all your custom configurations.

### 3. Download Fonts (Optional)

If you want to use locally hosted fonts instead of Google Fonts CDN:

```bash
chmod +x download_assets.sh
./download_assets.sh
```

This downloads Inter and Playfair Display font files to `hotel/static/fonts/`.

## Project Structure

```
hotel/
├── static/
│   ├── css/
│   │   ├── input.css          # Tailwind source file
│   │   ├── tailwind.css       # Compiled Tailwind CSS (generated)
│   │   └── project.css        # Additional custom styles
│   ├── js/
│   │   ├── alpine.min.js      # Alpine.js (copied from node_modules)
│   │   ├── zod.min.js         # Zod validation (copied from node_modules)
│   │   ├── app.js             # Main application JavaScript
│   │   ├── main.js            # Main site specific JavaScript
│   │   ├── form-validation.js # Form validation with Zod
│   │   └── notifications.js   # Toast notification system
│   ├── fonts/
│   │   ├── inter-*.woff2      # Inter font files
│   │   └── playfair-*.woff2   # Playfair Display font files
│   └── images/
│       └── ...
├── templates/
│   ├── base.html              # Main site base template
│   ├── base_auth.html         # Authentication pages base template
│   └── ...
├── package.json               # NPM dependencies
├── tailwind.config.js         # Tailwind configuration
├── download_assets.sh         # Font download script
└── scripts/
    └── copy-assets.js         # NPM postinstall script
```

## Features

### 1. Form Validation with Zod

Client-side form validation is automatically applied to authentication forms:

- **Login Form** - Email and password validation
- **Signup Form** - Email, password strength, and password confirmation
- **Password Reset** - Email validation
- **Password Change** - Current password, new password strength, and confirmation

Validation triggers on:
- Form submission (prevents invalid submissions)
- Field blur (validates after user leaves a field)
- Real-time feedback with error messages

### 2. Toast Notifications

Beautiful toast notifications appear at the **bottom-left** of the screen.

**Features:**
- Auto-dismiss after 5 seconds
- Manual dismiss with close button
- Progress bar showing time remaining
- Slide-in animation from left
- Four types: success, error, warning, info
- Dark mode support

**Usage in JavaScript:**
```javascript
// Success notification
notifications.success('Login successful!');

// Error notification
notifications.error('Invalid credentials');

// Warning notification
notifications.warning('Session expiring soon');

// Info notification
notifications.info('New update available');

// Custom duration (in milliseconds)
notifications.success('Saved!', 3000);
```

**Auto-conversion:**
Django messages are automatically converted to toast notifications.

### 3. Responsive Authentication Pages

All authentication pages (`/accounts/*`) are:
- Fully responsive (mobile, tablet, desktop)
- Separate from main site (no navbar/footer)
- Centered with logo at top
- Theme toggle (dark/light mode)
- Home button to return to main site
- Glass-morphism design with gradients

### 4. Theme Management

Dark mode is automatically handled with:
- System preference detection
- localStorage persistence
- Smooth transitions
- Toggle buttons on all pages

## NPM Scripts

```bash
# Install dependencies and copy assets
npm install

# Build Tailwind CSS (production)
npm run build

# Watch mode for development
npm run build:watch

# Complete setup (install + build)
npm run setup
```

## Development Workflow

### Making Style Changes

1. Edit `hotel/static/css/input.css` or templates
2. Run `npm run build:watch` in a terminal
3. Tailwind will automatically rebuild on file changes
4. Refresh browser to see changes

### Adding New JavaScript

1. Create new `.js` file in `hotel/static/js/`
2. Include it in template:
   ```html
   <script defer src="{% static 'js/your-file.js' %}"></script>
   ```

### Customizing Tailwind

Edit `tailwind.config.js`:
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // Add custom colors
      },
    }
  },
}
```

Then rebuild: `npm run build`

## Validation Schemas

Form validation schemas in `form-validation.js`:

```javascript
const schemas = {
  login: z.object({
    login: z.string().email(),
    password: z.string().min(1),
  }),

  signup: z.object({
    email: z.string().email(),
    password1: z.string()
      .min(8)
      .regex(/[A-Z]/)
      .regex(/[a-z]/)
      .regex(/[0-9]/),
    password2: z.string(),
  }).refine((data) => data.password1 === data.password2),

  // ... more schemas
};
```

## Troubleshooting

### Tailwind CSS not applying

1. Make sure you ran `npm run build`
2. Check that `tailwind.css` exists in `hotel/static/css/`
3. Verify static files are being served correctly
4. Run Django's `collectstatic` if in production

### Form validation not working

1. Check browser console for JavaScript errors
2. Verify `zod.min.js` is loaded before `form-validation.js`
3. Ensure form has correct `action` attribute matching validation schemas

### Notifications not showing

1. Check that `notifications.js` is loaded
2. Verify Django messages have correct tags (info, success, error, warning)
3. Check browser console for errors

### Fonts not loading

1. Ensure font files are in `hotel/static/fonts/`
2. Run `./download_assets.sh` to download fonts
3. Check `input.css` has correct `@font-face` declarations
4. Rebuild Tailwind: `npm run build`

## Production Deployment

Before deploying to production:

1. **Build assets:**
   ```bash
   npm run build
   ```

2. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Verify all assets are present:**
   - `static/css/tailwind.css`
   - `static/js/alpine.min.js`
   - `static/js/zod.min.js`
   - `static/fonts/*.woff2` (if using local fonts)

4. **Configure web server** to serve static files from `staticfiles/` directory

## Browser Support

- **Alpine.js**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Tailwind CSS**: All browsers with CSS Grid support
- **Zod**: Modern browsers with ES6+ support
- **Fonts**: WOFF2 format (all modern browsers)

## Additional Notes

- **No CDN required** - All assets are self-hosted
- **Offline-ready** - Works without internet connection
- **Fast loading** - No external network requests for assets
- **Version control** - All assets versioned in your repository
- **Customizable** - Full control over all libraries and styles

## Support

For issues or questions:
1. Check browser console for errors
2. Verify all npm packages are installed
3. Ensure Tailwind CSS is built
4. Check Django static files configuration

## License

This project uses the following open-source libraries:
- Alpine.js (MIT)
- Tailwind CSS (MIT)
- Zod (MIT)
- Inter font (SIL Open Font License)
- Playfair Display (SIL Open Font License)
