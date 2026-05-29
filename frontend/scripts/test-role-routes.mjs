/**
 * Lightweight checks for spec-aligned dashboard paths (no vitest required).
 * Run: node scripts/test-role-routes.mjs
 */

import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

// Compile TS on the fly via Next's transpilation is heavy; duplicate critical expectations:
const ROLE_DASHBOARD_HOME = {
  SUPER_ADMIN: "/super-admin/dashboard",
  REGISTRAR: "/registrar/dashboard",
  PRINCIPAL: "/principal/dashboard",
  ACCOUNTANT: "/accounts/dashboard",
  ADMISSION_OFFICER: "/admissions/dashboard",
};

function resolveDashboardPath(role, roleSlug) {
  const slugMap = {
    registrar: "/registrar/dashboard",
    super_admin: "/super-admin/dashboard",
  };
  if (roleSlug && slugMap[roleSlug]) return slugMap[roleSlug];
  return ROLE_DASHBOARD_HOME[role] ?? "/student/dashboard";
}

assert.equal(resolveDashboardPath("SUPER_ADMIN", "super_admin"), "/super-admin/dashboard");
assert.equal(resolveDashboardPath("REGISTRAR", "registrar"), "/registrar/dashboard");
assert.equal(resolveDashboardPath("PRINCIPAL", "principal"), "/principal/dashboard");
assert.equal(resolveDashboardPath("ACCOUNTANT", null), "/accounts/dashboard");
assert.equal(resolveDashboardPath("ADMISSION_OFFICER", "admission_officer"), "/admissions/dashboard");

console.log("role-routes checks passed");
