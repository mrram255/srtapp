"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  GraduationCap, Search, Filter, Download, Upload, UserPlus, ChevronLeft, ChevronRight,
} from "lucide-react";
import api from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";

interface Student {
  id: string;
  enrollment_number: string;
  roll_number: string;
  full_name: string;
  department_name: string;
  semester: number;
  batch_year: number;
  student_status: string;
  gender: string;
  category: string;
  photo?: string;
}

interface ApiResponse {
  results: Student[];
  count: number;
  next: string | null;
  previous: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  detained: "bg-red-100 text-red-700",
  suspended: "bg-orange-100 text-orange-700",
  passout: "bg-blue-100 text-blue-700",
  alumni: "bg-purple-100 text-purple-700",
  dropped_out: "bg-gray-100 text-gray-600",
  year_back: "bg-yellow-100 text-yellow-700",
  semester_back: "bg-yellow-100 text-yellow-600",
};

export default function StudentsPage() {
  const { user } = useAuthStore();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    if (!user?.id) return;
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (statusFilter) params.set("student_status", statusFilter);
    if (categoryFilter) params.set("category", categoryFilter);
    params.set("page", String(page));

    api
      .get<ApiResponse>(`/students/?${params.toString()}`)
      .then((r) => {
        setStudents(r.data.results ?? []);
        setTotalCount(r.data.count ?? 0);
      })
      .catch(() => setStudents([]))
      .finally(() => setLoading(false));
  }, [user?.id, search, statusFilter, categoryFilter, page]);

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary flex items-center gap-2">
            <GraduationCap className="h-6 w-6" /> Student Master Database
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {totalCount} students total
          </p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm hover:bg-muted">
            <Upload className="h-4 w-4" /> Import
          </button>
          <button className="flex items-center gap-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm hover:bg-muted">
            <Download className="h-4 w-4" /> Export
          </button>
          <Link
            href="/registrar/students/new"
            className="flex items-center gap-1 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent/90"
          >
            <UserPlus className="h-4 w-4" /> Add Student
          </Link>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 rounded-xl border border-border bg-surface p-4">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search name, enrollment, phone..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full rounded-lg border border-border bg-background pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="detained">Detained</option>
          <option value="suspended">Suspended</option>
          <option value="passout">Passout</option>
          <option value="alumni">Alumni</option>
          <option value="dropped_out">Dropped Out</option>
          <option value="year_back">Year Back</option>
          <option value="semester_back">Semester Back</option>
        </select>
        <select
          value={categoryFilter}
          onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Categories</option>
          <option value="general">General</option>
          <option value="obc">OBC</option>
          <option value="sc">SC</option>
          <option value="st">ST</option>
          <option value="ews">EWS</option>
        </select>
        <button className="flex items-center gap-1 rounded-lg border border-border bg-background px-3 py-2 text-sm hover:bg-muted">
          <Filter className="h-4 w-4" /> More Filters
        </button>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border bg-surface shadow-card overflow-x-auto">
        {loading ? (
          <div className="flex min-h-[40vh] items-center justify-center">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
          </div>
        ) : students.length === 0 ? (
          <div className="flex min-h-[40vh] flex-col items-center justify-center gap-2 text-muted-foreground">
            <GraduationCap className="h-12 w-12 opacity-30" />
            <p>No students found</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-border bg-muted/40">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Student</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Enrollment</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden md:table-cell">Department</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden sm:table-cell">Semester</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground hidden lg:table-cell">Category</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
                <th className="px-4 py-3 text-left font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {students.map((s) => (
                <tr key={s.id} className="hover:bg-muted/20 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-accent/20 flex items-center justify-center text-accent font-semibold text-xs flex-shrink-0">
                        {s.full_name?.charAt(0) ?? "S"}
                      </div>
                      <span className="font-medium text-foreground">{s.full_name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-muted-foreground">{s.enrollment_number}</td>
                  <td className="px-4 py-3 text-muted-foreground hidden md:table-cell">{s.department_name ?? "—"}</td>
                  <td className="px-4 py-3 text-muted-foreground hidden sm:table-cell">Sem {s.semester}</td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    <span className="rounded-full bg-muted px-2 py-0.5 text-xs uppercase">{s.category ?? "—"}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${STATUS_COLORS[s.student_status] ?? "bg-gray-100 text-gray-600"}`}>
                      {s.student_status?.replace(/_/g, " ") ?? "—"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/registrar/students/${s.id}`}
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

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, totalCount)} of {totalCount}</span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="rounded-lg border border-border px-3 py-1.5 hover:bg-muted disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="rounded-lg border border-border px-3 py-1.5">{page} / {totalPages}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="rounded-lg border border-border px-3 py-1.5 hover:bg-muted disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
