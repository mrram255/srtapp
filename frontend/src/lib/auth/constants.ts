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
  attendance: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT"],
  timetable: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  exams: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  profile: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "SECURITY"],
  "id-card": ["SUPER_ADMIN", "ADMIN", "HOD", "STUDENT"],
  notifications: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "SECURITY"],
  settings: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN", "SECURITY"],
  users: ["SUPER_ADMIN"],
  roles: ["SUPER_ADMIN"],
  assignments: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  "study-materials": ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  analytics: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT", "ACCOUNTANT", "LIBRARIAN"],
  forum: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
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
