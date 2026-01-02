/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0b0b0d", // Obsidian Dark
                surface: "#1e1e24",
                primary: "#FFFBEB",    // Yellowish White (Amber-50)
                secondary: "#5a9bd4",  // Blue Accent
            },
            fontFamily: {
                sans: ['Rajdhani', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
