import api from "./client";

export interface UserNotification {
  id: string;
  notification: {
    id: string;
    title: string;
    message: string;
    notification_type: string;
    priority: string;
    created_at: string;
  };
  is_read: boolean;
  read_at: string | null;
  is_delivered: boolean;
}

export const notificationsApi = {
  list: (params?: Record<string, string>) =>
    api.get("/notifications/", { params }).then((r) => r.data),
  unreadCount: () =>
    api.get("/notifications/unread-count/").then((r) => r.data),
  markRead: (id: string) =>
    api.post(`/notifications/${id}/read/`).then((r) => r.data),
  markAllRead: () =>
    api.post("/notifications/mark-all-read/").then((r) => r.data),
};
