export const settingsKeys = {
  all: ['settings'] as const,
  list: (language: string, params?: unknown) => ['settings', 'list', language, params] as const,
};
