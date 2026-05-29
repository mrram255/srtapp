import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function RegistrarDashboardPage() {
  return (
    <RoleDashboardPage
      segment="registrar"
      title="Registrar Dashboard"
      allowedRoles={["REGISTRAR", "BURSAR", "SUPER_ADMIN"]}
      quickLinks={[
        { href: "/registrar/students", label: "Student database" },
        { href: "/registrar/staff", label: "Staff records" },
        { href: "/registrar/certificates", label: "Certificates" },
      ]}
    />
  );
}
