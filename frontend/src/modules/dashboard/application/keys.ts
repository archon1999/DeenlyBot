export const dashboardKeys = {
  all: ['dashboard'] as const,
  list: (language: string, params?: unknown) => ['dashboard', 'list', language, params] as const,
};
