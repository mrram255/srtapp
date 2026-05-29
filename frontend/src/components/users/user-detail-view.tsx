"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import {
  PermissionMatrixEditor,
  type MatrixRow,
} from "@/components/users/permission-matrix-editor";
import { ProtectedRoute } from "@/components/shared/ProtectedRoute";
import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type UserDetail = {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  masked_phone: string;
  role_display: string;
  role_slug: string | null;
  college_name: string;
  is_active: boolean;
  joined_at: string | null;
  permission_matrix: MatrixRow[];
};

type Activity = {
  id: string;
  action: string;
  module: string;
  description: string;
  created_at: string;
};

type SessionRow = {
  id: string;
  ip_address: string;
  user_agent: string;
  device_type: string;
  last_activity: string;
  created_at: string;
};

type UserDetailViewProps = {
  listPath?: string;
};

export function UserDetailView({ listPath = "/super-admin/users" }: UserDetailViewProps) {
  const params = useParams<{ id: string }>();
  const [user, setUser] = useState<UserDetail | null>(null);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [sessions, setSessions] = useState<SessionRow[]>([]);
  const [tab, setTab] = useState<"profile" | "permissions" | "activity" | "sessions">("profile");
  const [error, setError] = useState("");
  const [killing, setKilling] = useState<string | null>(null);

  const load = async () => {
    if (!params.id) return;
    try {
      const [detailRes, activityRes, sessionsRes] = await Promise.all([
        api.get<ApiEnvelope<UserDetail>>(`/users/${params.id}/`),
        api.get<ApiEnvelope<Activity[]>>(`/users/${params.id}/activity/`),
        api.get<ApiEnvelope<SessionRow[]>>(`/users/${params.id}/sessions/`),
      ]);
      setUser(detailRes.data.data ?? null);
      setActivity(activityRes.data.data ?? []);
      setSessions(sessionsRes.data.data ?? []);
      setError("");
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load user."));
    }
  };

  useEffect(() => {
    void load();
  }, [params.id]);

  async function killSession(sessionId: string) {
    if (!params.id) return;
    setKilling(sessionId);
    try {
      await api.post(`/users/${params.id}/sessions/kill/`, { session_id: sessionId });
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to terminate session."));
    } finally {
      setKilling(null);
    }
  }

  return (
    <ProtectedRoute roles={["SUPER_ADMIN"]}>
      {error ? (
        <div className="p-6">
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
          <Link href={listPath} className="mt-4 inline-block text-blue-600 hover:underline">
            Back to users
          </Link>
        </div>
      ) : !user ? (
        <div className="p-6 text-gray-500">Loading user…</div>
      ) : (
        <div className="space-y-6 p-6">
          <div className="flex items-center justify-between">
            <div>
              <Link href={listPath} className="text-sm text-blue-600 hover:underline">
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

          <div className="flex flex-wrap gap-2 border-b border-gray-200">
            {(["profile", "permissions", "activity", "sessions"] as const).map((item) => (
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
                <p className="font-medium text-gray-900">
                  {user.joined_at ? new Date(user.joined_at).toLocaleDateString() : "—"}
                </p>
              </div>
            </div>
          ) : null}

          {tab === "permissions" ? (
            <div className="space-y-3 rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Role permissions</h2>
                <Link href="/super-admin/roles" className="text-sm text-blue-600 hover:underline">
                  Edit roles →
                </Link>
              </div>
              <PermissionMatrixEditor rows={user.permission_matrix ?? []} readOnly />
            </div>
          ) : null}

          {tab === "activity" ? (
            <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-900">Activity log</h2>
              <div className="space-y-3">
                {activity.length === 0 ? (
                  <p className="text-sm text-gray-500">No activity recorded.</p>
                ) : (
                  activity.map((item) => (
                    <div key={item.id} className="rounded-lg border border-gray-100 p-3">
                      <div className="flex items-center justify-between gap-4">
                        <p className="font-medium text-gray-900">{item.description || item.action}</p>
                        <span className="text-xs text-gray-400">
                          {new Date(item.created_at).toLocaleString()}
                        </span>
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

          {tab === "sessions" ? (
            <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-900">Active sessions</h2>
              {sessions.length === 0 ? (
                <p className="text-sm text-gray-500">No active sessions.</p>
              ) : (
                <div className="space-y-3">
                  {sessions.map((session) => (
                    <div
                      key={session.id}
                      className="flex flex-wrap items-start justify-between gap-3 rounded-lg border border-gray-100 p-3"
                    >
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {session.device_type} · {session.ip_address}
                        </p>
                        <p className="text-xs text-gray-500">{session.user_agent}</p>
                        <p className="text-xs text-gray-400">
                          Last active {new Date(session.last_activity).toLocaleString()}
                        </p>
                      </div>
                      <button
                        type="button"
                        disabled={killing === session.id}
                        onClick={() => void killSession(session.id)}
                        className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-50 disabled:opacity-60"
                      >
                        {killing === session.id ? "Ending…" : "Kill session"}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : null}
        </div>
      )}
    </ProtectedRoute>
  );
}
