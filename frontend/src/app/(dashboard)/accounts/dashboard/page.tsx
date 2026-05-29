import { RoleDashboardPage } from "@/components/dashboard/role-dashboard-page";

export default function AccountsDashboardPage() {
  return (
    <RoleDashboardPage
      segment="accounts"
      title="Accounts Dashboard"
      allowedRoles={["ACCOUNTANT", "CHIEF_ACCOUNTANT", "CASHIER", "SUPER_ADMIN"]}
      quickLinks={[{ href: "/dashboard/finance", label: "Finance module" }]}
    />
  );
}
