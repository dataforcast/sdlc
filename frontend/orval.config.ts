import { defineConfig } from 'orval';

const backendUrl = process.env.API_BASE_URL ?? 'http://127.0.0.1:8010';

export default defineConfig({
  backend: {
    input: {
      target: `${backendUrl}/openapi.json`,
    },
    output: {
      mode: 'single',
      client: 'axios-functions',
      target: './src/api/generated/client.ts',
      schemas: './src/api/generated/models',
      override: {
        mutator: {
          path: './src/api/http-client.ts',
          name: 'apiClient',
        },
      },
    },
  },
});
