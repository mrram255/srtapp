import api from "./client";

export interface AttendanceRecord {
  id: string;
  student: string;
  student_enrollment: string;
  subject: string;
  subject_name: string;
  teacher: string;
  date: string;
  status: "PRESENT" | "ABSENT" | "LATE" | "EXCUSED" | "HALF_DAY";
  period: number;
  remarks: string;
  marked_at: string;
}

export interface AttendanceSummary {
  id: string;
  student: string;
  student_enrollment: string;
  subject: string;
  subject_name: string;
  academic_year: string;
  total_classes: number;
  present_count: number;
  absent_count: number;
  late_count: number;
  excused_count: number;
  percentage: number;
}

export interface MonthlyStats {
  total: number;
  present: number;
  absent: number;
  late: number;
  excused: number;
  percentage: number;
  is_low: boolean;
}

export const attendanceApi = {
  list: (params?: Record<string, string>) =>
    api.get("/attendance/", { params }).then((r) => r.data),

  summary: (params?: Record<string, string>) =>
    api.get("/attendance/summary/", { params }).then((r) => r.data),

  monthlyStats: (studentId: string, params?: Record<string, string>) =>
    api
      .get("/attendance/monthly-stats/", { params: { student: studentId, ...params } })
      .then((r) => r.data),

  alerts: (params?: Record<string, string>) =>
    api.get("/attendance/alerts/", { params }).then((r) => r.data),

  bulkMark: (rows: Partial<AttendanceRecord>[]) =>
    api.post("/attendance/", rows).then((r) => r.data),
};
