import type { Job } from "bullmq"
import { ML_SERVICE_URL } from "./config"
import type { PredictionJobData } from "./types"

async function postJson(path: string, body: unknown): Promise<unknown> {
  const response = await fetch(`${ML_SERVICE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Internal-API-Key": process.env.INTERNAL_API_KEY ?? "internal-change-me",
    },
    body: JSON.stringify(body),
  })

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const message =
      payload && typeof payload === "object" && "detail" in payload
        ? String(payload.detail)
        : `Request failed with status ${response.status}`
    throw new Error(message)
  }

  return payload
}

export async function executePredictionJob(job: Job<PredictionJobData>) {
  const attempt = job.attemptsMade + 1

  try {
    return await postJson(`/internal/predictions/jobs/${job.data.job_id}/execute`, {
      attempt,
    })
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    if (attempt < (job.opts.attempts ?? 3)) {
      await postJson(`/internal/predictions/jobs/${job.data.job_id}/retrying`, {
        attempt,
        error: message,
      }).catch(() => undefined)
    } else {
      await postJson(`/internal/predictions/jobs/${job.data.job_id}/failed`, {
        attempt,
        error: message,
      }).catch(() => undefined)
    }
    throw error
  }
}
