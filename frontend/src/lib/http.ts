const DEFAULT_TIMEOUT_MS = 12000;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly body?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export type RequestOptions = RequestInit & {
  json?: unknown;
  timeoutMs?: number;
};

export function getErrorMessage(error: unknown) {
  if (error instanceof Error) return error.message;
  return "Something went wrong. Please try again.";
}

export async function request<T>(baseUrl: string, path: string, options: RequestOptions = {}): Promise<T> {
  const controller = new AbortController();
  const { json, timeoutMs, headers, ...requestOptions } = options;
  const timeoutId = globalThis.setTimeout(() => controller.abort(), timeoutMs ?? DEFAULT_TIMEOUT_MS);

  try {
    const response = await fetch(`${baseUrl}${path}`, {
      ...requestOptions,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(headers ?? {})
      },
      body: json === undefined ? requestOptions.body : JSON.stringify(json),
      signal: controller.signal
    });

    if (!response.ok) {
      const body = await response.text();
      throw new ApiError(parseErrorBody(body) || `Request failed: ${response.status}`, response.status, body);
    }

    if (response.status === 204) {
      return undefined as T;
    }
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Request timed out. Check that the local API is running and try again.");
    }
    throw new ApiError("API is unreachable. Make sure the FastAPI server is running on port 8000.");
  } finally {
    globalThis.clearTimeout(timeoutId);
  }
}

function parseErrorBody(body: string) {
  if (!body) return "";
  try {
    const parsed = JSON.parse(body) as { detail?: unknown };
    if (typeof parsed.detail === "string") {
      return parsed.detail;
    }
  } catch {
    return body;
  }
  return body;
}
