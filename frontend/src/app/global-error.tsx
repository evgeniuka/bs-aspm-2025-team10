"use client";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, sans-serif", display: "flex", minHeight: "100vh", alignItems: "center", justifyContent: "center", margin: 0 }}>
        <main style={{ maxWidth: 480, padding: 24, textAlign: "center" }}>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>The app hit an unexpected error</h1>
          <p style={{ marginTop: 8, color: "#64748b" }}>{error.message || "Please reload and try again."}</p>
          <button
            onClick={reset}
            style={{ marginTop: 16, padding: "8px 16px", borderRadius: 8, border: 0, background: "#2454d6", color: "#fff", fontWeight: 600, cursor: "pointer" }}
            type="button"
          >
            Try again
          </button>
        </main>
      </body>
    </html>
  );
}
