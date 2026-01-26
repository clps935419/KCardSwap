/**
 * OpenAPI SDK Generation Configuration
 *
 * This configuration tells hey-api to:
 * 1. Read OpenAPI spec from repo root (../../openapi/openapi.json)
 * 2. Generate TypeScript SDK to src/shared/api/generated/
 * 3. Use axios as the HTTP client
 */

import { defineConfig } from '@hey-api/openapi-ts'

export default defineConfig({
  client: 'axios',
  input: '../../openapi/openapi.json',
  output: './src/shared/api/generated',
})
