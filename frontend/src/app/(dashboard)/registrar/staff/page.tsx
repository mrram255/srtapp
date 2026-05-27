"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Users, Search, Download, UserPlus, ChevronLeft, ChevronRight } from "lucide-react";
import api from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";

interface Staff {
  id: string;
  employee_id: string;
  full_name: string;
  email: string;
  phone: string;
  department_name: string;
  designation_name: string;
  staff_type: string;
  status: string;
}

interface ApiResponse {
  results: Staff[];
  count: number;
  next: string | null;
  previous: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  on_leave: "bg-yellow-100 text-yellow-700",
  deputation: "bg-blue-100 text-blue-700",
  resigned: "bg-gray-100 text-gray-600",
  retired: "bg-purple-100 text-purple-700",
  terminated: "bg-red-100 text-red-700",
};

const TYPE_COLORS: Record<string, string> = {
  teaching: "bg-accent/10 text-accent",
  non_teaching: "bg-muted text-muted-foreground",
  contract: "bg-orange-100 text-orange-700",
  visiting: "bg-blue-100 text-blue-700",
  guest: "bg-purple-100 text-purple-700",
};

export default function StaffPage() {
  const { user } = useAuthStore();
  const [staff, setStaff] = useState<Staff[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    if (!user?.id) return;
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (typeFilter) params.set("staff_type", typeFilter);
    if (statusFilter) params.set("status", statusFilter);
    params.set("page", String(page));

    api
      .get<ApiResponse>(`/staff/?${params.toString()}`)
      .then((r) => {
        setStaff(r.data.results ?? []);
        setTotalCount(r.data.count ?? 0);
      })
      .catch(() => setStaff([]))
      .finally(() => setLoading(false));
  }, [user?.id, search, typeFilter, statusFilter, page]);

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary flex items-center gap-2">
            <Users className="h-6 w-6" /> Staff Database
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">{totalCount} staff members total</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm hover:bg-muted">
            <Download className="h-4 w-4" /> Export
          </button>
          <Link
            href="/registrar/staff/new"
            className="flex items-center gap-1 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent/90"
          >
            <UserPlus className="h-4 w-4" /> Add Staff
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 rounded-xl border border-border bg-surface p-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search name, employee ID, email..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full rounded-lg border border-border bg-background pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Types</option>
          <option value="teaching">Teaching</option>
          <option value="non_teaching">Non-Teaching</option>
          <option value="contract">Contract</option>
          <option value="visiting">Visiting</option>
          <option value="guest">Guest</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="on_leave">On Leave</option>
          <option value="deputation">Deputation</option>
          <option value="resigned">Resigned</option>
          <option value="retired">Retired</option>
          <option value="terminated">Terminated</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border bg-surface shadow-card overflow-x-auto">
        {loading ? (
          <div className="flex min-h-[40vh] items-center justify-center">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
          </div>
        ) : staff.length === 0 ? (
          <div className="flex min-h-[40vh] flex-col items-center justify-center gap-2 text-muted-foreground">
            <Users className="h-12 w-12 opacity-30" />
            <p>No staff found</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-muted/40">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Staff</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Employee ID</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden md:table-cell">Designation</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden md:table-cell">Department</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden sm:table-cell">Type</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {staff.map((s) => (
                <tr key={s.id} className="hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold text-xs flex-shrink-0">
                        {s.full_name?.charAt(0) ?? "S"}
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{s.full_name}</p>
                        <p className="text-xs text-muted-foreground">{s.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-muted-foreground">{s.employee_id}</td>
                  <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">{s.designation_name ?? "—"}</td>
                  <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">{s.department_name ?? "—"}</td>
                  <td className="px-4 py-3 hidden sm:table-cell">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${TYPE_COLORS[s.staff_type] ?? "bg-muted text-muted-foreground"}`}>
                      {s.staff_type?.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[s.status] ?? "bg-gray-100 text-gray-600"}`}>
                      {s.status?.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/registrar/staff/${s.id}`}
                      className="rounded-lg bg-accent/10 px-3 py-1 text-xs font-medium text-accent hover:bg-accent/20"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, totalCount)} of {totalCount}</span>
          <div className="flex gap-2">
            <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
              className="rounded-lg border border-border px-3 py-1.5 hover:bg-muted disabled:opacity-40">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="rounded-lg border border-border px-3 py-1.5">{page} / {totalPages}</span>
            <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}
              className="rounded-lg border border-border px-3 py-1.5 hover:bg-muted disabled:opacity-40">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
