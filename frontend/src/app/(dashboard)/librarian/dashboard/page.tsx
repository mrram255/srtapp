import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function LibrarianDashboardPage() {
  return (
    <RoleDashboardPage
      segment="librarian"
      title="Librarian Dashboard"
      allowedRoles={["LIBRARIAN", "SUPER_ADMIN", "ADMIN"]}
    />
  );
}
