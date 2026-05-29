import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function AdmissionsDashboardPage() {
  return (
    <RoleDashboardPage
      segment="admissions"
      title="Admissions Dashboard"
      allowedRoles={["ADMISSION_OFFICER", "ADMISSION_COUNSELLOR", "SUPER_ADMIN"]}
      quickLinks={[{ href: "/dashboard/admissions", label: "Admissions module" }]}
    />
  );
}
