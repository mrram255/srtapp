import Link from "next/link";
import { AdminDashboard } from "@/components/dashboard/admin-dashboard";

export default function PrincipalDashboardPage() {
  return (
    <div className="space-y-4">
      <AdminDashboard segment="principal" titleOverride="Principal Dashboard" />
      <div className="rounded-xl border border-border bg-surface p-4">
        <Link href="/principal/governance" className="text-sm font-medium text-accent hover:underline">
          Open governance — approvals & meetings →
        </Link>
      </div>
    </div>
  );
}
