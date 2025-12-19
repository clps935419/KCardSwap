import { defineConfig } from '@hey-api/openapi-ts';

/**
 * Hey API OpenAPI Code Generator Configuration
 * 
 * Generates TypeScript SDK from OpenAPI specification with:
 * - Axios client for HTTP requests
 * - TanStack Query hooks for React components
 * - Type-safe request/response interfaces
 * 
 * Important: OpenAPI paths already include /api/v1 prefix, 
 * so baseUrl should be host-only (e.g., http://localhost:8080)
 * to avoid /api/v1/api/v1 duplication.
 */
export default defineConfig({
  client: '@hey-api/client-axios',
  input: '../../openapi/openapi.json',
  output: {
    path: 'src/shared/api/generated',
    format: 'prettier',
    lint: 'eslint',
  },
  plugins: [
    '@tanstack/react-query',
    {
      enums: 'javascript',
      name: '@hey-api/typescript',
    },
  ],
});
