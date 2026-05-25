import api from "./client";

export interface TimetableEntry {
  id: string;
  subject: string;
  subject_name: string;
  teacher: string;
  teacher_name: string;
  department: string;
  semester: number;
  section: string;
  day: string;
  start_time: string;
  end_time: string;
  room_number: string;
  academic_year: string;
  is_active: boolean;
}

export type WeekTimetable = Record<string, TimetableEntry[]>;

export const timetableApi = {
  today: () =>
    api.get("/academics/timetable/today/").then((r) => r.data),
  week: () =>
    api.get("/academics/timetable/week/").then((r) => r.data),
  list: (params?: Record<string, string>) =>
    api.get("/academics/timetable/", { params }).then((r) => r.data),
  create: (data: Partial<TimetableEntry>) =>
    api.post("/academics/timetable/", data).then((r) => r.data),
  update: (id: string, data: Partial<TimetableEntry>) =>
    api.put(`/academics/timetable/${id}/`, data).then((r) => r.data),
  remove: (id: string) =>
    api.delete(`/academics/timetable/${id}/`).then((r) => r.data),
};
