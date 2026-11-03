import { getCollection, type CollectionEntry } from 'astro:content';
import siteContentRaw from '../../../publication/site-content.txt?raw';
import { LIBRARY_BASE_URL, PASSAGE_URL, TRACK_ORDER } from '../config';

export type TrackEntry = CollectionEntry<'tracks'>;
export type LessonEntry = CollectionEntry<'lessons'>;
export type Text = { zh: string; en?: string };

export interface UnitNode {
  id: string;
  title: Text;
  summary?: Text;
  lessons: LessonEntry[];
}
export interface TrackNode {
  id: string;
  data: TrackEntry['data'];
  units: UnitNode[];
  /** Published lessons in reading order (used for next/prev and progress). */
  path: LessonEntry[];
}

export const trackOf = (lesson: LessonEntry) => lesson.id.split('/')[0];

let cache: Promise<TrackNode[]> | undefined;

function loadLibraryAllowlist(): Set<string> {
  return new Set(
    siteContentRaw
      .split(/\r?\n/)
      .map((line: string) => line.trim())
      .filter((line: string) => Boolean(line) && !line.startsWith('#')),
  );
}

/** Loads tracks + lessons and checks that they fit together (fails the build if not). */
export function loadTracks(): Promise<TrackNode[]> {
  cache ??= (async () => {
    const tracks = await getCollection('tracks');
    const lessons = await getCollection('lessons');
    const allowlist = loadLibraryAllowlist();
    const problems: string[] = [];

    for (const id of TRACK_ORDER) {
      if (!tracks.some((t) => t.id === id)) problems.push(`config TRACK_ORDER lists "${id}" but tracks/${id}.yaml is missing`);
    }
    for (const t of tracks) {
      if (!(TRACK_ORDER as readonly string[]).includes(t.id)) problems.push(`tracks/${t.id}.yaml is not listed in TRACK_ORDER (src/config.ts)`);
    }
    for (const l of lessons) {
      const track = tracks.find((t) => t.id === trackOf(l));
      if (!track) problems.push(`lessons/${l.id}.md is in folder "${trackOf(l)}", which is not a track`);
      else if (!track.data.units.some((u) => u.id === l.data.unit))
        problems.push(`lessons/${l.id}.md has unit "${l.data.unit}", but tracks/${track.id}.yaml has no such unit`);
      for (const [i, q] of l.data.check.entries()) {
        if (q.answer >= q.options.length) problems.push(`lessons/${l.id}.md check #${i + 1}: answer ${q.answer} is out of range (options start at 0)`);
      }
      for (const f of l.data.further) {
        const [file] = f.path.split('#');
        if (allowlist && !allowlist.has(file)) {
          problems.push(`lessons/${l.id}.md further path "${file}" is not in publication/site-content.txt`);
        }
      }
      if (l.data.status === 'published') {
        if (!l.body?.trim()) problems.push(`lessons/${l.id}.md is published but has no body text`);
        if (!l.data.title.en) problems.push(`lessons/${l.id}.md is published but missing title.en`);
        if (!l.data.summary.en) problems.push(`lessons/${l.id}.md is published but missing summary.en`);
      }
    }
    if (problems.length) throw new Error('Content problems:\n  - ' + problems.join('\n  - '));

    const byOrder = (a: LessonEntry, b: LessonEntry) => a.data.order - b.data.order || a.id.localeCompare(b.id);
    return TRACK_ORDER.map((id) => {
      const t = tracks.find((x) => x.id === id)!;
      const units = t.data.units.map((u) => ({
        ...u,
        lessons: lessons.filter((l) => trackOf(l) === id && l.data.unit === u.id).sort(byOrder),
      }));
      const path = units.flatMap((u) => u.lessons).filter((l) => l.data.status === 'published');
      return { id, data: t.data, units, path };
    });
  })();
  return cache;
}

// ---------- URLs ----------

const BASE = import.meta.env.BASE_URL.replace(/\/?$/, '/');
export const url = (p = '') => BASE + p.replace(/^\//, '');
export const lessonUrl = (lesson: LessonEntry | string) => url(`learn/${typeof lesson === 'string' ? lesson : lesson.id}/`);
export const trackUrl = (id: string) => url(`tracks/${id}/`);
export const artUrl = (name?: string) => (name ? url(`repo-assets/art/${name}.svg`) : undefined);
export const passageUrl = (refEn: string) => PASSAGE_URL.replace('{q}', encodeURIComponent(refEn));

/**
 * Repository Markdown path (e.g. "Bible_Timeline/X.md#frag") → library page URL.
 * When built under `<prefix>/learn/`, links resolve to `<prefix>/` on the same host
 * so GitHub Pages and static mirrors work without hardcoding the domain.
 */
export function libraryUrl(mdPath: string) {
  const [file, hash] = mdPath.split('#');
  const html = file.replace(/(^|\/)README\.md$/, '$1index.html').replace(/\.md$/, '.html');
  const base = BASE.endsWith('/learn/')
    ? BASE.slice(0, -'learn/'.length)
    : LIBRARY_BASE_URL.endsWith('/')
      ? LIBRARY_BASE_URL
      : `${LIBRARY_BASE_URL}/`;
  return base + encodeURI(html) + (hash ? `#${hash}` : '');
}
