import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function TeacherDashboardPage() {
  return (
    <RoleDashboardPage
      segment="teacher"
      title="Teacher Dashboard"
      allowedRoles={["TEACHER", "SUPER_ADMIN", "ADMIN", "HOD"]}
    />
  );
}
