"use client";

import { useCallback, useEffect, useState } from "react";

import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type AcademicYear = { id: string; year: string; is_current: boolean };
type Department = { id: string; name: string; code: string; program_count?: number };
type Program = { id: string; name: string; code: string; department_name?: string };
type Holiday = { id: string; date: string; name: string; holiday_type: string };
type Subject = { id: string; name: string; code: string; semester_number: number };

const TABS = [
  "Academic Years",
  "Departments",
  "Programs",
  "Subjects",
  "Holidays",
  "Calendar",
] as const;

export default function AcademicConfigPage() {
  const [tab, setTab] = useState<(typeof TABS)[number]>("Academic Years");
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [programs, setPrograms] = useState<Program[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [importing, setImporting] = useState(false);
  const [calendar, setCalendar] = useState<{ holidays: Holiday[]; events: { title: string; start_date: string }[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [yRes, dRes, pRes, hRes, sRes] = await Promise.all([
        api.get<ApiEnvelope<AcademicYear[]>>("/academic-years/?limit=20"),
        api.get<ApiEnvelope<Department[]>>("/departments/?limit=50"),
        api.get<ApiEnvelope<Program[]>>("/programs/?limit=50"),
        api.get<ApiEnvelope<Holiday[]>>("/holidays/?limit=50"),
        api.get<ApiEnvelope<Subject[]>>("/subjects/?limit=50"),
      ]);
      setYears(yRes.data.data ?? []);
      setDepartments(dRes.data.data ?? []);
      setPrograms(pRes.data.data ?? []);
      setHolidays(hRes.data.data ?? []);
      setSubjects(sRes.data.data ?? []);
      const currentYear = (yRes.data.data ?? []).find((y) => y.is_current);
      if (currentYear) {
        const calRes = await api.get<ApiEnvelope<{ holidays: Holiday[]; events: { title: string; start_date: string }[] }>>(
          `/academic-calendar/?academic_year=${currentYear.id}`,
        );
        setCalendar(calRes.data.data ?? null);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load academic configuration."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const activateYear = async (id: string) => {
    try {
      await api.post(`/academic-years/${id}/activate/`);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to activate academic year."));
    }
  };

  if (loading) {
    return <div className="p-6 text-sm text-gray-500">Loading academic configuration…</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Academic Configuration</h1>
        <p className="text-sm text-gray-500">Years, departments, programs, holidays, and calendar</p>
      </div>

      {error ? <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</p> : null}

      <div className="flex flex-wrap gap-2 border-b border-gray-100 pb-2">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-3 py-2 text-sm font-medium ${tab === t ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "Academic Years" ? (
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-left">
              <tr>
                <th className="px-4 py-3">Year</th>
                <th className="px-4 py-3">Current</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {years.map((y) => (
                <tr key={y.id} className="border-t">
                  <td className="px-4 py-3 font-medium">{y.year}</td>
                  <td className="px-4 py-3">{y.is_current ? "Yes" : "No"}</td>
                  <td className="px-4 py-3">
                    {!y.is_current ? (
                      <button
                        type="button"
                        className="text-indigo-600 hover:underline"
                        onClick={() => void activateYear(y.id)}
                      >
                        Set current
                      </button>
                    ) : (
                      <span className="text-gray-400">Active</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {tab === "Departments" ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {departments.map((d) => (
            <a
              key={d.id}
              href={`/dashboard/academic/departments/${d.id}`}
              className="rounded-xl border bg-white p-4 shadow-sm transition hover:border-indigo-300"
            >
              <h3 className="font-semibold text-gray-900">{d.name}</h3>
              <p className="text-xs text-gray-500">{d.code}</p>
              <p className="mt-2 text-sm text-gray-600">{d.program_count ?? 0} programs</p>
            </a>
          ))}
        </div>
      ) : null}

      {tab === "Subjects" ? (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <a
              href="/api/v1/subjects/import-template/"
              className="rounded-lg border bg-white px-3 py-2 text-sm text-indigo-600 hover:bg-indigo-50"
            >
              Download template
            </a>
            <label className="cursor-pointer rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700">
              {importing ? "Importing…" : "Bulk import Excel"}
              <input
                type="file"
                accept=".xlsx,.xls"
                className="hidden"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  setImporting(true);
                  setError("");
                  try {
                    const fd = new FormData();
                    fd.append("file", file);
                    await api.post("/subjects/bulk-import/", fd);
                    await load();
                  } catch (err) {
                    setError(getApiErrorMessage(err, "Subject import failed."));
                  } finally {
                    setImporting(false);
                  }
                }}
              />
            </label>
          </div>
          <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="px-4 py-3">Subject</th>
                  <th className="px-4 py-3">Code</th>
                  <th className="px-4 py-3">Semester</th>
                </tr>
              </thead>
              <tbody>
                {subjects.map((s) => (
                  <tr key={s.id} className="border-t">
                    <td className="px-4 py-3">{s.name}</td>
                    <td className="px-4 py-3">{s.code}</td>
                    <td className="px-4 py-3">{s.semester_number}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {tab === "Programs" ? (
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-left">
              <tr>
                <th className="px-4 py-3">Program</th>
                <th className="px-4 py-3">Code</th>
                <th className="px-4 py-3">Department</th>
              </tr>
            </thead>
            <tbody>
              {programs.map((p) => (
                <tr key={p.id} className="border-t">
                  <td className="px-4 py-3">{p.name}</td>
                  <td className="px-4 py-3">{p.code}</td>
                  <td className="px-4 py-3 text-gray-500">{p.department_name ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {tab === "Holidays" ? (
        <ul className="divide-y rounded-xl border bg-white shadow-sm">
          {holidays.map((h) => (
            <li key={h.id} className="flex justify-between px-4 py-3 text-sm">
              <span className="font-medium">{h.name}</span>
              <span className="text-gray-500">
                {h.date} · {h.holiday_type}
              </span>
            </li>
          ))}
        </ul>
      ) : null}

      {tab === "Calendar" ? (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="mb-3 font-semibold">Holidays</h3>
            <ul className="space-y-2 text-sm">
              {(calendar?.holidays ?? []).map((h) => (
                <li key={h.id}>
                  {h.date} — {h.name}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border bg-white p-4 shadow-sm">
            <h3 className="mb-3 font-semibold">Events</h3>
            <ul className="space-y-2 text-sm">
              {(calendar?.events ?? []).map((e, i) => (
                <li key={`${e.title}-${i}`}>
                  {e.start_date} — {e.title}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
    </div>
  );
}
