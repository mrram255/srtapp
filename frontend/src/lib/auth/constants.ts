export type Role =
  | "SUPER_ADMIN"
  | "ADMIN"
  | "HOD"
  | "TEACHER"
  | "STUDENT"
  | "PARENT"
  | "ACCOUNTANT"
  | "LIBRARIAN"
  | "SECURITY";

export const ACCESS_COOKIE = "access_token";
export const REFRESH_COOKIE = "refresh_token";

export const DASHBOARD_SEGMENT_ROLES: Record<string, readonly Role[]> = {
  "super-admin": ["SUPER_ADMIN"],
  admin: ["SUPER_ADMIN", "ADMIN"],
  hod: ["SUPER_ADMIN", "ADMIN", "HOD"],
  teacher: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER"],
  student: ["STUDENT"],
  parent: ["PARENT"],
  accountant: ["SUPER_ADMIN", "ADMIN", "ACCOUNTANT"],
  librarian: ["SUPER_ADMIN", "ADMIN", "LIBRARIAN"],
  security: ["SUPER_ADMIN", "ADMIN", "SECURITY"],
  students: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER"],
  teachers: ["SUPER_ADMIN", "ADMIN", "HOD"],
  academics: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  attendance: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT"],
  timetable: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  exams: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  profile: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "SECURITY"],
  "id-card": ["SUPER_ADMIN", "ADMIN", "HOD", "STUDENT"],
  notifications: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "SECURITY"],
  settings: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "SECURITY"],
  users: ["SUPER_ADMIN"],
  roles: ["SUPER_ADMIN"],
  institution: ["SUPER_ADMIN"],
  academic: ["SUPER_ADMIN"],
  assignments: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  "study-materials": ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  analytics: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN"],
  forum: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  finance: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "ACCOUNTANT"],
  library: ["SUPER_ADMIN", "ADMIN", "HOD", "LIBRARIAN", "TEACHER", "STUDENT"],
  messages: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT"],
  admissions: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "ACCOUNTANT"],
  hostel: ["SUPER_ADMIN", "ADMIN", "STUDENT", "PARENT"],
  transport: ["SUPER_ADMIN", "ADMIN", "STUDENT", "PARENT"],
  placements: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  mess: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  events: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT"],
  reports: ["SUPER_ADMIN", "ADMIN", "HOD", "ACCOUNTANT"],
  gate: ["SUPER_ADMIN", "ADMIN", "SECURITY"],
};

export const ROLE_HOME_SEGMENT: Record<string, string> = {
  SUPER_ADMIN: "super-admin",
  ADMIN: "admin",
  HOD: "hod",
  TEACHER: "teacher",
  STUDENT: "student",
  PARENT: "parent",
  ACCOUNTANT: "accountant",
  LIBRARIAN: "librarian",
  SECURITY: "security",
};
