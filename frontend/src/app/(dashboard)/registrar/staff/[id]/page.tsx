"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, User, Briefcase, GraduationCap, BookOpen, DollarSign } from "lucide-react";
import api from "@/lib/api/client";

interface StaffDetail {
  id: string;
  employee_id: string;
  full_name: string;
  email: string;
  phone: string;
  gender: string;
  date_of_birth: string;
  department_name: string;
  designation_name: string;
  staff_type: string;
  status: string;
  date_of_joining: string;
  appointment_type: string;
  highest_qualification: string;
  specialization: string;
  phd_status: string;
  net_set_qualified: boolean;
  total_experience_years: number;
  teaching_experience_years: number;
  google_scholar_id: string;
  orcid_id: string;
  pay_band: string;
  basic_pay: number;
  bank_name: string;
}

interface ServiceEntry {
  id: string;
  entry_type: string;
  effective_date: string;
  order_number: string;
  description: string;
  old_designation?: string;
  new_designation?: string;
}

const TABS = [
  { key: "personal", label: "Personal", icon: User },
  { key: "employment", label: "Employment", icon: Briefcase },
  { key: "qualification", label: "Qualification", icon: GraduationCap },
  { key: "service_book", label: "Service Book", icon: BookOpen },
  { key: "salary", label: "Salary", icon: DollarSign },
];

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  on_leave: "bg-yellow-100 text-yellow-700",
  deputation: "bg-blue-100 text-blue-700",
  resigned: "bg-gray-100 text-gray-600",
  retired: "bg-purple-100 text-purple-700",
  terminated: "bg-red-100 text-red-700",
};

function InfoRow({ label, value }: { label: string; value?: string | number | boolean | null }) {
  return (
    <div className="flex flex-col gap-0.5 py-2 border-b border-border last:border-0">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm font-medium text-foreground">{value != null && value !== "" ? String(value) : "—"}</span>
    </div>
  );
}

export default function StaffProfilePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [staff, setStaff] = useState<StaffDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("personal");
  const [serviceBook, setServiceBook] = useState<ServiceEntry[]>([]);

  useEffect(() => {
    if (!id) return;
    api.get<StaffDetail>(`/staff/${id}/`)
      .then((r) => setStaff(r.data))
      .catch(() => setStaff(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!id || activeTab !== "service_book") return;
    api.get<{ results: ServiceEntry[] }>(`/staff/${id}/service-book/`)
      .then((r) => setServiceBook(r.data.results ?? []))
      .catch(() => setServiceBook([]));
  }, [id, activeTab]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-accent" />
      </div>
    );
  }

  if (!staff) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-muted-foreground">
        <p>Staff member not found.</p>
        <button onClick={() => router.back()} className="text-accent underline text-sm">Go back</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <button onClick={() => router.back()} className="mt-1 rounded-lg border border-border p-2 hover:bg-muted">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-lg">
              {staff.full_name?.charAt(0) ?? "S"}
            </div>
            <div>
              <h1 className="font-display text-xl font-bold text-primary">{staff.full_name}</h1>
              <p className="text-sm text-muted-foreground">{staff.designation_name} · <span className="font-mono">{staff.employee_id}</span></p>
            </div>
            <span className={`ml-auto rounded-full px-3 py-1 text-xs font-medium capitalize ${STATUS_COLORS[staff.status] ?? "bg-gray-100 text-gray-600"}`}>
              {staff.status?.replace(/_/g, " ")}
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
                activeTab === t.key ? "bg-accent text-white" : "text-muted-foreground hover:bg-muted"
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
          <div className="grid gap-x-8 sm:grid-cols-2 lg:grid-cols-3">
            <InfoRow label="Full Name" value={staff.full_name} />
            <InfoRow label="Email" value={staff.email} />
            <InfoRow label="Phone" value={staff.phone} />
            <InfoRow label="Gender" value={staff.gender} />
            <InfoRow label="Date of Birth" value={staff.date_of_birth} />
            <InfoRow label="Department" value={staff.department_name} />
          </div>
        )}

        {activeTab === "employment" && (
          <div className="grid gap-x-8 sm:grid-cols-2 lg:grid-cols-3">
            <InfoRow label="Employee ID" value={staff.employee_id} />
            <InfoRow label="Designation" value={staff.designation_name} />
            <InfoRow label="Staff Type" value={staff.staff_type?.replace(/_/g, " ")} />
            <InfoRow label="Appointment Type" value={staff.appointment_type?.replace(/_/g, " ")} />
            <InfoRow label="Date of Joining" value={staff.date_of_joining} />
            <InfoRow label="Status" value={staff.status?.replace(/_/g, " ")} />
          </div>
        )}

        {activeTab === "qualification" && (
          <div className="grid gap-x-8 sm:grid-cols-2 lg:grid-cols-3">
            <InfoRow label="Highest Qualification" value={staff.highest_qualification?.toUpperCase()} />
            <InfoRow label="Specialization" value={staff.specialization} />
            <InfoRow label="PhD Status" value={staff.phd_status?.replace(/_/g, " ")} />
            <InfoRow label="NET/SET Qualified" value={staff.net_set_qualified ? "Yes" : "No"} />
            <InfoRow label="Total Experience (yrs)" value={staff.total_experience_years} />
            <InfoRow label="Teaching Experience (yrs)" value={staff.teaching_experience_years} />
            <InfoRow label="Google Scholar ID" value={staff.google_scholar_id} />
            <InfoRow label="ORCID ID" value={staff.orcid_id} />
          </div>
        )}

        {activeTab === "service_book" && (
          <div className="space-y-4">
            {serviceBook.length === 0 ? (
              <p className="text-sm text-muted-foreground">No service book entries found.</p>
            ) : (
              <div className="relative">
                <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />
                <div className="space-y-4">
                  {serviceBook.map((entry) => (
                    <div key={entry.id} className="relative pl-10">
                      <div className="absolute left-3 top-1.5 h-3 w-3 rounded-full border-2 border-accent bg-surface" />
                      <div className="rounded-lg border border-border p-4">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="rounded-full bg-accent/10 px-2 py-0.5 text-xs font-medium text-accent capitalize">
                            {entry.entry_type?.replace(/_/g, " ")}
                          </span>
                          <span className="text-xs text-muted-foreground">{entry.effective_date}</span>
                        </div>
                        <p className="mt-2 text-sm text-foreground">{entry.description}</p>
                        {entry.order_number && (
                          <p className="mt-1 text-xs text-muted-foreground">Order: {entry.order_number}</p>
                        )}
                        {(entry.old_designation || entry.new_designation) && (
                          <p className="mt-1 text-xs text-muted-foreground">
                            {entry.old_designation} → {entry.new_designation}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "salary" && (
          <div className="grid gap-x-8 sm:grid-cols-2 lg:grid-cols-3">
            <InfoRow label="Pay Band" value={staff.pay_band} />
            <InfoRow label="Basic Pay" value={staff.basic_pay ? `₹${staff.basic_pay}` : null} />
            <InfoRow label="Bank Name" value={staff.bank_name} />
          </div>
        )}
      </div>
    </div>
  );
}
