import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function SecurityDashboardPage() {
  return (
    <RoleDashboardPage
      segment="security"
      title="Security Dashboard"
      allowedRoles={["SECURITY", "SUPER_ADMIN", "ADMIN"]}
    />
  );
}
