import { Queue, type ConnectionOptions } from "bullmq"
import {
  PREDICTION_JOB_OPTIONS,
  PREDICTION_QUEUE_NAME,
  REDIS_URL,
} from "./config"
import type { PredictionJobData } from "./types"

export function createRedisConnection(): ConnectionOptions {
  const redisUrl = new URL(REDIS_URL)
  return {
    host: redisUrl.hostname,
    port: Number(redisUrl.port || 6379),
    username: redisUrl.username || undefined,
    password: redisUrl.password || undefined,
    maxRetriesPerRequest: null,
  } as ConnectionOptions
}

export function createPredictionQueue(
  connection = createRedisConnection(),
): Queue<PredictionJobData, unknown, "execute-prediction"> {
  return new Queue<PredictionJobData, unknown, "execute-prediction">(PREDICTION_QUEUE_NAME, {
    connection,
    defaultJobOptions: PREDICTION_JOB_OPTIONS,
  })
}

export async function enqueuePredictionJob(
  data: PredictionJobData,
  queue = createPredictionQueue(),
) {
  return queue.add("execute-prediction", data, {
    ...PREDICTION_JOB_OPTIONS,
    jobId: data.job_id,
  })
}
