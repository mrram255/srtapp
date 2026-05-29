/**
 * Spec-aligned post-login destinations and route-prefix access control.
 * @see Master Prompt Section 2 — role-based dashboard redirects
 */

/** Primary home URL per RBAC role name (accounts.User.role, upper snake). */
export const ROLE_DASHBOARD_HOME: Record<string, string> = {
  SUPER_ADMIN: "/super-admin/dashboard",
  ADMIN: "/super-admin/dashboard",
  PRINCIPAL: "/principal/dashboard",
  VICE_PRINCIPAL: "/principal/dashboard",
  DEAN: "/principal/dashboard",
  REGISTRAR: "/registrar/dashboard",
  BURSAR: "/registrar/dashboard",
  CHIEF_ACCOUNTANT: "/accounts/dashboard",
  ACCOUNTANT: "/accounts/dashboard",
  CASHIER: "/accounts/dashboard",
  ADMISSION_OFFICER: "/admissions/dashboard",
  ADMISSION_COUNSELLOR: "/admissions/dashboard",
  HOD: "/hod/dashboard",
  TEACHER: "/teacher/dashboard",
  STUDENT: "/student/dashboard",
  PARENT: "/parent/dashboard",
  LIBRARIAN: "/librarian/dashboard",
  SECURITY: "/security/dashboard",
};

/** Home URL keyed by users.Role.name (lower snake). */
export const ROLE_SLUG_DASHBOARD_HOME: Record<string, string> = {
  super_admin: "/super-admin/dashboard",
  principal: "/principal/dashboard",
  vice_principal: "/principal/dashboard",
  dean: "/principal/dashboard",
  registrar: "/registrar/dashboard",
  bursar: "/registrar/dashboard",
  chief_accountant: "/accounts/dashboard",
  accountant: "/accounts/dashboard",
  cashier: "/accounts/dashboard",
  admission_officer: "/admissions/dashboard",
  admission_counsellor: "/admissions/dashboard",
  hod: "/hod/dashboard",
  teacher: "/teacher/dashboard",
  student: "/student/dashboard",
  parent: "/parent/dashboard",
  librarian: "/librarian/dashboard",
  security_officer: "/security/dashboard",
};

/** URL prefix (first path segment) → roles allowed to access that area. */
export const ROLE_ROUTE_ACCESS: Record<string, readonly string[]> = {
  "super-admin": ["SUPER_ADMIN", "ADMIN"],
  principal: ["PRINCIPAL", "VICE_PRINCIPAL", "DEAN", "SUPER_ADMIN"],
  registrar: ["REGISTRAR", "BURSAR", "SUPER_ADMIN"],
  accounts: ["ACCOUNTANT", "CHIEF_ACCOUNTANT", "CASHIER", "SUPER_ADMIN"],
  admissions: ["ADMISSION_OFFICER", "ADMISSION_COUNSELLOR", "SUPER_ADMIN"],
  hod: ["HOD", "SUPER_ADMIN", "ADMIN"],
  teacher: ["TEACHER", "SUPER_ADMIN", "ADMIN", "HOD"],
  student: ["STUDENT"],
  parent: ["PARENT"],
  librarian: ["LIBRARIAN", "SUPER_ADMIN", "ADMIN"],
  security: ["SECURITY", "SUPER_ADMIN", "ADMIN"],
};

/** Legacy /dashboard/{segment} homes → spec paths (301-style redirect in middleware). */
export const LEGACY_SEGMENT_REDIRECT: Record<string, string> = {
  "super-admin": "/super-admin/dashboard",
  admin: "/super-admin/dashboard",
  principal: "/principal/dashboard",
  registrar: "/registrar/dashboard",
  accountant: "/accounts/dashboard",
  admissions: "/admissions/dashboard",
  hod: "/hod/dashboard",
  teacher: "/teacher/dashboard",
  student: "/student/dashboard",
  parent: "/parent/dashboard",
  librarian: "/librarian/dashboard",
  security: "/security/dashboard",
};

export const ROLE_ROUTE_PREFIXES = Object.keys(ROLE_ROUTE_ACCESS);

function normalizeRoleKey(role: string): string {
  return role.trim().toUpperCase().replace(/-/g, "_");
}

export function resolveDashboardPath(role: string, roleSlug?: string | null): string {
  const slug = roleSlug?.trim().toLowerCase();
  if (slug && ROLE_SLUG_DASHBOARD_HOME[slug]) {
    return ROLE_SLUG_DASHBOARD_HOME[slug];
  }
  const key = normalizeRoleKey(role);
  return ROLE_DASHBOARD_HOME[key] ?? "/student/dashboard";
}

export function canAccessRoutePrefix(role: string, prefix: string): boolean {
  const allowed = ROLE_ROUTE_ACCESS[prefix];
  if (!allowed) return true;
  return allowed.includes(normalizeRoleKey(role));
}

export function legacyDashboardRedirect(pathname: string): string | null {
  if (pathname === "/dashboard") {
    return null;
  }
  const match = pathname.match(/^\/dashboard\/([^/]+)\/?$/);
  if (!match) {
    return null;
  }
  return LEGACY_SEGMENT_REDIRECT[match[1]] ?? null;
}
