import { QueueEvents } from "bullmq"
import { ML_SERVICE_URL, PREDICTION_QUEUE_NAME } from "./config"
import { createRedisConnection } from "./queue"

const connection = createRedisConnection()

export const predictionQueueEvents = new QueueEvents(PREDICTION_QUEUE_NAME, {
  connection,
})

async function postJson(path: string, body: unknown): Promise<void> {
  await fetch(`${ML_SERVICE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).catch(() => undefined)
}

predictionQueueEvents.on("failed", async ({ jobId, failedReason }) => {
  await postJson(`/internal/predictions/jobs/${jobId}/failed`, {
    attempt: 3,
    error: failedReason,
  })
})

predictionQueueEvents.on("waiting", ({ jobId }) => {
  console.log(`[prediction-events] waiting ${jobId}`)
})

predictionQueueEvents.on("completed", ({ jobId }) => {
  console.log(`[prediction-events] completed ${jobId}`)
})

process.on("SIGINT", async () => {
  await predictionQueueEvents.close()
})

process.on("SIGTERM", async () => {
  await predictionQueueEvents.close()
})
