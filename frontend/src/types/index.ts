export type AuthUser = {
  id: string;
  email: string;
  role: string;
  first_name: string;
  last_name: string;
  college_id: string | null;
  department_id: string | null;
  is_verified: boolean;
  must_change_password: boolean;
  profile_photo: string;
  signature: string;
};

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
  meta?: {
    total: number;
    page: number;
    limit: number;
    pages: number;
    next: string | null;
    previous: string | null;
  };
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface College {
  id: string;
  name: string;
  code: string;
  city: string;
  state: string;
  photo: string;
  signature: string;
  is_active: boolean;
}

export interface Department {
  id: string;
  college: string;
  name: string;
  code: string;
  hod: string | null;
  photo: string;
  signature: string;
  is_active: boolean;
}

export interface Student {
  id: string;
  user: string;
  user_name: string;
  enrollment_number: string;
  roll_number: string;
  department: string;
  department_name: string;
  branch: string;
  semester: number;
  section: string;
  photo: string;
  signature: string;
  is_active: boolean;
}

export interface Teacher {
  id: string;
  user: string;
  user_name: string;
  employee_id: string;
  department: string;
  department_name: string;
  designation: string;
  photo: string;
  signature: string;
  is_active: boolean;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  priority: string;
  is_read: boolean;
  created_at: string;
}

export interface DashboardStats {
  totalStudents: number;
  totalTeachers: number;
  totalDepartments: number;
  attendanceToday: number;
  feeCollection: number;
  pendingFees: number;
  upcomingExams: number;
  newAdmissions: number;
}
