"use client";

import { QueryCache, QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
import { ApiError } from "@/lib/http";
import { routes } from "@/lib/routes";

export function QueryProvider({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        queryCache: new QueryCache({
          onError: (error) => {
            // Central session-expiry handling: any unauthenticated read sends the user to login
            // instead of each screen reinventing its own 401 card.
            if (
              error instanceof ApiError &&
              error.status === 401 &&
              typeof window !== "undefined" &&
              window.location.pathname !== routes.login
            ) {
              window.location.assign(routes.login);
            }
          }
        }),
        defaultOptions: {
          queries: {
            retry: false,
            refetchOnWindowFocus: false,
            staleTime: 30_000,
            gcTime: 5 * 60_000
          },
          mutations: {
            retry: 0
          }
        }
      })
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
