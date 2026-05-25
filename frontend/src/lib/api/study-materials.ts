import api from "./client";

export interface StudyMaterial {
  id: string;
  title: string;
  description: string;
  subject: string;
  subject_name: string;
  teacher_name: string;
  department_name: string;
  material_type: "PDF" | "VIDEO" | "IMAGE" | "DOCUMENT" | "LINK" | "OTHER";
  file_url: string;
  external_link: string;
  file_size: number;
  version: number;
  semester: number;
  section: string;
  access_level: "ALL" | "DEPARTMENT" | "BATCH";
  is_published: boolean;
  download_count: number;
  tags: string;
  tags_list: string[];
  created_at: string;
}

export const studyMaterialsApi = {
  list: (params?: Record<string, string>) =>
    api.get("/study-materials/", { params }).then((r) => r.data),
  detail: (id: string) =>
    api.get(`/study-materials/${id}/`).then((r) => r.data),
  create: (data: Partial<StudyMaterial>) =>
    api.post("/study-materials/", data).then((r) => r.data),
  update: (id: string, data: Partial<StudyMaterial>) =>
    api.patch(`/study-materials/${id}/`, data).then((r) => r.data),
  delete: (id: string) =>
    api.delete(`/study-materials/${id}/`).then((r) => r.data),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/study-materials/upload/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
};
