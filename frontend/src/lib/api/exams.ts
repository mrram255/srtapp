import api from "./client";

export interface ExamSchedule {
  id: string;
  name: string;
  exam_type: string;
  subject: string;
  subject_name: string;
  department: string;
  semester: number;
  section: string;
  exam_date: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  room_number: string;
  max_marks: number;
  passing_marks: number;
  instructions: string;
  question_count: number;
}

export interface MCQQuestion {
  id: string;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  marks: number;
  order: number;
}

export interface ExamResult {
  id: string;
  exam: string;
  exam_name: string;
  marks_obtained: number;
  percentage: number;
  status: string;
  rank: number;
}

export interface Scorecard {
  exam_name: string;
  subject_name: string;
  total_questions: number;
  attempted: number;
  correct: number;
  incorrect: number;
  skipped: number;
  marks_obtained: number;
  max_marks: number;
  percentage: number;
  status: string;
  rank: number;
  total_students: number;
}

export const examsApi = {
  list: (params?: Record<string, string>) =>
    api.get("/exams/", { params }).then((r) => r.data),
  results: (params?: Record<string, string>) =>
    api.get("/exams/results/", { params }).then((r) => r.data),
  ranking: (examId: string) =>
    api.get(`/exams/${examId}/ranking/`).then((r) => r.data),
  admitCards: (params?: Record<string, string>) =>
    api.get("/exams/admit-cards/", { params }).then((r) => r.data),
  startExam: (examId: string) =>
    api.post(`/exams/${examId}/start/`).then((r) => r.data),
  submitExam: (attemptId: string, answers: { question: string; selected_option: string | null }[]) =>
    api.post(`/exams/attempts/${attemptId}/submit/`, { answers }).then((r) => r.data),
  tabSwitch: (attemptId: string) =>
    api.post(`/exams/attempts/${attemptId}/tab-switch/`).then((r) => r.data),
};
