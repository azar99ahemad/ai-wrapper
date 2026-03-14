/**
 * API client for communicating with the AI Wrapper backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface FetchOptions {
  method?: string;
  body?: unknown;
  token?: string;
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Auth
export const auth = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    apiFetch("/auth/register", { method: "POST", body: data }),

  login: (data: { email: string; password: string }) =>
    apiFetch<{ access_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: data,
    }),
};

// Projects
export const projects = {
  generate: (data: { prompt: string; name?: string }, token?: string) =>
    apiFetch("/projects/generate", { method: "POST", body: data, token }),

  get: (id: string, token?: string) =>
    apiFetch(`/projects/${id}`, { token }),

  getFiles: (id: string, token?: string) =>
    apiFetch(`/projects/${id}/files`, { token }),

  editFile: (
    projectId: string,
    fileId: string,
    data: { prompt: string },
    token?: string
  ) =>
    apiFetch(`/projects/${projectId}/files/${fileId}/edit`, {
      method: "POST",
      body: data,
      token,
    }),

  deploy: (
    projectId: string,
    data: { provider: string },
    token?: string
  ) =>
    apiFetch(`/projects/${projectId}/deploy`, {
      method: "POST",
      body: data,
      token,
    }),

  getPreviewUrl: (projectId: string, token?: string) =>
    apiFetch(`/projects/${projectId}/preview-url`, { token }),
};
