import api from "./client";

export interface ForumThread {
  id: string;
  title: string;
  body: string;
  author: string;
  author_name: string;
  author_role: string;
  subject: string | null;
  subject_name: string | null;
  semester: number | null;
  tags: string;
  tags_list: string[];
  is_pinned: boolean;
  is_closed: boolean;
  is_flagged: boolean;
  view_count: number;
  reply_count: number;
  created_at: string;
}

export interface ForumReply {
  id: string;
  thread: string;
  author: string;
  author_name: string;
  author_role: string;
  body: string;
  parent_reply: string | null;
  is_accepted: boolean;
  like_count: number;
  created_at: string;
}

export const forumApi = {
  list: (params?: Record<string, string>) =>
    api.get("/forum/", { params }).then((r) => r.data),
  detail: (id: string) =>
    api.get(`/forum/${id}/`).then((r) => r.data),
  create: (data: { title: string; body: string; subject?: string; semester?: number; tags?: string }) =>
    api.post("/forum/", data).then((r) => r.data),
  update: (id: string, data: Partial<ForumThread>) =>
    api.patch(`/forum/${id}/`, data).then((r) => r.data),
  delete: (id: string) =>
    api.delete(`/forum/${id}/`).then((r) => r.data),
  reply: (threadId: string, data: { body: string; parent_reply?: string }) =>
    api.post(`/forum/${threadId}/replies/`, data).then((r) => r.data),
  likeReply: (replyId: string) =>
    api.post(`/forum/replies/${replyId}/like/`).then((r) => r.data),
};
