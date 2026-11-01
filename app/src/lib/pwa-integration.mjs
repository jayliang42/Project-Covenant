// Small Astro integration that writes dist/sw.js after every build.
// The service worker precaches every built file so the whole app works
// offline once installed, and bumps its cache name whenever content changes.
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

function walk(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

export default function pwa() {
  let base = '/';
  return {
    name: 'covenant-pwa',
    hooks: {
      'astro:config:done': ({ config }) => {
        base = config.base.endsWith('/') ? config.base : `${config.base}/`;
      },
      'astro:build:done': ({ dir, logger }) => {
        const out = fileURLToPath(dir);
        const files = walk(out)
          .filter((f) => !f.endsWith('sw.js') && !f.endsWith('.map'))
          .filter((f) => !f.includes(`${sep}repo-assets${sep}illustrations${sep}`)); // large JPGs: cached on use
        const hash = createHash('sha256');
        const urls = files.map((f) => {
          hash.update(f).update(readFileSync(f));
          const rel = relative(out, f).split(sep).join('/');
          return base + rel.replace(/(^|\/)index\.html$/, '$1');
        });
        const version = hash.digest('hex').slice(0, 12);
        const template = readFileSync(new URL('./sw-template.js', import.meta.url), 'utf8');
        const sw = template
          .replace('__VERSION__', version)
          .replace('__BASE__', base)
          .replace('/*__PRECACHE__*/ []', JSON.stringify(urls));
        writeFileSync(join(out, 'sw.js'), sw);
        logger.info(`sw.js written: ${urls.length} files, cache ${version}`);
      },
    },
  };
}
