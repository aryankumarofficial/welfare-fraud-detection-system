"use client";

import { useState } from "react";
import { useApi } from "@/hooks/use-api";
import { compareModels } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function ModelComparePage() {
  const [ids, setIds] = useState("");
  const [query, setQuery] = useState("");
  const [loadRequest, setLoadRequest] = useState(false);
  const { data: comparison, error, loading, refetch } = useApi(
    async () => (query ? await compareModels(query) : []),
    [query, loadRequest]
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Model comparison</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Compare registered models</h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Enter comma-separated model IDs to inspect performance and registry metadata.
        </p>
      </div>

      <Card className="border border-border p-6">
        <form
          className="grid gap-4 sm:grid-cols-[1fr_auto]"
          onSubmit={(event) => {
            event.preventDefault();
            setQuery(ids.trim());
            setLoadRequest((value) => !value);
          }}
        >
          <input
            value={ids}
            onChange={(event) => setIds(event.target.value)}
            placeholder="model-id-1, model-id-2"
            className="w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
          <Button type="submit" className="w-full">Compare models</Button>
        </form>
      </Card>

      {loading ? (
        <div className="mt-6 rounded-3xl border border-border bg-muted/50 p-6 text-center">Loading comparison…</div>
      ) : error ? (
        <div className="mt-6 rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      {comparison?.length ? (
        <div className="mt-6 space-y-6">
          {comparison.map((model: any) => (
            <Card key={model.model_version_id} className="border border-border">
              <CardHeader>
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <CardTitle>{model.name}</CardTitle>
                    <CardDescription>Version {model.version}</CardDescription>
                  </div>
                  <Badge variant={model.role === "champion" ? "default" : "secondary"}>
                    {model.role ?? model.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">Evaluation summary</p>
                <pre className="overflow-x-auto rounded-2xl border border-border bg-muted/50 p-4 text-sm text-muted-foreground">
                  {JSON.stringify(model.latest_evaluation ?? {}, null, 2)}
                </pre>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : null}
    </div>
  );
}
