/// <reference types="bun" />

import { QUEUE_API_PORT, PREDICTION_QUEUE_NAME } from "./config"
import { enqueuePredictionJob } from "./queue"
import type { EnqueuePredictionBody } from "./types"

function jsonResponse(payload: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(payload), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  })
}

function isPredictionBody(value: unknown): value is EnqueuePredictionBody {
  if (!value || typeof value !== "object") return false
  return "job_id" in value && "student_profile_id" in value
}

const QUEUE_API_KEY = process.env.QUEUE_API_KEY ?? "queue-change-me"

Bun.serve({
  port: QUEUE_API_PORT,
  async fetch(request: Request) {
    const url = new URL(request.url)

    if (request.method === "GET" && url.pathname === "/health") {
      return jsonResponse({ ok: true, queue_name: PREDICTION_QUEUE_NAME })
    }

    if (request.method === "POST" && url.pathname === "/predictions/enqueue") {
      const authKey = request.headers.get("x-queue-api-key")
      if (authKey !== QUEUE_API_KEY) {
        return jsonResponse(
          { success: false, error: "UNAUTHORIZED" },
          { status: 401 },
        )
      }

      const body = await request.json().catch(() => null)
      if (!isPredictionBody(body)) {
        return jsonResponse(
          { success: false, error: "INVALID_PREDICTION_JOB_PAYLOAD" },
          { status: 422 },
        )
      }

      const job = await enqueuePredictionJob(body)
      return jsonResponse({
        success: true,
        bullmq_job_id: String(job.id),
        queue_name: PREDICTION_QUEUE_NAME,
      })
    }

    return jsonResponse({ success: false, error: "NOT_FOUND" }, { status: 404 })
  },
})

console.log(`[prediction-queue-api] listening on :${QUEUE_API_PORT}`)
