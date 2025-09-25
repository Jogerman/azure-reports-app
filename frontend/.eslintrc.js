/* eslint-disable no-undef */
// frontend/.eslintrc.js
module.exports = {
  env: {
    browser: true,
    es2020: true,
    node: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 11,
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
  },
  rules: {
    'no-unused-vars': 'off',
    'no-undef': 'off',
    'react-refresh/only-export-components': 'off',
  },
  settings: {
    react: { version: 'detect' },
  },
}