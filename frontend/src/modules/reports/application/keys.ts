export const reportsKeys = {
  all: ['reports'] as const,
  list: (language: string, params?: unknown) => ['reports', 'list', language, params] as const,
};
