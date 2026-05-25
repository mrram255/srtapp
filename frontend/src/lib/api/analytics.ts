import api from "./client";

export interface PerformanceData {
  student_id: string;
  overall_avg_percentage: number;
  exam_trend: {
    exam_id: string;
    exam_name: string;
    subject: string;
    exam_date: string;
    marks_obtained: number;
    max_marks: number;
    percentage: number;
    status: string;
  }[];
  subject_averages: {
    subject: string;
    avg_percentage: number;
    exam_count: number;
    is_weak: boolean;
  }[];
  weak_subjects: { subject: string; avg_percentage: number }[];
  attendance: { avg_percentage: number; subjects_below_75: number };
  assignments: { total: number; submitted: number; graded: number; avg_marks: number };
}

export interface ClassAnalytics {
  exam_id: string;
  total_students: number;
  class_average: number;
  highest_marks: number;
  lowest_marks: number;
  pass_count: number;
  fail_count: number;
  pass_percentage: number;
  score_distribution: Record<string, number>;
  toppers: { student__user__full_name: string; marks_obtained: number; percentage: number; rank: number }[];
}

export const analyticsApi = {
  studentPerformance: (studentId?: string) =>
    api.get("/analytics/student/", { params: studentId ? { student: studentId } : {} }).then((r) => r.data),
  classAnalytics: (examId: string) =>
    api.get("/analytics/class/", { params: { exam: examId } }).then((r) => r.data),
  dashboardStats: () =>
    api.get("/analytics/dashboard/").then((r) => r.data),
};
