import { it, expect, describe } from 'vitest';

import { safeReturnPath } from './safe-return-path';

describe('post-login navigation', () => {
  it('returns a protected local path with its query', () => {
    expect(safeReturnPath('/library?page=2')).toBe('/library?page=2');
  });
  it('rejects URLs and browser-normalized network paths', () => {
    for (const value of [
      'https://example.com',
      '//example.com',
      '/\\example.com',
      '/\nexample.com',
      null,
    ])
      expect(safeReturnPath(value)).toBe('/');
  });
  it('validates against the actual app origin and normalizes local dot segments', () => {
    expect(safeReturnPath('/names/../profile#telegram-link', 'http://localhost:5174')).toBe(
      '/profile#telegram-link'
    );
  });
});
