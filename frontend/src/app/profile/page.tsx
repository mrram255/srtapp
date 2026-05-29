"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import api from "@/lib/api/client";

interface ProfileData {
  id: string;
  email: string;
  phone: string;
  role: string;
  first_name: string;
  last_name: string;
  full_name: string;
  profile_photo: string;
  college_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

const ROLE_LABEL: Record<string, string> = {
  SUPER_ADMIN: "Super Admin",
  ADMIN: "Admin",
  HOD: "Head of Department",
  TEACHER: "Teacher",
  STUDENT: "Student",
  PARENT: "Parent",
  ACCOUNTANT: "Accountant",
  LIBRARIAN: "Librarian",
  SECURITY: "Security",
};

const ROLE_COLOR: Record<string, string> = {
  SUPER_ADMIN: "bg-red-100 text-red-700",
  ADMIN: "bg-purple-100 text-purple-700",
  HOD: "bg-indigo-100 text-indigo-700",
  TEACHER: "bg-blue-100 text-blue-700",
  STUDENT: "bg-green-100 text-green-700",
  PARENT: "bg-yellow-100 text-yellow-700",
  ACCOUNTANT: "bg-orange-100 text-orange-700",
  LIBRARIAN: "bg-teal-100 text-teal-700",
  SECURITY: "bg-gray-100 text-gray-700",
};

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", phone: "" });
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        const res = await api.get("/accounts/profile/").then((r) => r.data);
        setProfile(res.data);
        setForm({
          first_name: res.data.first_name,
          last_name: res.data.last_name,
          phone: res.data.phone,
        });
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load profile.");
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      await api.patch("/accounts/profile/", form);
      setProfile((prev) => prev ? { ...prev, ...form, full_name: `${form.first_name} ${form.last_name}` } : prev);
      setEditing(false);
      setSuccess("Profile updated successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch {
      setError("Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
      </div>
    );
  }

  if (error && !profile) {
    return (
      <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700">
        ⚠️ {error}
      </div>
    );
  }

  if (!profile) return null;

  const initials = `${profile.first_name[0] ?? ""}${profile.last_name[0] ?? ""}`.toUpperCase();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Header Card */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-2xl bg-white/20 flex items-center justify-center text-3xl font-bold">
              {profile.profile_photo ? (
                <Image src={profile.profile_photo} alt="Photo" width={200} height={200} className="w-full h-full object-cover rounded-2xl" />
              ) : initials}
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold">{profile.full_name}</h1>
              <p className="text-blue-200 text-sm mt-0.5">{profile.email}</p>
              <div className="flex items-center gap-2 mt-2">
                <span className={`text-xs font-semibold px-3 py-1 rounded-full bg-white/20`}>
                  {ROLE_LABEL[profile.role] ?? profile.role}
                </span>
                {profile.is_verified && (
                  <span className="text-xs font-semibold px-3 py-1 rounded-full bg-green-400/30">
                    ✓ Verified
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm font-medium">
            ✅ {success}
          </div>
        )}

        {/* Profile Details */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-gray-900">Personal Information</h2>
            {!editing ? (
              <button
                onClick={() => setEditing(true)}
                className="px-4 py-2 bg-blue-50 text-blue-600 text-sm font-medium rounded-lg hover:bg-blue-100 transition-colors"
              >
                ✏️ Edit
              </button>
            ) : (
              <div className="flex gap-2">
                <button
                  onClick={() => setEditing(false)}
                  className="px-4 py-2 bg-gray-100 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {saving ? "Saving..." : "Save"}
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field
              label="First Name"
              value={form.first_name}
              editing={editing}
              onChange={(v) => setForm((f) => ({ ...f, first_name: v }))}
            />
            <Field
              label="Last Name"
              value={form.last_name}
              editing={editing}
              onChange={(v) => setForm((f) => ({ ...f, last_name: v }))}
            />
            <Field
              label="Phone"
              value={form.phone}
              editing={editing}
              onChange={(v) => setForm((f) => ({ ...f, phone: v }))}
            />
            <Field label="Email" value={profile.email} editing={false} onChange={() => {}} />
            <Field label="College" value={profile.college_name} editing={false} onChange={() => {}} />
            <Field label="Role" value={ROLE_LABEL[profile.role] ?? profile.role} editing={false} onChange={() => {}} />
            <Field
              label="Member Since"
              value={new Date(profile.created_at).toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" })}
              editing={false}
              onChange={() => {}}
            />
            <Field label="Status" value={profile.is_active ? "Active" : "Inactive"} editing={false} onChange={() => {}} />
          </div>
        </div>

        {/* Account Security */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Security</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-medium text-gray-700">Password</p>
                <p className="text-xs text-gray-400">Last changed recently</p>
              </div>
              <button className="text-sm text-blue-600 font-medium hover:underline">
                Change
              </button>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-medium text-gray-700">Two-Factor Authentication</p>
                <p className="text-xs text-gray-400">Add extra security to your account</p>
              </div>
              <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gray-200 text-gray-600">
                Off
              </span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

function Field({
  label, value, editing, onChange,
}: {
  label: string;
  value: string;
  editing: boolean;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <p className="text-xs text-gray-400 uppercase tracking-wide font-medium mb-1">{label}</p>
      {editing ? (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      ) : (
        <p className="text-sm font-semibold text-gray-800">{value || "—"}</p>
      )}
    </div>
  );
}
