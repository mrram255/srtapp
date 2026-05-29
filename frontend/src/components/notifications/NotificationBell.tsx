"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Bell } from "lucide-react";
import { notificationsApi, type UserNotification } from "@/lib/api/notifications";

const POLL_MS = 30_000;

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState<UserNotification[]>([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const [listRes, countRes] = await Promise.all([
        notificationsApi.list({ limit: "10" }),
        notificationsApi.unreadCount(),
      ]);
      setItems(listRes.data ?? []);
      setUnread(countRes.data?.unread_count ?? 0);
    } catch {
      setItems([]);
      setUnread(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = setInterval(() => void refresh(), POLL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  const handleMarkRead = async (notificationId: string) => {
    await notificationsApi.markRead(notificationId);
    setItems((prev) =>
      prev.map((n) =>
        n.notification.id === notificationId ? { ...n, is_read: true } : n,
      ),
    );
    setUnread((c) => Math.max(0, c - 1));
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => {
          setOpen((v) => !v);
          if (!open) void refresh();
        }}
        className="relative rounded-lg p-2 text-muted-foreground hover:bg-muted"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unread > 0 && (
          <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-accent px-1 text-[10px] font-bold text-white">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-xl border border-border bg-surface shadow-elevated">
          <div className="flex items-center justify-between border-b border-border p-4">
            <h3 className="font-semibold text-foreground">Notifications</h3>
            {unread > 0 && (
              <span className="text-xs text-muted-foreground">{unread} unread</span>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto p-2">
            {loading && items.length === 0 ? (
              <p className="p-3 text-sm text-muted-foreground">Loading…</p>
            ) : items.length === 0 ? (
              <p className="p-3 text-sm text-muted-foreground">No notifications yet.</p>
            ) : (
              items.slice(0, 10).map((item) => (
                <div
                  key={item.id}
                  className={`rounded-lg p-3 hover:bg-muted ${!item.is_read ? "bg-muted/50" : ""}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium text-foreground">{item.notification.title}</p>
                    {!item.is_read && (
                      <button
                        type="button"
                        onClick={() => void handleMarkRead(item.notification.id)}
                        className="shrink-0 text-xs text-accent hover:underline"
                      >
                        Read
                      </button>
                    )}
                  </div>
                  <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                    {item.notification.message}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {new Date(item.notification.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            )}
          </div>
          <div className="border-t border-border p-3">
            <Link
              href="/dashboard/notifications"
              className="block text-center text-sm text-accent hover:underline"
              onClick={() => setOpen(false)}
            >
              View all
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
