import { it, vi, expect, describe, afterEach } from 'vitest';

import { ApiError, apiClient } from './api-client';

afterEach(() => {
  vi.unstubAllGlobals();
});

function browser(fetchMock: ReturnType<typeof vi.fn>) {
  vi.stubGlobal('window', { location: { origin: 'https://deenly.test' } });
  vi.stubGlobal('document', { cookie: 'other=1; csrftoken=csrf-test-value' });
  vi.stubGlobal('fetch', fetchMock);
}

describe('session API boundary', () => {
  it('sends same-origin session cookies and Django CSRF for a mutation', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, status: 200, json: async () => ({ created: true }) });
    browser(fetchMock);
    await apiClient.post('names/3/confirm/', {});
    const [url, request] = fetchMock.mock.calls[0];
    expect(url.href).toBe('https://deenly.test/api/v1/names/3/confirm/');
    expect(request.credentials).toBe('same-origin');
    expect(request.headers['X-CSRFToken']).toBe('csrf-test-value');
    expect(request.headers.Authorization).toBeUndefined();
  });

  it('encodes library queries and does not add a CSRF mutation header to reads', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, status: 200, json: async () => ({ results: [] }) });
    browser(fetchMock);
    await apiClient.get('library/', { q: 'Qur’on & duo', page: 2, empty: undefined });
    const [url, request] = fetchMock.mock.calls[0];
    expect(url.searchParams.get('q')).toBe('Qur’on & duo');
    expect(url.searchParams.get('page')).toBe('2');
    expect(url.searchParams.has('empty')).toBe(false);
    expect(request.headers['X-CSRFToken']).toBeUndefined();
  });

  it('preserves server validation details and refuses forbidden requests after one call', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ detail: 'Session required' }),
      });
    browser(fetchMock);
    await expect(apiClient.post('qada/complete/', { expected_key: 'stale' })).rejects.toMatchObject(
      { status: 403, message: 'Session required', details: { detail: 'Session required' } }
    );
    expect(fetchMock).toHaveBeenCalledTimes(1);
    await expect(apiClient.get('settings/')).rejects.toBeInstanceOf(ApiError);
  });
});
