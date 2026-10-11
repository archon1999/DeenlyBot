export const arabicKeys = {
  all: ['arabic'] as const,
  list: (language: string, params?: unknown) => ['arabic', 'list', language, params] as const,
  detail: (language: string, id: number | null) => ['arabic', 'detail', language, id] as const,
};
