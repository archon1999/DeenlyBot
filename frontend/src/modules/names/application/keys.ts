export const namesKeys = {
  all: ['names'] as const,
  list: (language: string, params?: unknown) => ['names', 'list', language, params] as const,
};
