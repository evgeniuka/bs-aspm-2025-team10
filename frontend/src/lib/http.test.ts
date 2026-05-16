import { afterEach, describe, expect, it, vi } from "vitest";
import { request } from "./http";

describe("request", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends JSON with credentials and parses the response", async () => {
    const fetchMock = vi.fn(async () => Response.json({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(request<{ ok: boolean }>("/api", "/sessions", { method: "POST", json: { client_ids: [1] } })).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/sessions",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        body: JSON.stringify({ client_ids: [1] })
      })
    );
  });

  it("surfaces FastAPI detail messages", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => Response.json({ detail: "Invalid client/program assignment" }, { status: 400 }))
    );

    await expect(request("/api", "/sessions", { method: "POST", json: {} })).rejects.toMatchObject({
      name: "ApiError",
      message: "Invalid client/program assignment",
      status: 400
    });
  });
});
