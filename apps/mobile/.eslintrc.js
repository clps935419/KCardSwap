module.exports = {
  root: true,
  extends: [
    'expo',
    'prettier',
  ],
  plugins: [
    'prettier',
  ],
  rules: {
    'prettier/prettier': 'warn',
    '@typescript-eslint/no-unused-vars': 'warn',
    'react-hooks/exhaustive-deps': 'warn',
  },
};
