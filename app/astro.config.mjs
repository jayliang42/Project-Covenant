import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import rehypeBilingual from './src/lib/rehype-bilingual.mjs';
import pwa from './src/lib/pwa-integration.mjs';

// BASE_PATH lets the same build run at a domain root, under a GitHub Pages
// sub-path (e.g. BASE_PATH=/Project-Covenant/learn/), or inside a Capacitor shell.
const base = process.env.BASE_PATH || '/';

export default defineConfig({
  base,
  site: process.env.SITE_URL || undefined,
  trailingSlash: 'always',
  build: { format: 'directory' },
  markdown: {
    // rehypeBilingual tags each paragraph as Chinese or English for the 中文/EN/中英 switch.
    processor: unified({ rehypePlugins: [rehypeBilingual] }),
  },
  integrations: [pwa()],
  devToolbar: { enabled: false },
});
