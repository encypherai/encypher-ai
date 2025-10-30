/** @type {import('tailwindcss').Config} */
const designSystemConfig = require('../../packages/design-system/tailwind.config');

module.exports = {
  ...designSystemConfig,
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    // Include design system components
    '../../packages/design-system/src/**/*.{js,ts,jsx,tsx}',
  ],
};
