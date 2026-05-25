export type ApiEnvelope<T = unknown> = {
  success: boolean;
  message: string;
  data?: T;
  errors?: Record<string, string[]>;
  error_code?: string;
  timestamp?: string;
};
