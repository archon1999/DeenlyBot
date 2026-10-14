import { it, expect } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';

import { LocaleProvider } from 'src/shared/i18n';

import { ReviewLink, ReviewSection } from './index';

it.each(['names-review', 'arabic-review', 'library-review'])(
  'links to the focusable %s review section without starting a quiz',
  (id) => {
    const html = renderToStaticMarkup(
      <LocaleProvider>
        <ReviewLink targetId={id} />
        <ReviewSection id={id}>Review content</ReviewSection>
      </LocaleProvider>
    );
    expect(html).toContain(`href="#${id}"`);
    expect(html).toContain(`aria-controls="${id}"`);
    expect(html).toContain(`id="${id}"`);
    expect(html).toContain('tabindex="-1"');
    expect(html).toContain('Takrorlashga o‘tish');
  }
);
