import { it, expect, describe } from 'vitest';

import { isNavItemSelected } from './navigation-state';

describe('top navigation selection', () => {
  it('does not keep Today selected on every route', () => {
    expect(isNavItemSelected('/', '/')).toBe(true);
    expect(isNavItemSelected('/names', '/')).toBe(false);
  });
  it('selects nested feature routes without matching a different feature prefix', () => {
    expect(isNavItemSelected('/arabic/lesson/1', '/arabic')).toBe(true);
    expect(isNavItemSelected('/namesake', '/names')).toBe(false);
  });
});
