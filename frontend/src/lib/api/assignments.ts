import api from "./client";

export interface Assignment {
  id: string;
  title: string;
  description: string;
  subject: string;
  subject_name: string;
  teacher: string;
  teacher_name: string;
  department: string;
  semester: number;
  section: string;
  max_marks: number;
  due_date: string;
  attachment: string;
  status: "DRAFT" | "PUBLISHED" | "CLOSED";
  created_at: string;
}

export interface AssignmentSubmission {
  id: string;
  assignment: string;
  assignment_title: string;
  student: string;
  student_enrollment: string;
  submission_text: string;
  attachment: string;
  submitted_at: string;
  marks_obtained: number | null;
  feedback: string;
  status: "PENDING" | "SUBMITTED" | "LATE" | "GRADED" | "RESUBMIT";
  graded_by: string | null;
  graded_at: string | null;
}

export const assignmentsApi = {
  list: (params?: Record<string, string>) =>
    api.get("/assignments/", { params }).then((r) => r.data),
  detail: (id: string) =>
    api.get(`/assignments/${id}/`).then((r) => r.data),
  create: (data: Partial<Assignment>) =>
    api.post("/assignments/", data).then((r) => r.data),
  update: (id: string, data: Partial<Assignment>) =>
    api.patch(`/assignments/${id}/`, data).then((r) => r.data),
  submissions: (params?: Record<string, string>) =>
    api.get("/assignments/submissions/", { params }).then((r) => r.data),
  submit: (data: { assignment: string; submission_text?: string; attachment?: string }) =>
    api.post("/assignments/submissions/", data).then((r) => r.data),
  grade: (submissionId: string, data: { marks_obtained: number; feedback?: string }) =>
    api.patch(`/assignments/submissions/${submissionId}/grade/`, data).then((r) => r.data),
  uploadAttachment: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/assignments/attachment/upload/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
};
