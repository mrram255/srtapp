import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function ParentDashboardPage() {
  return <RoleDashboardPage segment="parent" title="Parent Dashboard" allowedRoles={["PARENT"]} />;
}
