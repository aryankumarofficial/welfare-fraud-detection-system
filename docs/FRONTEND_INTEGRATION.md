# Frontend Integration

This document describes the new frontend integration work completed for the demo-ready admin experience.

## What was added

- `apps/web/src/lib/api.ts`: typed API client for ML backend requests
- `apps/web/src/lib/types.ts`: response and domain type definitions
- `apps/web/src/app/admin/*`: new admin route pages for live backend data
- `apps/web/src/app/admin/loading.tsx`: route-level loading state for admin pages
- `apps/web/src/components/layout/navbar.tsx`: updated navigation to expose the admin workspace

## New frontend pages

The following pages now connect to existing backend APIs:

- `/admin/dashboard`
  - uses `GET /dashboard/summary`
- `/admin/predictions`
  - uses `GET /predictions/{student_profile_id}`
- `/admin/predictions/detail/[prediction_id]`
  - uses `GET /predictions/detail/{prediction_id}`
- `/admin/jobs`
  - uses `GET /predictions/jobs/{job_id}`
- `/admin/analytics`
  - uses `GET /analytics/predictions`
- `/admin/analytics/model-performance`
  - uses `GET /analytics/model-performance`
- `/admin/analytics/drift`
  - uses `GET /analytics/drift`
- `/admin/analytics/queue`
  - uses `GET /analytics/queue`
- `/admin/analytics/alerts`
  - uses `GET /analytics/alerts`
- `/admin/reviews`
  - uses `GET /predictions/reviews`

## Existing frontend audit findings

The public marketing site remained unchanged and is still a static landing experience. The admin experience now provides live data from the backend for demonstration purposes.

Static pages / placeholder areas identified:
- `src/app/(public)/page.tsx`: static marketing homepage
- `src/components/home/stats/stats-section.tsx`: hardcoded metrics replaced in the admin dashboard only
- `src/app/(public)/contact/page.tsx`: static contact form placeholders

## Environment variables

The frontend admin layer now uses environment-based API configuration and server-side authentication.

Required values for the Next.js app runtime:

- `ML_API_URL`
  - Backend base URL for ML service requests
- `ANALYST_USERNAME`
- `ANALYST_PASSWORD`

Optional fallback:
- `NEXT_PUBLIC_API_URL`
  - Used when `ML_API_URL` is not provided, though server-side env values are preferred.

Example runtime values:

```env
ML_API_URL=http://localhost:8000
ANALYST_USERNAME=analyst
ANALYST_PASSWORD=analyst-password
```

A `apps/web/.env.example` file was added to help bootstrap local frontend demo configuration.

## Notes

- No backend ML logic or schema was modified.
- The admin pages call the existing ML API endpoints directly and render live backend data.
- Loading states are exposed through the admin route group, and query-based search forms support prediction and job lookups.

## Next steps

- Set `ML_API_URL` and analyst credentials in the Next.js environment before running the app.
- Navigate to `/admin/dashboard` to verify the live data path.
- Use `/admin/predictions` and `/admin/jobs` to demonstrate end-to-end data retrieval.
