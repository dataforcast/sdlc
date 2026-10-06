/** @type {import('orval').OrvalConfig } */
module.exports = {
  ticket: {
    output: {
      mode: 'tags-split',
      target: './src/api/generated/api.client.ts',
      schemas: './src/api/generated/models',
      client: 'react-query',
      clean: true,
      prettify: true,
      mock: false,
    },
    input: {
      target: 'http://localhost:8000/backend/openapi.json',
    },
  },
};
