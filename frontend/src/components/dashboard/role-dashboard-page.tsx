"use client";

import Link from "next/link";

import { AdminDashboard } from "@/components/dashboard/admin-dashboard";
import { StudentDashboard } from "@/components/dashboard/student-dashboard";
import { TeacherDashboard } from "@/components/dashboard/teacher-dashboard";
import { ProtectedRoute } from "@/components/shared/ProtectedRoute";

type RoleDashboardPageProps = {
  segment: string;
  title: string;
  allowedRoles: string[];
  quickLinks?: { href: string; label: string }[];
};

export function RoleDashboardPage({
  segment,
  title,
  allowedRoles,
  quickLinks = [],
}: RoleDashboardPageProps) {
  return (
    <ProtectedRoute roles={allowedRoles}>
      <div className="space-y-6">
        {quickLinks.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {quickLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium text-accent hover:bg-accent/5"
              >
                {link.label}
              </Link>
            ))}
          </div>
        ) : null}

        {segment === "student" ? (
          <StudentDashboard />
        ) : segment === "teacher" ? (
          <TeacherDashboard />
        ) : (
          <AdminDashboard segment={segment} titleOverride={title} />
        )}
      </div>
    </ProtectedRoute>
  );
}
