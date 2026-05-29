import api from "./client";

export interface UserNotification {
  id: string;
  notification: {
    id: string;
    title: string;
    message: string;
    notification_type: string;
    category?: string;
    priority: string;
    action_url?: string;
    created_at: string;
  };
  is_read: boolean;
  read_at: string | null;
  is_delivered: boolean;
}

export interface NotificationPreference {
  email_enabled: boolean;
  sms_enabled: boolean;
  whatsapp_enabled: boolean;
  push_enabled: boolean;
  dnd_start_time: string | null;
  dnd_end_time: string | null;
  category_preferences: Record<string, boolean>;
}

export interface NotificationTemplate {
  id: string;
  name: string;
  event_type: string;
  email_subject: string;
  push_title: string;
  push_body: string;
  is_active: boolean;
}

export interface BulkNotification {
  id: string;
  title: string;
  message: string;
  status: string;
  total_recipients: number;
  sent_count: number;
  created_at: string;
}

export interface Announcement {
  id: string;
  title: string;
  content: string;
  announcement_type: string;
  target_audience: string;
  published_at: string | null;
  is_pinned: boolean;
}

type ApiEnvelope<T> = { success: boolean; data: T; meta?: Record<string, unknown> };

export const notificationsApi = {
  list: (params?: Record<string, string>) =>
    api.get<ApiEnvelope<UserNotification[]>>("/notifications/", { params }).then((r) => r.data),

  unreadCount: () =>
    api.get<ApiEnvelope<{ unread_count: number }>>("/notifications/unread-count/").then((r) => r.data),

  markRead: (id: string) =>
    api.post(`/notifications/${id}/read/`).then((r) => r.data),

  markAllRead: () =>
    api.post("/notifications/mark-all-read/").then((r) => r.data),

  getPreferences: () =>
    api.get<ApiEnvelope<NotificationPreference>>("/notifications/preferences/").then((r) => r.data),

  updatePreferences: (data: Partial<NotificationPreference>) =>
    api.patch<ApiEnvelope<NotificationPreference>>("/notifications/preferences/", data).then((r) => r.data),

  listTemplates: () =>
    api.get<ApiEnvelope<NotificationTemplate[]>>("/notifications/templates/").then((r) => r.data),

  createTemplate: (data: Partial<NotificationTemplate>) =>
    api.post<ApiEnvelope<NotificationTemplate>>("/notifications/templates/", data).then((r) => r.data),

  sendBulk: (data: Record<string, unknown>) =>
    api.post<ApiEnvelope<BulkNotification>>("/notifications/send-bulk/", data).then((r) => r.data),

  bulkHistory: () =>
    api.get<ApiEnvelope<BulkNotification[]>>("/notifications/bulk-history/").then((r) => r.data),

  listAnnouncements: () =>
    api.get<ApiEnvelope<Announcement[]>>("/notifications/announcements/").then((r) => r.data),

  createAnnouncement: (data: Record<string, unknown>) =>
    api.post<ApiEnvelope<Announcement>>("/notifications/announcements/", data).then((r) => r.data),

  publishAnnouncement: (id: string) =>
    api.post<ApiEnvelope<Announcement>>(`/notifications/announcements/${id}/publish/`).then((r) => r.data),
};
