import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function StudentDashboardPage() {
  return (
    <RoleDashboardPage
      segment="student"
      title="Student Dashboard"
      allowedRoles={["STUDENT"]}
      quickLinks={[{ href: "/student/certificates", label: "Certificates" }]}
    />
  );
}
