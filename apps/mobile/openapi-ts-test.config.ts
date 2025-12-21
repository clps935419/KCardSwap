import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  client: '@hey-api/client-axios',
  input: '../../openapi/openapi.json',
  output: {
    path: 'src/shared/api/generated_test',
    format: 'prettier',
    lint: 'eslint',
  },
  plugins: [
    {
      enums: 'javascript',
      name: '@hey-api/typescript',
    },
  ],
});
