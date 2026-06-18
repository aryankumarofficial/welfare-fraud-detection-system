import type { PredictionReviewsResponse } from "@/lib/types";
import { getPredictionReviews } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ReviewsPageProps {
  searchParams: { decision?: string | string[] };
}

const reviewChoices = ["confirmed_fraud", "false_positive", "pending", "under_investigation"];

export default async function ReviewsPage({ searchParams }: ReviewsPageProps) {
  const decision = Array.isArray(searchParams.decision) ? searchParams.decision[0] : searchParams.decision;
  let reviews: PredictionReviewsResponse[] = [];
  let errorMessage: string | null = null;

  try {
    reviews = await getPredictionReviews(decision || undefined);
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : "Unable to fetch reviews.";
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Reviews Management</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Analyst review history and filtering
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Browse the latest prediction reviews and filter by decision type.
        </p>
      </div>

      <Card className="border border-border p-6">
        <form className="flex flex-wrap items-center gap-3" action="." method="get">
          <label htmlFor="decision" className="text-sm font-medium text-muted-foreground">
            Filter by decision
          </label>
          <select
            id="decision"
            name="decision"
            defaultValue={decision ?? ""}
            className="rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            <option value="">All reviews</option>
            {reviewChoices.map((choice) => (
              <option key={choice} value={choice}>{choice.replaceAll("_", " ")}</option>
            ))}
          </select>
          <button
            type="submit"
            className="rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
          >
            Apply filter
          </button>
        </form>
      </Card>

      {errorMessage ? (
        <div className="mt-6 rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {errorMessage}
        </div>
      ) : null}

      <div className="mt-8 space-y-6">
        <Card className="border border-border">
          <CardHeader className="px-6 py-5">
            <CardTitle>Review results</CardTitle>
            <CardDescription>Recent review records from the backend.</CardDescription>
          </CardHeader>
          <CardContent className="px-6 pb-6 pt-0">
            {reviews.length === 0 ? (
              <p className="text-sm text-muted-foreground">No reviews were returned for the selected filter.</p>
            ) : (
              <div className="space-y-4">
                {reviews.map((review) => (
                  <div key={review.review_id} className="rounded-3xl border border-border p-5">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Review ID</p>
                        <p className="mt-1 font-semibold">{review.review_id}</p>
                      </div>
                      <Badge variant="secondary">{review.decision.replaceAll("_", " ")}</Badge>
                    </div>
                    <div className="mt-4 grid gap-3 sm:grid-cols-3">
                      <div>
                        <p className="text-xs uppercase text-muted-foreground">Prediction ID</p>
                        <p className="mt-1 text-sm font-semibold">{review.prediction_id}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase text-muted-foreground">Reviewer</p>
                        <p className="mt-1 text-sm font-semibold">{review.reviewer}</p>
                      </div>
                      <div>
                        <p className="text-xs uppercase text-muted-foreground">Created at</p>
                        <p className="mt-1 text-sm font-semibold">{review.created_at}</p>
                      </div>
                    </div>
                    <div className="mt-4 rounded-3xl border border-border bg-muted/50 p-4 text-sm text-muted-foreground">
                      <p className="font-medium">Reviewer notes</p>
                      <p className="mt-1">{review.notes ?? "No notes provided."}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
