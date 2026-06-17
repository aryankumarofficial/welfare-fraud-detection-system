export const PREDICTION_QUEUE_NAME =
  process.env.PREDICTION_QUEUE_NAME ?? "prediction-processing"

export const REDIS_URL = process.env.REDIS_URL ?? "redis://127.0.0.1:6379"

export const ML_SERVICE_URL =
  process.env.ML_SERVICE_URL ?? "http://127.0.0.1:8000"

export const QUEUE_API_PORT = Number(process.env.PREDICTION_QUEUE_API_PORT ?? 8010)

export const PREDICTION_JOB_OPTIONS = {
  attempts: 3,
  backoff: {
    type: "exponential" as const,
    delay: 1_000,
  },
  removeOnComplete: {
    age: 60 * 60 * 24,
    count: 1_000,
  },
  removeOnFail: {
    age: 60 * 60 * 24 * 7,
    count: 5_000,
  },
}
