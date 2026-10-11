export type ApiParams = Record<string, string | number | boolean | undefined | null>;
export class ApiError extends Error {
  constructor(
    public status: number,
    public details: Record<string, unknown>
  ) {
    const fields = Object.entries(details)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`)
      .join('; ');
    super(
      typeof details.detail === 'string' ? details.detail : fields || `Request failed (${status})`
    );
    this.name = 'ApiError';
  }
}
function csrfToken() {
  return (
    document.cookie
      .split('; ')
      .find((entry) => entry.startsWith('csrftoken='))
      ?.slice(10) ?? ''
  );
}
async function request<T>(
  method: string,
  path: string,
  data?: unknown,
  params?: ApiParams
): Promise<T> {
  const url = new URL(`/api/v1/${path.replace(/^\/+/, '')}`, window.location.origin);
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '')
      url.searchParams.set(key, String(value));
  });
  const response = await fetch(url, {
    method,
    credentials: 'same-origin',
    headers: {
      Accept: 'application/json',
      ...(method !== 'GET'
        ? { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }
        : {}),
    },
    ...(method !== 'GET' ? { body: JSON.stringify(data ?? {}) } : {}),
  });
  const body =
    response.status === 204
      ? {}
      : await response.json().catch(() => ({ detail: response.statusText }));
  if (!response.ok) throw new ApiError(response.status, body);
  return body as T;
}
export const apiClient = {
  get: <T>(path: string, params?: ApiParams) => request<T>('GET', path, undefined, params),
  post: <T>(path: string, data?: unknown) => request<T>('POST', path, data),
  patch: <T>(path: string, data: unknown) => request<T>('PATCH', path, data),
};
