const { FlatCompat } = require('@eslint/eslintrc');
const js = require('@eslint/js');
const path = require('path');

const compat = new FlatCompat({
  baseDirectory: path.resolve(__dirname),
  recommendedConfig: js.configs.recommended,
});

module.exports = [
  ...compat.extends('expo', 'prettier'),
  {
    rules: {
      // Prevent importing deprecated legacy client
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['**/api/client', '**/api/client.ts'],
              message:
                '❌ Legacy client is deprecated. Use SDK from "@/src/shared/api/sdk" instead. ' +
                'For API calls, use TanStack Query options/mutations (e.g., getMyProfileOptions()). ' +
                'For Signed URL uploads, use independent fetch().',
            },
          ],
        },
      ],
    },
  },
];

