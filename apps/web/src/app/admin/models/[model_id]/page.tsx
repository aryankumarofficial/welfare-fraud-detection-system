"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useApi } from "@/hooks/use-api";
import { useAuth } from "@/components/auth/auth-provider";
import { getModelDetail, promoteModel, rollbackModel, archiveModel } from "@/lib/api";
import type { ModelDetail } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function ModelDetailPage() {
  const params = useParams();
  const { user } = useAuth();
  const modelId = Array.isArray(params?.model_id) ? params?.model_id[0] : params?.model_id;
  const { data: model, error, loading, refetch } = useApi<ModelDetail | null>(
    () => (modelId ? getModelDetail(modelId) : Promise.resolve(null)),
    [modelId]
  );
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const isAdmin = user?.role === "admin";

  if (!modelId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="rounded-3xl border border-border bg-background p-8 text-center">
          <p className="text-lg font-semibold">Model ID is required.</p>
        </div>
      </div>
    );
  }

  const handleAction = async (action: "promote" | "rollback" | "archive") => {
    setActionMessage(null);
    try {
      if (action === "promote") {
        await promoteModel(modelId);
        setActionMessage(`Model ${modelId} promoted.`);
      }
      if (action === "rollback") {
        await rollbackModel(modelId);
        setActionMessage(`Model ${modelId} rolled back.`);
      }
      if (action === "archive") {
        await archiveModel(modelId);
        setActionMessage(`Model ${modelId} archived.`);
      }
      await refetch();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : "Unable to perform model action.");
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Model detail</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Model {modelId}</h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Live model metadata and lifecycle actions from the backend registry.
        </p>
      </div>

      {loading ? (
        <div className="rounded-3xl border border-border bg-muted/50 p-8 text-center">Loading model details…</div>
      ) : error ? (
        <div className="rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      {actionMessage ? (
        <div className="mb-6 rounded-3xl border border-border bg-background p-6 text-sm text-foreground">
          {actionMessage}
        </div>
      ) : null}

      {model ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border border-border">
            <CardHeader>
              <CardTitle>{model.name}</CardTitle>
              <CardDescription>{model.description ?? "Model registry details."}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Version</p>
                <p className="font-semibold">{model.version}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <Badge variant={model.role === "champion" ? "default" : model.status === "ARCHIVED" ? "destructive" : "secondary"}>
                  {model.role ?? model.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Deployed at</p>
                <p>{model.deployed_at ?? "N/A"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Promoted by</p>
                <p>{model.promoted_by ?? "N/A"}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-border">
            <CardHeader>
              <CardTitle>Lifecycle actions</CardTitle>
              <CardDescription>Promote, rollback, or archive this model.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button size="sm" className="w-full" onClick={() => void handleAction("promote")} disabled={!isAdmin}>Promote model</Button>
              <Button size="sm" variant="outline" className="w-full" onClick={() => void handleAction("rollback")} disabled={!isAdmin}>Rollback model</Button>
              <Button size="sm" variant="destructive" className="w-full" onClick={() => void handleAction("archive")} disabled={!isAdmin}>Archive model</Button>
              {!isAdmin ? (
                <p className="text-sm text-muted-foreground mt-3">Admin role is required to perform lifecycle actions.</p>
              ) : null}
            </CardContent>
          </Card>

          <Card className="lg:col-span-2 border border-border">
            <CardHeader>
              <CardTitle>Training & configuration</CardTitle>
              <CardDescription>Model registry metadata from the backend.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Artifact URI</p>
                <p>{model.artifact_uri ?? "N/A"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Feature schema version</p>
                <p>{model.feature_schema_version ?? "N/A"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Configuration</p>
                <pre className="mt-2 overflow-x-auto rounded-2xl border border-border bg-muted/50 p-4 text-sm text-muted-foreground">
                  {JSON.stringify(model.configuration ?? {}, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2 border border-border">
            <CardHeader>
              <CardTitle>Evaluation history</CardTitle>
              <CardDescription>Latest evaluation runs for this model version.</CardDescription>
            </CardHeader>
            <CardContent>
              {model.evaluation_runs?.length ? (
                <div className="space-y-4">
                  {model.evaluation_runs.map((run: any) => (
                    <div key={run.evaluation_run_id} className="rounded-3xl border border-border p-4">
                      <div className="flex items-center justify-between gap-4">
                        <p className="font-semibold">{run.dataset_name}</p>
                        <Badge>{run.dataset_version ?? "latest"}</Badge>
                      </div>
                      <div className="grid gap-2 sm:grid-cols-3 mt-3 text-sm text-muted-foreground">
                        <div>
                          <p>Precision</p>
                          <p className="font-semibold">{run.precision}</p>
                        </div>
                        <div>
                          <p>Recall</p>
                          <p className="font-semibold">{run.recall}</p>
                        </div>
                        <div>
                          <p>FPR</p>
                          <p className="font-semibold">{run.false_positive_rate}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No evaluation runs are available for this model.</p>
              )}
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
