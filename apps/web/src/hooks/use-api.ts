"use client";

import { useCallback, useEffect, useState } from "react";

export function useApi<T>(fetcher: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      setData(result);
    } catch (error) {
      setError(error instanceof Error ? error.message : "Unable to load data.");
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    void refetch();
  }, [refetch]);

  return {
    data,
    error,
    loading,
    refetch,
  };
}
