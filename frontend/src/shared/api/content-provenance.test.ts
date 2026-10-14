import { it, expect } from 'vitest';

import { mapContentProvenance } from './content-provenance';

it('keeps a missing source honest and preserves summary status and citation', () => {
  expect(mapContentProvenance()).toBeUndefined();
  expect(
    mapContentProvenance({
      kind: 'ayah',
      title: 'Quran',
      reference: '2:255',
      url: 'https://quran.com/2/255',
      meaning_is_summary: true,
    })
  ).toEqual({
    kind: 'ayah',
    title: 'Quran',
    reference: '2:255',
    url: 'https://quran.com/2/255',
    meaningIsSummary: true,
  });
});

it('does not turn an unsafe or credential-bearing source into a clickable link', () => {
  for (const url of [
    'javascript:alert(1)',
    'data:text/html,x',
    '//example.org',
    'https://user:pass@example.org',
    'not a URL',
  ]) {
    expect(
      mapContentProvenance({
        kind: 'dua',
        title: 'Recorded source',
        reference: 'Report 1',
        url,
        meaning_is_summary: false,
      })?.url
    ).toBe('');
  }
});
