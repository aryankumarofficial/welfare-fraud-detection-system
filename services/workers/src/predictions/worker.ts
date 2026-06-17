import { Worker } from "bullmq"
import { PREDICTION_QUEUE_NAME } from "./config"
import { executePredictionJob } from "./handler"
import { createRedisConnection } from "./queue"
import type { PredictionJobData } from "./types"

const connection = createRedisConnection()

export const predictionWorker = new Worker<PredictionJobData>(
  PREDICTION_QUEUE_NAME,
  executePredictionJob,
  {
    connection,
    concurrency: Number(process.env.PREDICTION_WORKER_CONCURRENCY ?? 2),
  },
)

predictionWorker.on("completed", (job) => {
  console.log(`[prediction-worker] completed ${job.id}`)
})

predictionWorker.on("failed", (job, error) => {
  console.error(`[prediction-worker] failed ${job?.id}: ${error.message}`)
})

process.on("SIGINT", async () => {
  await predictionWorker.close()
})

process.on("SIGTERM", async () => {
  await predictionWorker.close()
})
