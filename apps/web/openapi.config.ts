/**
 * OpenAPI SDK Generation Configuration
 *
 * This configuration tells hey-api to:
 * 1. Read OpenAPI spec from repo root (../../openapi/openapi.json)
 * 2. Generate TypeScript SDK to src/shared/api/generated/
 * 3. Use axios as the HTTP client
 * 4. Generate TanStack Query hooks for React
 */

export default {
  client: '@hey-api/client-axios',
  input: '../../openapi/openapi.json',
  output: {
    path: './src/shared/api/generated',
  },
  plugins: [
    '@hey-api/typescript',
    '@hey-api/sdk',
    {
      name: '@tanstack/react-query',
      infiniteQueryOptions: true,
      mutationOptions: true,
      queryOptions: true,
    },
  ],
}
