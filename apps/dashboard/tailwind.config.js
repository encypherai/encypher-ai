/** @type {import('tailwindcss').Config} */
const designSystemConfig = require('./design-system/tailwind.config');

module.exports = {
  ...designSystemConfig,
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    // Include design system components (bundled locally for deployment)
    './design-system/src/**/*.{js,ts,jsx,tsx}',
  ],
};
