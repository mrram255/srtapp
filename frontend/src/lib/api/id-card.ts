import api from "./client";

export interface IDCardData {
  student_id: string;
  name: string;
  enrollment_number: string;
  roll_number: string;
  department: string;
  branch: string;
  semester: number;
  section: string;
  blood_group: string;
  college_name: string;
  profile_photo: string;
  qr_code: string;
  valid_till: string;
}

export const idCardApi = {
  get: (studentId?: string) =>
    api.get("/students/id-card/me/", {
      params: studentId ? { student: studentId } : {},
    }).then((r) => r.data),

  downloadPdf: (studentId?: string) =>
    api.get("/students/id-card/me/", {
      params: { format: "pdf", ...(studentId ? { student: studentId } : {}) },
      responseType: "blob",
    }).then((r) => r.data),
};
