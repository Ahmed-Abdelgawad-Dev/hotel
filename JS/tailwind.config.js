/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        '../hotel/templates/**/*.html',
        '../hotel/**/templates/**/*.html',
        '../hotel/static/js/**/*.js',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                gold: {
                    50: '#fbf8ea',
                    100: '#f5efc9',
                    200: '#ebde9a',
                    300: '#dfc763',
                    400: '#d4af37',
                    500: '#b99225',
                    600: '#a2781d',
                    700: '#835b1b',
                    800: '#6e4a1c',
                    900: '#5c3e1b',
                },
                dark: {
                    900: '#1a1a1a',
                    800: '#262626',
                    700: '#404040',
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                serif: ['Playfair Display', 'serif'],
            }
        }
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
