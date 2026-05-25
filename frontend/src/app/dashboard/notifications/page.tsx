"use client";

import { useEffect, useState } from "react";
import { notificationsApi, type UserNotification } from "@/lib/api/notifications";

const TYPE_ICON: Record<string, string> = {
  ANNOUNCEMENT: "📢",
  EVENT: "🎉",
  EXAM: "📝",
  FEE: "💰",
  ATTENDANCE: "📋",
  ASSIGNMENT: "📚",
  RESULT: "🏆",
  EMERGENCY: "🚨",
  GENERAL: "🔔",
};

const PRIORITY_COLOR: Record<string, string> = {
  LOW: "bg-gray-100 text-gray-600",
  NORMAL: "bg-blue-100 text-blue-600",
  HIGH: "bg-orange-100 text-orange-600",
  URGENT: "bg-red-100 text-red-600",
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<UserNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const [markingAll, setMarkingAll] = useState(false);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const params: Record<string, string> = filter === "unread" ? { is_read: "false" } : {};
      const res = await notificationsApi.list(params);
      setNotifications(res.data ?? []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load notifications.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const handleMarkRead = async (id: string) => {
    await notificationsApi.markRead(id);
    setNotifications((prev) =>
      prev.map((n) =>
        n.notification.id === id ? { ...n, is_read: true } : n
      )
    );
  };

  const handleMarkAllRead = async () => {
    try {
      setMarkingAll(true);
      await notificationsApi.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } finally {
      setMarkingAll(false);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
          <p className="text-sm text-gray-400">Loading notifications...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700">
        ⚠️ {error}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {unreadCount > 0 ? `${unreadCount} unread` : "All caught up!"}
          </p>
        </div>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllRead}
            disabled={markingAll}
            className="px-4 py-2 bg-blue-50 text-blue-600 text-sm font-medium rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
          >
            {markingAll ? "Marking..." : "✓ Mark all read"}
          </button>
        )}
      </div>

      <div className="flex bg-gray-100 rounded-xl p-1 gap-1 w-fit">
        {(["all", "unread"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-5 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
              filter === f
                ? "bg-white text-blue-600 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {f === "unread" ? `Unread (${unreadCount})` : "All"}
          </button>
        ))}
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-16 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
          <p className="text-4xl mb-3">🔔</p>
          <p className="text-gray-500 font-medium">No notifications</p>
          <p className="text-gray-400 text-sm mt-1">You are all caught up!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((item) => (
            <NotificationCard
              key={item.id}
              item={item}
              onMarkRead={handleMarkRead}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function NotificationCard({
  item,
  onMarkRead,
}: {
  item: UserNotification;
  onMarkRead: (id: string) => void;
}) {
  const { notification, is_read } = item;
  const icon = TYPE_ICON[notification.notification_type] ?? "🔔";
  const priorityColor = PRIORITY_COLOR[notification.priority] ?? "bg-gray-100 text-gray-600";

  return (
    <div className={`bg-white border rounded-xl p-4 shadow-sm transition-all ${
      !is_read ? "border-blue-200 border-l-4 border-l-blue-500" : "border-gray-100"
    }`}>
      <div className="flex items-start gap-3">
        <div className="text-2xl shrink-0">{icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className={`font-semibold text-sm ${!is_read ? "text-gray-900" : "text-gray-600"}`}>
              {notification.title}
            </h3>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${priorityColor}`}>
              {notification.priority}
            </span>
            {!is_read && <span className="w-2 h-2 bg-blue-500 rounded-full shrink-0" />}
          </div>
          <p className="text-sm text-gray-500 line-clamp-2">{notification.message}</p>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-gray-400">
              {new Date(notification.created_at).toLocaleDateString("en-IN", {
                day: "numeric", month: "short", year: "numeric",
                hour: "2-digit", minute: "2-digit",
              })}
            </p>
            {!is_read && (
              <button
                onClick={() => onMarkRead(notification.id)}
                className="text-xs text-blue-600 font-medium hover:underline"
              >
                Mark read
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
