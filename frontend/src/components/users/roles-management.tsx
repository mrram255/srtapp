"use client";

import { useEffect, useState } from "react";

import {
  PermissionMatrixEditor,
  type MatrixRow,
} from "@/components/users/permission-matrix-editor";
import { ProtectedRoute } from "@/components/shared/ProtectedRoute";
import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type RoleRow = {
  id: string;
  name: string;
  display_name: string;
  description: string;
  is_system_role: boolean;
  user_count: number;
};

type RoleDetail = RoleRow & {
  permission_matrix: MatrixRow[];
};

export function RolesManagement() {
  const [roles, setRoles] = useState<RoleRow[]>([]);
  const [selected, setSelected] = useState<RoleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    void (async () => {
      setLoading(true);
      try {
        const response = await api.get<ApiEnvelope<RoleRow[]>>("/roles/?limit=50");
        setRoles(response.data.data ?? []);
      } catch (err) {
        setError(getApiErrorMessage(err, "Failed to load roles."));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const loadRoleDetail = async (roleId: string) => {
    try {
      const response = await api.get<ApiEnvelope<RoleDetail>>(`/roles/${roleId}/`);
      setSelected(response.data.data ?? null);
      setError("");
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load role details."));
    }
  };

  async function savePermissions(permissionIds: number[]) {
    if (!selected) return;
    setSaving(true);
    try {
      await api.post(`/roles/${selected.id}/permissions/`, { permissions: permissionIds });
      await loadRoleDetail(selected.id);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to save permissions."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <ProtectedRoute roles={["SUPER_ADMIN"]}>
      <div className="grid gap-6 p-6 lg:grid-cols-[320px_1fr]">
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Role management</h1>
            <p className="text-sm text-gray-500">Permission matrix per role (module × action)</p>
          </div>

          {error ? <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

          <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
            {loading ? (
              <p className="p-4 text-sm text-gray-500">Loading roles…</p>
            ) : (
              <ul className="divide-y divide-gray-100">
                {roles.map((role) => (
                  <li key={role.id}>
                    <button
                      type="button"
                      onClick={() => void loadRoleDetail(role.id)}
                      className={`flex w-full items-start justify-between px-4 py-3 text-left hover:bg-gray-50 ${
                        selected?.id === role.id ? "bg-blue-50" : ""
                      }`}
                    >
                      <div>
                        <p className="font-medium text-gray-900">{role.display_name}</p>
                        <p className="text-xs text-gray-500">{role.name}</p>
                      </div>
                      <span className="text-xs text-gray-400">{role.user_count} users</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
          {!selected ? (
            <p className="text-sm text-gray-500">Select a role to edit its permission matrix.</p>
          ) : (
            <>
              <div className="mb-6 flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{selected.display_name}</h2>
                  <p className="text-sm text-gray-500">{selected.description}</p>
                </div>
                {selected.is_system_role ? (
                  <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
                    System role
                  </span>
                ) : null}
              </div>

              <PermissionMatrixEditor
                key={selected.id}
                rows={selected.permission_matrix}
                readOnly={selected.is_system_role}
                saving={saving}
                onSave={selected.is_system_role ? undefined : savePermissions}
              />
            </>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
