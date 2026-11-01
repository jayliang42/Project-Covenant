// Copies the repository's shared art and maps into public/repo-assets so the
// app can reuse them without duplicating files in git.
import { cpSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const appRoot = join(dirname(fileURLToPath(import.meta.url)), '..');
const repoAssets = join(appRoot, '..', 'assets');
const target = join(appRoot, 'public', 'repo-assets');

rmSync(target, { recursive: true, force: true });
mkdirSync(target, { recursive: true });
for (const folder of ['art', 'maps', 'illustrations']) {
  const from = join(repoAssets, folder);
  if (existsSync(from)) cpSync(from, join(target, folder), { recursive: true });
}
console.log(`synced repo assets -> ${target}`);

// App icons: PNGs are generated from the SVG sources so the repository only
// stores reviewable text files (see scripts/audit_publication.py at the root).
const sharp = (await import('sharp')).default;
const icons = join(appRoot, 'public', 'icons');
for (const [src, out, size] of [
  ['icon.svg', 'icon-192.png', 192],
  ['icon.svg', 'icon-512.png', 512],
  ['maskable.svg', 'maskable-512.png', 512],
  ['maskable.svg', 'apple-touch-icon.png', 180],
]) {
  await sharp(join(icons, src), { density: 300 }).resize(size, size).png().toFile(join(icons, out));
}
console.log('generated PNG icons');
