// @ts-check
import { readdirSync } from 'node:fs';
import { URL, fileURLToPath } from 'node:url';
import { defineConfig, envField } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Each file in ../clientes/ is a client; CLIENTE picks which one is built (RF-01).
// Unknown names are rejected by the astro:env enum below, before any page renders.
const clientes = readdirSync(new URL('../clientes/', import.meta.url))
  .filter((arquivo) => arquivo.endsWith('.json'))
  .map((arquivo) => arquivo.replace(/\.json$/, ''));

// https://astro.build/config
export default defineConfig({
  env: {
    schema: {
      CLIENTE: envField.enum({
        context: 'server',
        access: 'public',
        values: clientes,
        default: 'demo-bpo',
      }),
    },
  },
  vite: {
    plugins: [tailwindcss()],
    // clientes/ and schemas/ live outside web/; astro dev must be allowed to read them.
    server: {
      fs: {
        allow: [fileURLToPath(new URL('../', import.meta.url))],
      },
    },
  },
});
