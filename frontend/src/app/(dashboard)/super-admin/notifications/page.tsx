"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  notificationsApi,
  type BulkNotification,
  type NotificationTemplate,
} from "@/lib/api/notifications";

export default function SuperAdminNotificationsPage() {
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [history, setHistory] = useState<BulkNotification[]>([]);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [targetType, setTargetType] = useState("all");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const load = async () => {
    try {
      const [tRes, hRes] = await Promise.all([
        notificationsApi.listTemplates(),
        notificationsApi.bulkHistory(),
      ]);
      setTemplates(tRes.data ?? []);
      setHistory(hRes.data ?? []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load data.");
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleBulkSend = async (e: FormEvent) => {
    e.preventDefault();
    setSending(true);
    setError("");
    setSuccess("");
    try {
      await notificationsApi.sendBulk({
        title,
        message,
        category: "general",
        priority: "NORMAL",
        target_type: targetType,
        target_filters: targetType === "role" ? { roles: ["STUDENT"] } : {},
        channels: { in_app: true, push: true, email: false },
      });
      setSuccess("Bulk notification queued.");
      setTitle("");
      setMessage("");
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Send failed.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Notifications</h1>
        <p className="text-sm text-muted-foreground">Bulk send, templates, and delivery history</p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
      )}
      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700">{success}</div>
      )}

      <form onSubmit={handleBulkSend} className="max-w-xl space-y-4 rounded-xl border border-border bg-surface p-6">
        <h2 className="text-lg font-semibold">Send bulk notification</h2>
        <input
          className="w-full rounded-lg border border-input px-3 py-2 text-sm"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <textarea
          className="w-full rounded-lg border border-input px-3 py-2 text-sm"
          placeholder="Message"
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          required
        />
        <select
          className="w-full rounded-lg border border-input px-3 py-2 text-sm"
          value={targetType}
          onChange={(e) => setTargetType(e.target.value)}
        >
          <option value="all">All users</option>
          <option value="role">Students (by role)</option>
        </select>
        <button
          type="submit"
          disabled={sending}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {sending ? "Sending…" : "Queue bulk send"}
        </button>
      </form>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Templates</h2>
        {templates.length === 0 ? (
          <p className="text-sm text-muted-foreground">No templates yet.</p>
        ) : (
          <ul className="divide-y divide-border rounded-xl border border-border">
            {templates.map((t) => (
              <li key={t.id} className="flex justify-between px-4 py-3 text-sm">
                <span className="font-medium">{t.name}</span>
                <span className="text-muted-foreground">{t.event_type}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Bulk history</h2>
        {history.length === 0 ? (
          <p className="text-sm text-muted-foreground">No bulk sends yet.</p>
        ) : (
          <ul className="divide-y divide-border rounded-xl border border-border">
            {history.map((b) => (
              <li key={b.id} className="px-4 py-3 text-sm">
                <p className="font-medium">{b.title}</p>
                <p className="text-muted-foreground">
                  {b.status} · {b.sent_count}/{b.total_recipients} sent
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
