import type { ContentProvenance } from 'src/shared/domain/content-provenance';

export type ContentProvenanceDto = {
  kind: ContentProvenance['kind'];
  title: string;
  url: string;
  reference: string;
  meaning_is_summary: boolean;
};

export function mapContentProvenance(value?: ContentProvenanceDto): ContentProvenance | undefined {
  if (!value) return undefined;
  let url = '';
  try {
    const parsed = new URL(value.url);
    if (['https:', 'http:'].includes(parsed.protocol) && !parsed.username) url = parsed.href;
  } catch {
    /* A missing or invalid reference remains visible as text. */
  }
  return {
    kind: value.kind,
    title: value.title,
    url,
    reference: value.reference,
    meaningIsSummary: value.meaning_is_summary,
  };
}
