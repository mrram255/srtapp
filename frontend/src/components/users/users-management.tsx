"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { Upload, UserPlus } from "lucide-react";

import { ProtectedRoute } from "@/components/shared/ProtectedRoute";
import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type UserRow = {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role_display: string;
  is_active: boolean;
};

type RoleOption = { id: string; name: string; display_name: string };

type UsersManagementProps = {
  basePath?: string;
};

export function UsersManagement({ basePath = "/super-admin/users" }: UsersManagementProps) {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [roles, setRoles] = useState<RoleOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<string>("");
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState({
    email: "",
    phone: "",
    first_name: "",
    last_name: "",
    role_ref: "",
    password: "ChangeMe@123",
  });

  const loadUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (roleFilter) params.set("role", roleFilter);
      const qs = params.toString();
      const path = qs ? `/users/?${qs}` : "/users/";
      const response = await api.get<ApiEnvelope<UserRow[]>>(path);
      setUsers(response.data.data ?? []);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load users."));
    } finally {
      setLoading(false);
    }
  }, [search, roleFilter]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    void (async () => {
      try {
        const response = await api.get<ApiEnvelope<RoleOption[]>>("/roles/?limit=50");
        setRoles(response.data.data ?? []);
      } catch {
        /* optional */
      }
    })();
  }, []);

  async function downloadTemplate() {
    try {
      const response = await api.get("/users/import-template/", { responseType: "blob" });
      const url = window.URL.createObjectURL(response.data);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "user_import_template.xlsx";
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to download template."));
    }
  }

  async function exportUsers() {
    try {
      const response = await api.get("/users/export/", { responseType: "blob" });
      const url = window.URL.createObjectURL(response.data);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "users.xlsx";
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to export users."));
    }
  }

  async function handleBulkImport(file: File) {
    setImporting(true);
    setImportResult("");
    setError("");
    try {
      const body = new FormData();
      body.append("file", file);
      const response = await api.post<ApiEnvelope<{ created: number; errors: Array<{ row: number; error: string }> }>>(
        "/users/bulk-create/",
        body,
        { headers: { "Content-Type": "multipart/form-data" } },
      );
      const result = response.data.data;
      setImportResult(`Imported ${result?.created ?? 0} users. ${result?.errors?.length ?? 0} errors.`);
      await loadUsers();
    } catch (err) {
      setError(getApiErrorMessage(err, "Bulk import failed."));
    } finally {
      setImporting(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function handleCreateUser(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError("");
    try {
      await api.post("/users/", {
        ...form,
        role_ref: form.role_ref || undefined,
      });
      setShowCreate(false);
      setForm({
        email: "",
        phone: "",
        first_name: "",
        last_name: "",
        role_ref: "",
        password: "ChangeMe@123",
      });
      await loadUsers();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to create user."));
    } finally {
      setCreating(false);
    }
  }

  return (
    <ProtectedRoute roles={["SUPER_ADMIN"]}>
      <div className="space-y-6 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
            <p className="text-sm text-gray-500">Accounts, roles, bulk import, and session control</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void downloadTemplate()}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium hover:bg-gray-50"
            >
              Import template
            </button>
            <button
              type="button"
              onClick={() => void exportUsers()}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium hover:bg-gray-50"
            >
              Export Excel
            </button>
            <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium hover:bg-gray-50">
              <Upload className="h-4 w-4" />
              {importing ? "Importing…" : "Bulk import"}
              <input
                ref={fileRef}
                type="file"
                accept=".xlsx,.xls"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) void handleBulkImport(file);
                }}
              />
            </label>
            <button
              type="button"
              onClick={() => setShowCreate(true)}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              <UserPlus className="h-4 w-4" />
              Add user
            </button>
          </div>
        </div>

        {importResult ? (
          <div className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">{importResult}</div>
        ) : null}
        {error ? <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}

        {showCreate ? (
          <form
            onSubmit={(e) => void handleCreateUser(e)}
            className="grid gap-3 rounded-xl border border-gray-100 bg-white p-4 shadow-sm md:grid-cols-2"
          >
            <input
              required
              placeholder="Email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
            />
            <input
              required
              placeholder="Phone (+91...)"
              value={form.phone}
              onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
            />
            <input
              required
              placeholder="First name"
              value={form.first_name}
              onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
            />
            <input
              required
              placeholder="Last name"
              value={form.last_name}
              onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
            />
            <select
              required
              value={form.role_ref}
              onChange={(e) => setForm((f) => ({ ...f, role_ref: e.target.value }))}
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm md:col-span-2"
            >
              <option value="">Select role</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.display_name}
                </option>
              ))}
            </select>
            <input
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              className="rounded-lg border border-gray-200 px-3 py-2 text-sm md:col-span-2"
            />
            <div className="flex gap-2 md:col-span-2">
              <button
                type="submit"
                disabled={creating}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              >
                {creating ? "Creating…" : "Create user"}
              </button>
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="rounded-lg border border-gray-200 px-4 py-2 text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : null}

        <div className="flex flex-wrap gap-3 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search name, email, phone…"
            className="min-w-[220px] flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm"
          />
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="rounded-lg border border-gray-200 px-3 py-2 text-sm"
          >
            <option value="">All roles</option>
            {roles.map((role) => (
              <option key={role.id} value={role.name.toUpperCase()}>
                {role.display_name}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => void loadUsers()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Apply filters
          </button>
        </div>

        <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-100 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Name</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Email</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Phone</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Role</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    Loading users…
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    No users found.
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{user.full_name}</td>
                    <td className="px-4 py-3 text-gray-600">{user.email}</td>
                    <td className="px-4 py-3 text-gray-600">{user.phone}</td>
                    <td className="px-4 py-3 text-gray-600">{user.role_display}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-medium ${
                          user.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`${basePath}/${user.id}`} className="text-blue-600 hover:underline">
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </ProtectedRoute>
  );
}
