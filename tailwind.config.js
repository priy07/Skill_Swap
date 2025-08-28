/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",  // All HTML files in templates folder
    "./app.py"                // Optional: if you have Tailwind classes in Python strings
  ],
  theme: {
    darkMode: 'class',
    extend: {},
  },
  plugins: [],
}

