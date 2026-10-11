export const libraryKeys = {
  all: ['library'] as const,
  list: (language: string, params?: unknown) => ['library', 'list', language, params] as const,
  practice: (language: string, kind: string) => ['library', 'practice', language, kind] as const,
  detail: (language: string, kind: string, id: number | null) =>
    ['library', 'detail', language, kind, id] as const,
};
