"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft, User, BookOpen, Users, FileText, DollarSign, BarChart2, Award,
} from "lucide-react";
import api from "@/lib/api/client";

interface StudentDetail {
  id: string;
  enrollment_number: string;
  roll_number: string;
  full_name: string;
  email: string;
  phone: string;
  gender: string;
  date_of_birth: string;
  student_status: string;
  semester: number;
  batch_year: number;
  department_name: string;
  category: string;
  blood_group: string;
  nationality: string;
  address: string;
  city: string;
  state: string;
  pincode: string;
  parents?: { father_name?: string; father_phone?: string; mother_name?: string; mother_phone?: string };
  previous_education?: { ssc_percentage?: string; hsc_percentage?: string };
  abc_id?: string;
  hostel_resident: boolean;
  mentor_name?: string;
}

const TABS = [
  { key: "personal", label: "Personal", icon: User },
  { key: "academic", label: "Academic", icon: BookOpen },
  { key: "family", label: "Family", icon: Users },
  { key: "documents", label: "Documents", icon: FileText },
  { key: "fees", label: "Fees", icon: DollarSign },
  { key: "attendance", label: "Attendance", icon: BarChart2 },
  { key: "certificates", label: "Certificates", icon: Award },
];

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  detained: "bg-red-100 text-red-700",
  suspended: "bg-orange-100 text-orange-700",
  passout: "bg-blue-100 text-blue-700",
  alumni: "bg-purple-100 text-purple-700",
};

function InfoRow({ label, value }: { label: string; value?: string | number | boolean | null }) {
  return (
    <div className="flex flex-col gap-0.5 py-2 border-b border-border last:border-0">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm font-medium text-foreground">{value != null && value !== "" ? String(value) : "—"}</span>
    </div>
  );
}

