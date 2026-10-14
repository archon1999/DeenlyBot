import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { DashboardHeading } from './dashboard-heading';

it.each([
  { title: 'Bugun', subtitle: 'Bugungi kichik qadamlar.' },
  { title: 'Сегодня', subtitle: 'Небольшие шаги на сегодня.' },
  { title: 'Today', subtitle: 'Small steps for today.' },
])('keeps the Arabic Basmala alongside the $title heading', (labels) => {
  const html = renderToStaticMarkup(<DashboardHeading labels={labels} />);
  expect(html).toContain(labels.title);
  expect(html).toContain(labels.subtitle);
  expect(html).toContain('بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ');
  expect(html).toContain('lang="ar"');
  expect(html).toContain('dir="rtl"');
  expect(html).toContain('Amiri');
  expect(html).toContain('flex-direction:column');
  expect(html).toContain('flex-direction:row');
  expect(html).toContain('max-width:100%');
  expect(html).toContain('order:-1');
  expect(html).toContain('order:0');
});
