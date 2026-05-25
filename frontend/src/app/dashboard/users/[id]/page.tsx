"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type UserDetail = {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  masked_phone: string;
  role_display: string;
  college_name: string;
  is_active: boolean;
  joined_at: string | null;
  accessible_modules: Array<{ name: string; display_name: string }>;
};

type Activity = {
  id: string;
  action: string;
  module: string;
  description: string;
  created_at: string;
};

export default function UserDetailPage() {
  const params = useParams<{ id: string }>();
  const [user, setUser] = useState<UserDetail | null>(null);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [tab, setTab] = useState<"profile" | "permissions" | "activity">("profile");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!params.id) return;
    void (async () => {
      try {
        const [detailRes, activityRes] = await Promise.all([
          api.get<ApiEnvelope<UserDetail>>(`/users/${params.id}/`),
          api.get<ApiEnvelope<Activity[]>>(`/users/${params.id}/activity/`),
        ]);
        setUser(detailRes.data.data ?? null);
        setActivity(activityRes.data.data ?? []);
      } catch (err) {
        setError(getApiErrorMessage(err, "Failed to load user."));
      }
    })();
  }, [params.id]);

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
        <Link href="/dashboard/users" className="mt-4 inline-block text-blue-600 hover:underline">
          Back to users
        </Link>
      </div>
    );
  }

  if (!user) {
    return <div className="p-6 text-gray-500">Loading user...</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/dashboard/users" className="text-sm text-blue-600 hover:underline">
            ← Back to users
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{user.full_name}</h1>
          <p className="text-sm text-gray-500">{user.email}</p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-sm font-medium ${
            user.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"
          }`}
        >
          {user.is_active ? "Active" : "Inactive"}
        </span>
      </div>

      <div className="flex gap-2 border-b border-gray-200">
        {(["profile", "permissions", "activity"] as const).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setTab(item)}
            className={`px-4 py-2 text-sm font-medium capitalize ${
              tab === item ? "border-b-2 border-blue-600 text-blue-600" : "text-gray-500"
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {tab === "profile" ? (
        <div className="grid gap-4 rounded-xl border border-gray-100 bg-white p-6 shadow-sm md:grid-cols-2">
          <div>
            <p className="text-xs uppercase text-gray-400">Role</p>
            <p className="font-medium text-gray-900">{user.role_display}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-gray-400">Phone</p>
            <p className="font-medium text-gray-900">{user.masked_phone || user.phone}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-gray-400">College</p>
            <p className="font-medium text-gray-900">{user.college_name || "—"}</p>
          </div>
          <div>
            <p className="text-xs uppercase text-gray-400">Joined</p>
            <p className="font-medium text-gray-900">{user.joined_at ? new Date(user.joined_at).toLocaleDateString() : "—"}</p>
          </div>
        </div>
      ) : null}

      {tab === "permissions" ? (
        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Accessible Modules</h2>
          <div className="flex flex-wrap gap-2">
            {user.accessible_modules?.length ? (
              user.accessible_modules.map((module) => (
                <span key={module.name} className="rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-700">
                  {module.display_name}
                </span>
              ))
            ) : (
              <p className="text-sm text-gray-500">No module permissions assigned.</p>
            )}
          </div>
        </div>
      ) : null}

      {tab === "activity" ? (
        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Activity Log</h2>
          <div className="space-y-3">
            {activity.length === 0 ? (
              <p className="text-sm text-gray-500">No activity recorded.</p>
            ) : (
              activity.map((item) => (
                <div key={item.id} className="rounded-lg border border-gray-100 p-3">
                  <div className="flex items-center justify-between gap-4">
                    <p className="font-medium text-gray-900">{item.description || item.action}</p>
                    <span className="text-xs text-gray-400">{new Date(item.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-xs text-gray-500">
                    {item.module} · {item.action}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
