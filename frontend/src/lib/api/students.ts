import api from "./client";
import type { Student } from "@/types";

export const studentsApi = {
  me: () =>
    api.get("/students/me/").then((r) => r.data as { data: Student }),

  dashboard: () =>
    api.get("/students/dashboard/").then((r) => r.data),

  uploadPhoto: (file: File, studentId?: string) => {
    const form = new FormData();
    form.append("photo", file);
    if (studentId) form.append("student", studentId);
    return api.post("/students/photo/upload/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },

  uploadSignature: (file: File, studentId?: string) => {
    const form = new FormData();
    form.append("signature", file);
    if (studentId) form.append("student", studentId);
    return api.post("/students/signature/upload/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
};
