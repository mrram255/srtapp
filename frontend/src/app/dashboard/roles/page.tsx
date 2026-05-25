"use client";

import { useEffect, useState } from "react";

import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type RoleRow = {
  id: string;
  name: string;
  display_name: string;
  description: string;
  is_system_role: boolean;
  user_count: number;
};

type PermissionMatrixRow = {
  id: number;
  module: string;
  module_display: string;
  action: string;
  assigned: boolean;
};

type RoleDetail = RoleRow & {
  permission_matrix: PermissionMatrixRow[];
};

export default function RolesPage() {
  const [roles, setRoles] = useState<RoleRow[]>([]);
  const [selected, setSelected] = useState<RoleDetail | null>(null);
  const [loading, setLoading] = useState(true);
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
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load role details."));
    }
  };

  return (
    <div className="grid gap-6 p-6 lg:grid-cols-[320px_1fr]">
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Roles</h1>
          <p className="text-sm text-gray-500">System and custom roles with RBAC permissions</p>
        </div>

        {error ? <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

        <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
          {loading ? (
            <p className="p-4 text-sm text-gray-500">Loading roles...</p>
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
          <p className="text-sm text-gray-500">Select a role to view its permission matrix.</p>
        ) : (
          <>
            <div className="mb-6 flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{selected.display_name}</h2>
                <p className="text-sm text-gray-500">{selected.description}</p>
              </div>
              {selected.is_system_role ? (
                <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">System role</span>
              ) : null}
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-100 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium text-gray-600">Module</th>
                    <th className="px-3 py-2 text-left font-medium text-gray-600">Action</th>
                    <th className="px-3 py-2 text-left font-medium text-gray-600">Assigned</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {selected.permission_matrix
                    .filter((row) => row.assigned)
                    .map((row) => (
                      <tr key={`${row.id}-${row.action}`}>
                        <td className="px-3 py-2">{row.module_display}</td>
                        <td className="px-3 py-2 capitalize">{row.action}</td>
                        <td className="px-3 py-2">
                          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700">Yes</span>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
