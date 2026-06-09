export type ApiOptions = RequestInit & { token?: string | null };

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');
  if (options.token) headers.set('Authorization', `Bearer ${options.token}`);
  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function post<T>(path: string, body: unknown, token?: string | null) {
  return api<T>(path, { method: 'POST', body: JSON.stringify(body), token });
}

export function patch<T>(path: string, body: unknown, token?: string | null) {
  return api<T>(path, { method: 'PATCH', body: JSON.stringify(body), token });
}
