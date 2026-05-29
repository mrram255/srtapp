"use client";

import { FormEvent, useState } from "react";

export default function PublicApplyPage() {
  const [submitted, setSubmitted] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(e.currentTarget);
    const body = Object.fromEntries(form.entries());
    try {
      const res = await fetch("/django-api/admissions/apply/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.message || "Submit failed");
      setSubmitted(json.data?.application_number ?? "Submitted");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit");
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="mx-auto max-w-lg p-8 text-center">
        <h1 className="text-2xl font-bold text-green-700">Application submitted</h1>
        <p className="mt-2 text-muted-foreground">Your application number: <strong>{submitted}</strong></p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg space-y-6 p-8">
      <h1 className="text-2xl font-bold">Apply for admission</h1>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <input name="college" placeholder="College UUID" required className="w-full rounded border px-3 py-2 text-sm" />
        <div className="grid grid-cols-2 gap-3">
          <input name="first_name" placeholder="First name" required className="rounded border px-3 py-2 text-sm" />
          <input name="last_name" placeholder="Last name" required className="rounded border px-3 py-2 text-sm" />
        </div>
        <input name="email" type="email" placeholder="Email" required className="w-full rounded border px-3 py-2 text-sm" />
        <input name="phone" placeholder="Phone" required className="w-full rounded border px-3 py-2 text-sm" />
        <input name="date_of_birth" type="date" required className="w-full rounded border px-3 py-2 text-sm" />
        <select name="gender" required className="w-full rounded border px-3 py-2 text-sm">
          <option value="MALE">Male</option>
          <option value="FEMALE">Female</option>
          <option value="OTHER">Other</option>
        </select>
        <input name="department" placeholder="Department UUID" required className="w-full rounded border px-3 py-2 text-sm" />
        <input name="branch" placeholder="Branch UUID" required className="w-full rounded border px-3 py-2 text-sm" />
        <input name="previous_school" placeholder="Previous school" required className="w-full rounded border px-3 py-2 text-sm" />
        <input name="previous_percentage" placeholder="Previous %" required className="w-full rounded border px-3 py-2 text-sm" />
        <button type="submit" disabled={loading} className="w-full rounded-lg bg-accent py-2 text-white disabled:opacity-50">
          {loading ? "Submitting…" : "Submit application"}
        </button>
      </form>
    </div>
  );
}
