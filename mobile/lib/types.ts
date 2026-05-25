/** Django `APIResponse` JSON shape (see backend `apps/core/responses.py`). */
export type ApiEnvelope<T> = {
  success?: boolean;
  message?: string;
  data?: T;
  errors?: unknown;
};

export type AuthBundle = {
  access: string;
  refresh: string;
  user: AuthUser;
};

export type AuthUser = {
  id: string;
  email: string;
  role: string;
  first_name: string;
  last_name: string;
  college_id: string | null;
  department_id?: string | null;
  photo?: string;
};
