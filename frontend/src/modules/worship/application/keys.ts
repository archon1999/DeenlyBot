export const worshipKeys = {
  all: ['worship'] as const,
  list: (language: string, params?: unknown) => ['worship', 'list', language, params] as const,
};
