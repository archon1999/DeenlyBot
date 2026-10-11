import { it, expect, describe } from 'vitest';

import { sameLibraryScope } from './library-query-scope';

describe('library pagination scope', () => {
  const original = { kind: 'ayah' as const, page: 1, q: 'Yunus' };
  it('allows retained content only while paging the same localized result set', () => {
    expect(sameLibraryScope('uz', original, 'uz', { ...original, page: 2 })).toBe(true);
    expect(sameLibraryScope('uz', original, 'ru', original)).toBe(false);
    expect(sameLibraryScope('uz', original, 'uz', { ...original, kind: 'dua' })).toBe(false);
    expect(sameLibraryScope('uz', original, 'uz', { ...original, q: 'Musa' })).toBe(false);
    expect(sameLibraryScope(undefined, undefined, 'uz', original)).toBe(false);
  });
});
