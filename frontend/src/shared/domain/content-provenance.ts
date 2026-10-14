export type ContentProvenance = {
  kind: 'name' | 'lesson' | 'ayah' | 'surah' | 'dua' | 'analysis';
  title: string;
  url: string;
  reference: string;
  meaningIsSummary: boolean;
};
