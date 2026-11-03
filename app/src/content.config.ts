import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

/** Bilingual text. Chinese is required; English is optional while drafting. */
const text = z.strictObject({
  zh: z.string().min(1),
  en: z.string().optional(),
});

/**
 * Tracks: one YAML file per audience in src/content/tracks/.
 * Units are declared here, in order; lessons point at a unit by its id.
 */
const tracks = defineCollection({
  loader: glob({ pattern: '*.yaml', base: './src/content/tracks' }),
  schema: z.object({
    title: text,
    who: text, // "我想…" line shown on the chooser
    tagline: text,
    description: text,
    color: z.string().regex(/^#[0-9a-fA-F]{6}$/),
    art: z.string().optional(), // file name in ../assets/art without .svg
    units: z
      .array(
        z.object({
          id: z.string().regex(/^[a-z0-9-]+$/),
          title: text,
          summary: text.optional(),
        }),
      )
      .min(1),
  }),
});

const scripture = z.object({
  ref: z.string(), // Chinese reference, e.g. 约 3:16
  refEn: z.string(), // English reference, e.g. John 3:16 (used for the reader link)
  text: text.optional(), // only public-domain wording (和合本 1919 / WEB)
});

const question = z.object({
  q: text,
  options: z.array(text).min(2).max(5),
  answer: z.number().int().min(0),
  explain: text.optional(),
});

/**
 * Lessons: Markdown in src/content/lessons/<track>/<file>.md.
 * The folder name is the track; `unit` must match a unit id in that track.
 */
const lessons = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/lessons' }),
  schema: z.object({
    title: text,
    summary: text,
    unit: z.string(),
    order: z.number(),
    minutes: z.number().int().positive().default(5),
    status: z.enum(['published', 'planned']).default('published'),
    review: z.enum(['draft', 'reviewed']).default('draft'),
    art: z.string().optional(),
    scripture: z.array(scripture).default([]),
    reflect: z.array(text).default([]),
    check: z.array(question).default([]),
    further: z
      .array(z.object({ label: text, path: z.string(), why: text.optional() }))
      .default([]),
  }),
});

export const collections = { tracks, lessons };
