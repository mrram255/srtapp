"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type Dept = { id: string; name: string; code: string; hod_name?: string };
type Stats = {
  programs: number;
  batches: number;
  subjects: number;
  students: number;
  faculty: number;
};
type Faculty = { id: string; full_name: string; email: string; role: string };

export default function DepartmentDetailPage() {
  const params = useParams();
  const id = String(params.id);
  const [dept, setDept] = useState<Dept | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [faculty, setFaculty] = useState<Faculty[]>([]);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      const [dRes, sRes, fRes] = await Promise.all([
        api.get<ApiEnvelope<Dept>>(`/departments/${id}/`),
        api.get<ApiEnvelope<Stats>>(`/departments/${id}/stats/`),
        api.get<ApiEnvelope<Faculty[]>>(`/departments/${id}/faculty/`),
      ]);
      setDept(dRes.data.data ?? null);
      setStats(sRes.data.data ?? null);
      setFaculty(fRes.data.data ?? []);
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load department."));
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!dept && !error) {
    return <div className="p-6 text-sm text-gray-500">Loading department…</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <Link href="/dashboard/academic" className="text-sm text-indigo-600 hover:underline">
        ← Academic configuration
      </Link>
      {error ? <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</p> : null}
      {dept ? (
        <>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{dept.name}</h1>
            <p className="text-sm text-gray-500">{dept.code}</p>
            {dept.hod_name ? <p className="mt-1 text-sm">HOD: {dept.hod_name}</p> : null}
          </div>
          {stats ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              {(
                [
                  ["Programs", stats.programs],
                  ["Batches", stats.batches],
                  ["Subjects", stats.subjects],
                  ["Students", stats.students],
                  ["Faculty", stats.faculty],
                ] as const
              ).map(([label, value]) => (
                <div key={label} className="rounded-xl border bg-white p-4 shadow-sm">
                  <p className="text-xs text-gray-500">{label}</p>
                  <p className="text-2xl font-semibold">{value}</p>
                </div>
              ))}
            </div>
          ) : null}
          <div className="rounded-xl border bg-white p-4 shadow-sm">
            <h2 className="mb-3 font-semibold">Faculty</h2>
            <ul className="divide-y text-sm">
              {faculty.map((f) => (
                <li key={f.id} className="flex justify-between py-2">
                  <span>{f.full_name}</span>
                  <span className="text-gray-500">
                    {f.role} · {f.email}
                  </span>
                </li>
              ))}
              {faculty.length === 0 ? <li className="py-2 text-gray-400">No faculty assigned</li> : null}
            </ul>
          </div>
        </>
      ) : null}
    </div>
  );
}
