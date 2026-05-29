import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function HodDashboardPage() {
  return (
    <RoleDashboardPage segment="hod" title="HOD Dashboard" allowedRoles={["HOD", "SUPER_ADMIN", "ADMIN"]} />
  );
}
