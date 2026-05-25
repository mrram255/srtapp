"use client";

import { useCallback, useEffect, useState } from "react";

import { api, getApiErrorMessage, type ApiEnvelope } from "@/lib/api";

type Institution = {
  id: string;
  name: string;
  code: string;
  short_name?: string;
  institution_type: string;
  city?: string;
  state?: string;
  email?: string;
  phone?: string;
  website_url?: string;
  affiliation_university?: string;
};

type Settings = {
  id: string;
  attendance_minimum_percentage: string;
  grading_system: string;
  result_display_mode: string;
  timezone: string;
  enrollment_number_format: string;
  sms_enabled: boolean;
  email_enabled: boolean;
};

const TABS = ["Basic Info", "Contact", "Settings"] as const;

export default function InstitutionPage() {
  const [tab, setTab] = useState<(typeof TABS)[number]>("Basic Info");
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [selected, setSelected] = useState<Institution | null>(null);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const instRes = await api.get<ApiEnvelope<Institution[]>>("/institutions/?limit=10");
      const rows = instRes.data.data ?? [];
      setInstitutions(rows);
      const first = rows[0] ?? null;
      setSelected(first);
      if (first) {
        const detail = await api.get<ApiEnvelope<Institution>>(`/institutions/${first.id}/`);
        setSelected(detail.data.data ?? first);
      }
      try {
        const settingsRes = await api.get<ApiEnvelope<Settings>>("/institutions/settings/");
        setSettings(settingsRes.data.data ?? null);
      } catch {
        setSettings(null);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to load institution."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const saveInstitution = async () => {
    if (!selected) return;
    setSaving(true);
    setMessage("");
    setError("");
    try {
      await api.patch(`/institutions/${selected.id}/`, selected);
      setMessage("Institution saved.");
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to save institution."));
    } finally {
      setSaving(false);
    }
  };

  const saveSettings = async () => {
    if (!settings) return;
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const res = await api.patch<ApiEnvelope<Settings>>("/institutions/settings/", settings);
      setSettings(res.data.data ?? settings);
      setMessage("Settings saved.");
    } catch (err) {
      setError(getApiErrorMessage(err, "Failed to save settings."));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="p-6 text-sm text-gray-500">Loading institution configuration…</div>;
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Institution Setup</h1>
        <p className="text-sm text-gray-500">College profile, contact, and system settings (Super Admin)</p>
      </div>

      {error ? <p className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</p> : null}
      {message ? <p className="rounded-lg bg-green-50 px-4 py-2 text-sm text-green-700">{message}</p> : null}

      <div className="flex flex-wrap gap-2 border-b border-gray-100 pb-2">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${tab === t ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-700"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {!selected && institutions.length === 0 ? (
        <p className="text-sm text-gray-500">No institution configured yet. Create one via API or admin.</p>
      ) : null}

      {selected && tab === "Basic Info" ? (
        <div className="grid max-w-3xl gap-4 rounded-xl border bg-white p-6 shadow-sm">
          <label className="text-sm">
            Name
            <input
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={selected.name}
              onChange={(e) => setSelected({ ...selected, name: e.target.value })}
            />
          </label>
          <label className="text-sm">
            Code
            <input
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={selected.code}
              onChange={(e) => setSelected({ ...selected, code: e.target.value })}
            />
          </label>
          <label className="text-sm">
            Type
            <select
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={selected.institution_type}
              onChange={(e) => setSelected({ ...selected, institution_type: e.target.value })}
            >
              <option value="affiliated">Affiliated</option>
              <option value="autonomous">Autonomous</option>
              <option value="university">University</option>
              <option value="deemed">Deemed</option>
            </select>
          </label>
          <label className="text-sm">
            Affiliation University
            <input
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={selected.affiliation_university ?? ""}
              onChange={(e) => setSelected({ ...selected, affiliation_university: e.target.value })}
            />
          </label>
          <button
            type="button"
            disabled={saving}
            onClick={() => void saveInstitution()}
            className="w-fit rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save Basic Info"}
          </button>
        </div>
      ) : null}

      {selected && tab === "Contact" ? (
        <div className="grid max-w-3xl gap-4 rounded-xl border bg-white p-6 shadow-sm">
          {(["email", "phone", "website_url", "city", "state"] as const).map((field) => (
            <label key={field} className="text-sm capitalize">
              {field.replace("_", " ")}
              <input
                className="mt-1 w-full rounded-lg border px-3 py-2"
                value={(selected[field] as string) ?? ""}
                onChange={(e) => setSelected({ ...selected, [field]: e.target.value })}
              />
            </label>
          ))}
          <button
            type="button"
            disabled={saving}
            onClick={() => void saveInstitution()}
            className="w-fit rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
          >
            Save Contact
          </button>
        </div>
      ) : null}

      {tab === "Settings" && settings ? (
        <div className="grid max-w-3xl gap-4 rounded-xl border bg-white p-6 shadow-sm">
          <label className="text-sm">
            Min attendance %
            <input
              type="number"
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={settings.attendance_minimum_percentage}
              onChange={(e) =>
                setSettings({ ...settings, attendance_minimum_percentage: e.target.value })
              }
            />
          </label>
          <label className="text-sm">
            Grading system
            <select
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={settings.grading_system}
              onChange={(e) => setSettings({ ...settings, grading_system: e.target.value })}
            >
              <option value="CGPA_10">CGPA 10</option>
              <option value="CGPA_4">CGPA 4</option>
              <option value="percentage">Percentage</option>
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={settings.sms_enabled}
              onChange={(e) => setSettings({ ...settings, sms_enabled: e.target.checked })}
            />
            SMS enabled
          </label>
          <button
            type="button"
            disabled={saving}
            onClick={() => void saveSettings()}
            className="w-fit rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white"
          >
            Save Settings
          </button>
        </div>
      ) : null}

      {tab === "Settings" && !settings ? (
        <p className="text-sm text-gray-500">No settings record yet. Create an institution first.</p>
      ) : null}
    </div>
  );
}
