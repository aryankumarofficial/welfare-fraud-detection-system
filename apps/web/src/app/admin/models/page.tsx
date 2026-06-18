"use client";

import Link from "next/link";
import { useState } from "react";
import { useApi } from "@/hooks/use-api";
import { useAuth } from "@/components/auth/auth-provider";
import { getModels, promoteModel, rollbackModel, archiveModel } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export default function ModelsPage() {
  const { user } = useAuth();
  const { data: models, error, loading, refetch } = useApi(getModels);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const isAdmin = user?.role === "admin";

  const handleAction = async (modelId: string, action: "promote" | "rollback" | "archive") => {
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
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Model Registry</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Model management and lifecycle</h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Live model inventory and lifecycle actions using the backend model registry endpoints.
        </p>
      </div>

      {loading ? (
        <div className="rounded-3xl border border-border bg-muted/50 p-8 text-center">Loading models…</div>
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

      <div className="grid gap-6 lg:grid-cols-3">
        {models?.map((model) => (
          <Card key={model.model_version_id} className="border border-border">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <CardTitle>{model.name}</CardTitle>
                  <CardDescription>Version {model.version}</CardDescription>
                </div>
                <Badge variant={model.role === "champion" ? "default" : model.status === "ARCHIVED" ? "destructive" : "secondary"}>
                  {model.role ?? model.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">Status</p>
              <p className="font-semibold">{model.status}</p>
              <p className="text-sm text-muted-foreground">Registered</p>
              <p>{model.created_at ?? "Unknown"}</p>
              <div className="space-y-2">
                <Button asChild size="sm" className="w-full">
                  <Link href={`/admin/models/${model.model_version_id}`}>View details</Link>
                </Button>
                <div className="grid gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => void handleAction(model.model_version_id, "promote")}
                    disabled={!isAdmin}
                  >
                    Promote
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => void handleAction(model.model_version_id, "rollback")}
                    disabled={!isAdmin}
                  >
                    Rollback
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => void handleAction(model.model_version_id, "archive")}
                    disabled={!isAdmin}
                  >
                    Archive
                  </Button>
                </div>
                {!isAdmin ? (
                  <p className="text-sm text-muted-foreground">Model lifecycle actions require admin privileges.</p>
                ) : null}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
