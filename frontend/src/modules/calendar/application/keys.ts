export const calendarKeys = {
  all: ['calendar'] as const,
  list: (language: string, params?: unknown) => ['calendar', 'list', language, params] as const,
};
