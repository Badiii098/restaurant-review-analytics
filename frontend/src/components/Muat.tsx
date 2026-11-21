import type { UseQueryResult } from "@tanstack/react-query";
import type { ReactNode } from "react";

export function Muat<T>({ q, children }: { q: UseQueryResult<T>; children: (d: T) => ReactNode }) {
  if (q.isPending) return <p className="kecil" aria-busy="true">Memuat…</p>;
  if (q.isError) return <p className="galat" role="alert">{(q.error as Error).message}</p>;
  return <>{children(q.data as T)}</>;
}
