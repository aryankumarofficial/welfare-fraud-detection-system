import { describe, expect, test } from "bun:test"
import { PREDICTION_JOB_OPTIONS, PREDICTION_QUEUE_NAME } from "./config"
import { executePredictionJob } from "./handler"
import { enqueuePredictionJob } from "./queue"
import type { PredictionJobData } from "./types"

describe("prediction BullMQ configuration", () => {
  test("uses the prediction queue name", () => {
    expect(PREDICTION_QUEUE_NAME).toBe("prediction-processing")
  })

  test("configures exponential retries with three attempts", () => {
    expect(PREDICTION_JOB_OPTIONS.attempts).toBe(3)
    expect(PREDICTION_JOB_OPTIONS.backoff).toEqual({
      type: "exponential",
      delay: 1_000,
    })
  })

  test("enqueues prediction jobs with deterministic BullMQ ids", async () => {
    const data: PredictionJobData = {
      job_id: "job-1",
      student_profile_id: "profile-1",
      feature_snapshot_id: null,
      batch_id: null,
    }
    const calls: unknown[] = []
    const queue = {
      add(name: string, payload: PredictionJobData, options: unknown) {
        calls.push({ name, payload, options })
        return Promise.resolve({ id: payload.job_id })
      },
    }

    const job = await enqueuePredictionJob(data, queue as never)

    expect(job.id).toBe("job-1")
    expect(calls).toHaveLength(1)
    expect(calls[0]).toMatchObject({
      name: "execute-prediction",
      payload: data,
      options: {
        attempts: 3,
        backoff: { type: "exponential", delay: 1_000 },
        jobId: "job-1",
      },
    })
  })
})

describe("prediction BullMQ worker handler", () => {
  test("calls the ML execution endpoint and returns the response payload", async () => {
    const calls: Array<{ path: string; body: unknown }> = []
    const restoreFetch = mockFetch(async (input, init) => {
      const url = new URL(String(input))
      calls.push({ path: url.pathname, body: JSON.parse(String(init?.body)) })
      return json({ success: true, data: { prediction_id: "prediction-1" } })
    })

    try {
      const result = await executePredictionJob(fakeJob({ attemptsMade: 0 }))

      expect(result).toEqual({
        success: true,
        data: { prediction_id: "prediction-1" },
      })
      expect(calls).toEqual([
        {
          path: "/internal/predictions/jobs/job-1/execute",
          body: { attempt: 1 },
        },
      ])
    } finally {
      restoreFetch()
    }
  })

  test("marks a job retrying when an attempt fails before the final attempt", async () => {
    const calls: Array<{ path: string; body: unknown }> = []
    const restoreFetch = mockFetch(async (input, init) => {
      const url = new URL(String(input))
      calls.push({ path: url.pathname, body: JSON.parse(String(init?.body)) })
      if (url.pathname.endsWith("/execute")) {
        return json({ detail: "temporary failure" }, { status: 500 })
      }
      return json({ success: true })
    })

    try {
      await expect(executePredictionJob(fakeJob({ attemptsMade: 0 }))).rejects.toThrow(
        "temporary failure",
      )

      expect(calls).toEqual([
        {
          path: "/internal/predictions/jobs/job-1/execute",
          body: { attempt: 1 },
        },
        {
          path: "/internal/predictions/jobs/job-1/retrying",
          body: { attempt: 1, error: "temporary failure" },
        },
      ])
    } finally {
      restoreFetch()
    }
  })

  test("marks a job failed when the final attempt is exhausted", async () => {
    const calls: Array<{ path: string; body: unknown }> = []
    const restoreFetch = mockFetch(async (input, init) => {
      const url = new URL(String(input))
      calls.push({ path: url.pathname, body: JSON.parse(String(init?.body)) })
      if (url.pathname.endsWith("/execute")) {
        return json({ detail: "permanent failure" }, { status: 500 })
      }
      return json({ success: true })
    })

    try {
      await expect(executePredictionJob(fakeJob({ attemptsMade: 2 }))).rejects.toThrow(
        "permanent failure",
      )

      expect(calls).toEqual([
        {
          path: "/internal/predictions/jobs/job-1/execute",
          body: { attempt: 3 },
        },
        {
          path: "/internal/predictions/jobs/job-1/failed",
          body: { attempt: 3, error: "permanent failure" },
        },
      ])
    } finally {
      restoreFetch()
    }
  })
})

function fakeJob({ attemptsMade }: { attemptsMade: number }) {
  return {
    attemptsMade,
    opts: { attempts: 3 },
    data: {
      job_id: "job-1",
      student_profile_id: "profile-1",
      feature_snapshot_id: null,
      batch_id: null,
    },
  } as never
}

function json(payload: unknown, init?: ResponseInit): Response {
  return new Response(JSON.stringify(payload), {
    ...init,
    headers: { "Content-Type": "application/json" },
  })
}

function mockFetch(
  implementation: (input: unknown, init?: { body?: unknown }) => Promise<Response>,
): () => void {
  const originalFetch = globalThis.fetch
  globalThis.fetch = implementation as typeof fetch
  return () => {
    globalThis.fetch = originalFetch
  }
}
