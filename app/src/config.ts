// App-wide settings. Most day-to-day edits happen in src/content/, not here.

export const APP = {
  name: { zh: '圣约学堂', en: 'Covenant Learn' },
  shortName: 'Covenant',
  tagline: {
    zh: '一步一步读懂圣经：从好奇到扎根。',
    en: 'Understand the Bible step by step, from curiosity to deep roots.',
  },
  themeColor: '#1c3554',
};

/**
 * Fallback base URL for the full reading library (the Project Covenant static
 * site) when the app is served at root (`/`) during local development.
 * When built under a `.../learn/` subpath, `libraryUrl()` automatically links
 * to the parent `.../` path on the same origin.
 */
export const LIBRARY_BASE_URL = 'https://jayliang42.github.io/Project-Covenant/';

/**
 * Online passage reader for scripture references. `{q}` is replaced with the
 * URL-encoded English reference (e.g. "John 3:16").
 * The app does not bundle copyrighted Bible translations.
 */
export const PASSAGE_URL = 'https://www.biblegateway.com/passage/?search={q}&version=CUVS;NIV';

/** Order in which the four tracks are shown. Must match files in content/tracks. */
export const TRACK_ORDER = ['curious', 'seeking', 'new', 'deeper'] as const;
