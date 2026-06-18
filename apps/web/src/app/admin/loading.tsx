export default function AdminLoading() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4 py-16">
      <div className="rounded-3xl border border-border bg-background/90 p-8 text-center shadow-xl">
        <p className="text-lg font-semibold">Loading admin dashboard…</p>
        <p className="text-sm text-muted-foreground mt-2">
          Fetching live data from the ML backend.
        </p>
      </div>
    </div>
  );
}
