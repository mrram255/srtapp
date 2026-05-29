"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import api from "@/lib/api/client";

type Department = { id: string; name: string; code: string };
type Branch = { id: string; name: string; code: string };

const STEPS = ["Account", "Academic", "Personal", "Family & Education", "Review"] as const;

const emptyForm = {
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  phone: "",
  enrollment_number: "",
  roll_number: "",
  department: "",
  branch: "",
  semester: "1",
  batch_year: String(new Date().getFullYear()),
  date_of_birth: "",
  gender: "MALE",
  category: "",
  abc_id: "",
  address: "",
  city: "",
  state: "",
  pincode: "",
  emergency_contact: "",
  emergency_contact_name: "",
  admission_date: "",
  admission_type: "REGULAR",
  father_name: "",
  mother_name: "",
  guardian_phone: "",
  ssc_percentage: "",
  hsc_percentage: "",
};

export default function RegistrarStudentNewPage() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState(emptyForm);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .get<{ results?: Department[]; data?: Department[] }>("/departments/?limit=100")
      .then((r) => setDepartments(r.data.results ?? r.data.data ?? []))
      .catch(() => setDepartments([]));
  }, []);

  useEffect(() => {
    if (!form.department) {
      setBranches([]);
      return;
    }
    api
      .get<{ results?: Branch[]; data?: Branch[] }>(`/branches/?department=${form.department}&limit=50`)
      .then((r) => setBranches(r.data.results ?? r.data.data ?? []))
      .catch(() => setBranches([]));
  }, [form.department]);

  const set = useCallback((key: keyof typeof emptyForm, value: string) => {
    setForm((f) => ({ ...f, [key]: value }));
  }, []);

  const canNext = () => {
    if (step === 0) {
      return form.email && form.password.length >= 12 && form.first_name && form.last_name && form.phone;
    }
    if (step === 1) {
      return form.department && form.branch && form.enrollment_number && form.roll_number;
    }
    if (step === 2) {
      return (
        form.date_of_birth &&
        form.address &&
        form.city &&
        form.state &&
        form.pincode &&
        form.emergency_contact &&
        form.emergency_contact_name &&
        form.admission_date
      );
    }
    return true;
  };

  const submit = async () => {
    setSubmitting(true);
    setError("");
    try {
      const payload = {
        email: form.email,
        password: form.password,
        first_name: form.first_name,
        last_name: form.last_name,
        phone: form.phone,
        enrollment_number: form.enrollment_number,
        roll_number: form.roll_number,
        department: form.department,
        branch: form.branch,
        semester: Number(form.semester),
        batch_year: Number(form.batch_year),
        date_of_birth: form.date_of_birth,
        gender: form.gender,
        category: form.category,
        abc_id: form.abc_id,
        address: form.address,
        city: form.city,
        state: form.state,
        pincode: form.pincode,
        emergency_contact: form.emergency_contact,
        emergency_contact_name: form.emergency_contact_name,
        admission_date: form.admission_date,
        admission_type: form.admission_type,
        family_details: {
          father_name: form.father_name,
          mother_name: form.mother_name,
          guardian_phone: form.guardian_phone,
        },
        education_details: {
          ssc_percentage: form.ssc_percentage ? Number(form.ssc_percentage) : null,
          hsc_percentage: form.hsc_percentage ? Number(form.hsc_percentage) : null,
        },
      };
      await api.post("/students/", payload);
      window.location.href = "/registrar/students";
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? JSON.stringify((err as { response?: { data?: unknown } }).response?.data)
          : "Failed to create student";
      setError(String(msg));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Link href="/registrar/students" className="text-sm text-muted-foreground hover:text-primary">
          <ChevronLeft className="inline h-4 w-4" /> Back
        </Link>
        <h1 className="font-display text-2xl font-bold text-primary">New student admission</h1>
      </div>

      <ol className="flex flex-wrap gap-2 text-xs">
        {STEPS.map((label, i) => (
          <li
            key={label}
            className={`rounded-full px-3 py-1 ${i === step ? "bg-accent text-white" : i < step ? "bg-green-100 text-green-800" : "bg-muted text-muted-foreground"}`}
          >
            {i + 1}. {label}
          </li>
        ))}
      </ol>

      {error ? <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</p> : null}

      <div className="rounded-xl border border-border bg-surface p-6 shadow-sm">
        {step === 0 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Email" value={form.email} onChange={(v) => set("email", v)} type="email" />
            <Field label="Password (min 12)" value={form.password} onChange={(v) => set("password", v)} type="password" />
            <Field label="First name" value={form.first_name} onChange={(v) => set("first_name", v)} />
            <Field label="Last name" value={form.last_name} onChange={(v) => set("last_name", v)} />
            <Field label="Phone" value={form.phone} onChange={(v) => set("phone", v)} />
          </div>
        ) : null}

        {step === 1 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm">
              <span className="text-muted-foreground">Department</span>
              <select
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2"
                value={form.department}
                onChange={(e) => set("department", e.target.value)}
              >
                <option value="">Select</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-sm">
              <span className="text-muted-foreground">Branch</span>
              <select
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2"
                value={form.branch}
                onChange={(e) => set("branch", e.target.value)}
              >
                <option value="">Select</option>
                {branches.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </label>
            <Field label="Enrollment no." value={form.enrollment_number} onChange={(v) => set("enrollment_number", v)} />
            <Field label="Roll no." value={form.roll_number} onChange={(v) => set("roll_number", v)} />
            <Field label="Semester" value={form.semester} onChange={(v) => set("semester", v)} />
            <Field label="Batch year" value={form.batch_year} onChange={(v) => set("batch_year", v)} />
          </div>
        ) : null}

        {step === 2 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Date of birth" value={form.date_of_birth} onChange={(v) => set("date_of_birth", v)} type="date" />
            <label className="block text-sm">
              <span className="text-muted-foreground">Gender</span>
              <select
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2"
                value={form.gender}
                onChange={(e) => set("gender", e.target.value)}
              >
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </label>
            <Field label="Category" value={form.category} onChange={(v) => set("category", v)} />
            <Field label="ABC ID" value={form.abc_id} onChange={(v) => set("abc_id", v)} />
            <Field label="Address" value={form.address} onChange={(v) => set("address", v)} className="sm:col-span-2" />
            <Field label="City" value={form.city} onChange={(v) => set("city", v)} />
            <Field label="State" value={form.state} onChange={(v) => set("state", v)} />
            <Field label="Pincode" value={form.pincode} onChange={(v) => set("pincode", v)} />
            <Field label="Emergency contact" value={form.emergency_contact} onChange={(v) => set("emergency_contact", v)} />
            <Field label="Emergency name" value={form.emergency_contact_name} onChange={(v) => set("emergency_contact_name", v)} />
            <Field label="Admission date" value={form.admission_date} onChange={(v) => set("admission_date", v)} type="date" />
          </div>
        ) : null}

        {step === 3 ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Father name" value={form.father_name} onChange={(v) => set("father_name", v)} />
            <Field label="Mother name" value={form.mother_name} onChange={(v) => set("mother_name", v)} />
            <Field label="Guardian phone" value={form.guardian_phone} onChange={(v) => set("guardian_phone", v)} />
            <Field label="SSC %" value={form.ssc_percentage} onChange={(v) => set("ssc_percentage", v)} />
            <Field label="HSC %" value={form.hsc_percentage} onChange={(v) => set("hsc_percentage", v)} />
          </div>
        ) : null}

        {step === 4 ? (
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <Item k="Name" v={`${form.first_name} ${form.last_name}`} />
            <Item k="Email" v={form.email} />
            <Item k="Enrollment" v={form.enrollment_number} />
            <Item k="ABC ID" v={form.abc_id || "—"} />
            <Item k="Father" v={form.father_name || "—"} />
            <Item k="SSC %" v={form.ssc_percentage || "—"} />
          </dl>
        ) : null}
      </div>

      <div className="flex justify-between">
        <button
          type="button"
          disabled={step === 0}
          onClick={() => setStep((s) => s - 1)}
          className="flex items-center gap-1 rounded-lg border px-4 py-2 text-sm disabled:opacity-40"
        >
          <ChevronLeft className="h-4 w-4" /> Previous
        </button>
        {step < STEPS.length - 1 ? (
          <button
            type="button"
            disabled={!canNext()}
            onClick={() => setStep((s) => s + 1)}
            className="flex items-center gap-1 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            Next <ChevronRight className="h-4 w-4" />
          </button>
        ) : (
          <button
            type="button"
            disabled={submitting}
            onClick={() => void submit()}
            className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            {submitting ? "Saving…" : "Submit admission"}
          </button>
        )}
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  className = "",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  className?: string;
}) {
  return (
    <label className={`block text-sm ${className}`}>
      <span className="text-muted-foreground">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent"
      />
    </label>
  );
}

function Item({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-muted-foreground">{k}</dt>
      <dd className="font-medium">{v}</dd>
    </div>
  );
}