export default function StudentProfilePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [student, setStudent] = useState<StudentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("personal");
  const [semRecords, setSemRecords] = useState<unknown[]>([]);
  const [documents, setDocuments] = useState<unknown[]>([]);

  useEffect(() => {
    if (!id) return;
    api.get<StudentDetail>(`/students/${id}/`)
      .then((r) => setStudent(r.data))
      .catch(() => setStudent(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!id || activeTab !== "academic") return;
    api.get<{ results: unknown[] }>(`/students/${id}/semester-records/`)
      .then((r) => setSemRecords(r.data.results ?? []))
      .catch(() => setSemRecords([]));
  }, [id, activeTab]);

  useEffect(() => {
    if (!id || activeTab !== "documents") return;
    api.get<{ results: unknown[] }>(`/students/${id}/documents/`)
      .then((r) => setDocuments(r.data.results ?? []))
      .catch(() => setDocuments([]));
  }, [id, activeTab]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
      </div>
    );
  }

  if (!student) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-muted-foreground">
        <p>Student not found.</p>
        <button onClick={() => router.back()} className="text-accent underline text-sm">Go back</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back + Header */}
      <div className="flex items-start gap-4">
        <button onClick={() => router.back()} className="mt-1 rounded-lg border border-border p-2 hover:bg-muted">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-accent/20 flex items-center justify-center text-accent font-bold text-lg">
              {student.full_name?.charAt(0) ?? "S"}
            </div>
            <div>
              <h1 className="font-display text-xl font-bold text-primary">{student.full_name}</h1>
              <p className="text-sm text-muted-foreground font-mono">{student.enrollment_number}</p>
            </div>
            <span className={`ml-auto rounded-full px-3 py-1 text-xs font-medium capitalize ${STATUS_COLORS[student.student_status] ?? "bg-gray-100 text-gray-600"}`}>
              {student.student_status?.replace(/_/g, " ")}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto rounded-xl border border-border bg-surface p-1">
        {TABS.map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === t.key
                  ? "bg-accent text-white"
                  : "text-muted-foreground hover:bg-muted"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="rounded-xl border border-border bg-surface p-6 shadow-card">
        {activeTab === "personal" && (
          <div className="grid gap-x-8 gap-y-0 sm:grid-cols-2 lg:grid-cols-3">
            <InfoRow label="Full Name" value={student.full_name} />
            <InfoRow label="Enrollment Number" value={student.enrollment_number} />
            <InfoRow label="Roll Number" value={student.roll_number} />
            <InfoRow label="Email" value={student.email} />
            <InfoRow label="Phone" value={student.phone} />
            <InfoRow label="Gender" value={student.gender} />
            <InfoRow label="Date of Birth" value={student.date_of_birth} />
            <InfoRow label="Blood Group" value={student.blood_group} />
            <InfoRow label="Category" value={student.category?.toUpperCase()} />
            <InfoRow label="Nationality" value={student.nationality} />
            <InfoRow label="Address" value={student.address} />
            <InfoRow label="City" value={student.city} />
            <InfoRow label="State" value={student.state} />
            <InfoRow label="Pincode" value={student.pincode} />
            <InfoRow label="ABC ID" value={student.abc_id} />
            <InfoRow label="Hostel Resident" value={student.hostel_resident ? "Yes" : "No"} />
            <InfoRow label="Mentor" value={student.mentor_name} />
          </div>
        )}

        {activeTab === "academic" && (
          <div className="space-y-4">
            <div className="grid gap-x-8 sm:grid-cols-2 lg:grid-cols-3">
              <InfoRow label="Department" value={student.department_name} />
              <InfoRow label="Semester" value={student.semester} />
              <InfoRow label="Batch Year" value={student.batch_year} />
              <InfoRow label="Status" value={student.student_status?.replace(/_/g, " ")} />
            </div>
            <h3 className="mt-4 font-semibold text-foreground">Semester Records</h3>
            {semRecords.length === 0 ? (
              <p className="text-sm text-muted-foreground">No semester records found.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b border-border">
                    <tr>
                      <th className="py-2 text-left text-muted-foreground">Semester</th>
                      <th className="py-2 text-left text-muted-foreground">SGPA</th>
                      <th className="py-2 text-left text-muted-foreground">CGPA</th>
                      <th className="py-2 text-left text-muted-foreground">Attendance</th>
                      <th className="py-2 text-left text-muted-foreground">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {(semRecords as Record<string, unknown>[]).map((r, i) => (
                      <tr key={i}>
                        <td className="py-2">{String(r.semester_number ?? r.semester ?? "—")}</td>
                        <td className="py-2">{String(r.sgpa ?? "—")}</td>
                        <td className="py-2">{String(r.cgpa ?? "—")}</td>
                        <td className="py-2">{r.attendance_percentage ? `${String(r.attendance_percentage)}%` : "—"}</td>
                        <td className="py-2 capitalize">{String(r.status ?? "—")}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === "family" && (
          <div className="grid gap-x-8 sm:grid-cols-2">
            <div>
              <h3 className="mb-3 font-semibold text-foreground">Father</h3>
              <InfoRow label="Name" value={student.parents?.father_name} />
              <InfoRow label="Phone" value={student.parents?.father_phone} />
            </div>
            <div>
              <h3 className="mb-3 font-semibold text-foreground">Mother</h3>
              <InfoRow label="Name" value={student.parents?.mother_name} />
              <InfoRow label="Phone" value={student.parents?.mother_phone} />
            </div>
          </div>
        )}

        {activeTab === "documents" && (
          <div className="space-y-3">
            {documents.length === 0 ? (
              <p className="text-sm text-muted-foreground">No documents uploaded yet.</p>
            ) : (
              (documents as Record<string, unknown>[]).map((d, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border border-border p-3">
                  <div>
                    <p className="text-sm font-medium capitalize">{String(d.document_type ?? "").replace(/_/g, " ")}</p>
                    <p className="text-xs text-muted-foreground capitalize">{String(d.status ?? "pending")}</p>
                  </div>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    d.status === "verified" ? "bg-green-100 text-green-700" :
                    d.status === "rejected" ? "bg-red-100 text-red-700" :
                    "bg-yellow-100 text-yellow-700"
                  }`}>
                    {String(d.status ?? "pending")}
                  </span>
                </div>
              ))
            )}
          </div>
        )}

        {(activeTab === "fees" || activeTab === "attendance" || activeTab === "certificates") && (
          <div className="flex min-h-[20vh] items-center justify-center text-muted-foreground text-sm">
            This section will be available in the next module.
          </div>
        )}
      </div>
    </div>
  );
}
