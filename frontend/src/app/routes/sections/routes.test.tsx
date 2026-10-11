import { it, expect } from 'vitest';
import { matchRoutes } from 'react-router';

import { routesSection } from './index';

it.each(['/missing', '/missing/deep/page', '/404'])(
  'renders %s outside the protected dashboard layout',
  (path) => {
    const matches = matchRoutes(routesSection, path);
    expect(matches).toHaveLength(1);
    expect(matches?.[0].route.path).toBe('*');
  }
);

it('keeps regular feature routes inside the dashboard', () => {
  const matches = matchRoutes(routesSection, '/library');
  expect(matches).toHaveLength(2);
  expect(matches?.[0].route.path).toBeUndefined();
  expect(matches?.[1].route.path).toBe('library');
});

it('keeps explicit login separate from dashboard and missing-page routes', () => {
  const matches = matchRoutes(routesSection, '/login');
  expect(matches).toHaveLength(1);
  expect(matches?.[0].route.path).toBe('login');
});
