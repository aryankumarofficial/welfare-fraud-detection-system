export type PredictionJobData = {
  job_id: string
  student_profile_id: string
  feature_snapshot_id?: string | null
  batch_id?: string | null
}

export type EnqueuePredictionBody = PredictionJobData
