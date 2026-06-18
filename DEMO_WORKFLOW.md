# Demo Workflow

This workflow describes how to demo the integrated web frontend using the live ML backend.

## Setup
1. Start the ML backend from `services/ml`.
2. Set environment variables for `apps/web`:
   - `ANALYST_USERNAME` - username configured in the ML backend.
   - `ANALYST_PASSWORD` - password configured in the ML backend.
   - `ML_API_URL` or `NEXT_PUBLIC_API_URL` - backend URL, e.g. `http://localhost:8000`.
3. Start the frontend:
   - `cd apps/web`
   - `npm install` (if needed)
   - `npm run dev`

## Login
1. Open the browser and navigate to the web app.
2. Click `Sign in` or navigate to `/login`.
3. Enter the backend analyst credentials.
4. On successful login, the app redirects to `/admin/dashboard`.

## Dashboard review
1. Confirm the dashboard loads real metrics from `GET /dashboard/summary`.
2. Validate counts for profiles, snapshots, predictions, and risk levels.
3. Verify the admin navigation is visible and the role badge appears.

## Analytics exploration
1. Visit `Analytics` to load `GET /analytics/predictions`.
2. Open `Model Performance` to load `GET /analytics/model-performance`.
3. Open `Drift` to load `GET /analytics/drift?days=7`.
4. Open `Alerts` and `Queue` to validate `GET /analytics/alerts` and `GET /analytics/queue`.
5. Open `Model Health` to validate `GET /analytics/model-health`.

## Prediction workflow
1. Go to `Workflows`.
2. Run a snapshot generation using a student profile ID.
3. Generate a prediction from the snapshot and verify `POST /predict/generate`.
4. Queue a prediction job with `POST /predictions/queue`.
5. Inspect prediction history for the same student profile.
6. Review predictions using `POST /predictions/{prediction_id}/review`.

## Model registry demo
1. Open `Models` to load `GET /models`.
2. View details for a model via `GET /models/{model_id}`.
3. Promote, rollback, or archive a model and watch the UI refresh.
4. Use `Compare models` to load `GET /models/compare?ids=...`.

## Expected behavior
- All dashboard and analytics widgets should render live backend values.
- Protected admin pages should redirect to `/login` when not authenticated.
- Model registry actions should invoke backend lifecycle endpoints.
- The frontend should show loading and error states for API calls.

## Troubleshooting
- If login fails, verify `ANALYST_USERNAME` and `ANALYST_PASSWORD`.
- If pages fail to load, confirm `ML_API_URL` or `NEXT_PUBLIC_API_URL` points to a running backend.
- If a token expires, refresh the page or login again.
