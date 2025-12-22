/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './hotel/templates/**/*.html',
        './hotel/**/templates/**/*.html',
        './hotel/static/js/**/*.js',
    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
