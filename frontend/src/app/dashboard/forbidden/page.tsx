import Link from "next/link";

export default function ForbiddenPage() {
  return (
    <div className="mx-auto max-w-lg space-y-4 text-center">
      <h1 className="font-display text-3xl font-semibold text-foreground">Access denied</h1>
      <p className="text-muted-foreground">
        Your role cannot open this dashboard area. Pick another module from your home dashboard.
      </p>
      <Link
        href="/dashboard"
        className="inline-flex rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
      >
        Back to dashboard
      </Link>
    </div>
  );
}
