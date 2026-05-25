"use client";

import { AdminDashboard } from "@/components/dashboard/admin-dashboard";
import { StudentDashboard } from "@/components/dashboard/student-dashboard";
import { TeacherDashboard } from "@/components/dashboard/teacher-dashboard";

export function DashboardBySegment({ segment }: { segment: string }) {
  switch (segment) {
    case "student":
      return <StudentDashboard />;
    case "teacher":
      return <TeacherDashboard />;
    case "admin":
    case "super-admin":
    case "hod":
    case "accountant":
    case "librarian":
    case "security":
    case "parent":
      return <AdminDashboard segment={segment} />;
    default:
      return (
        <div className="space-y-2">
          <h1 className="font-display text-2xl font-semibold capitalize text-foreground">
            {segment.replace(/-/g, " ")} dashboard
          </h1>
          <p className="text-muted-foreground">
            Connect this segment to your Django APIs when modules are ready.
          </p>
        </div>
      );
  }
}
