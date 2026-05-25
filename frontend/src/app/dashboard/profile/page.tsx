"use client";

import { useEffect, useRef, useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import { Camera, Upload, Loader2 } from "lucide-react";
import api from "@/lib/api/client";

interface ProfileData {
  id: string; email: string; phone: string; role: string;
  first_name: string; last_name: string; full_name: string;
  profile_photo: string; signature: string;
  college_name: string; is_active: boolean; is_verified: boolean; created_at: string;
}

const ROLE_LABEL: Record<string, string> = {
  SUPER_ADMIN: "Super Admin", ADMIN: "Admin", HOD: "Head of Department",
  TEACHER: "Teacher", STUDENT: "Student", PARENT: "Parent",
  ACCOUNTANT: "Accountant", LIBRARIAN: "Librarian", SECURITY: "Security",
};

export default function ProfilePage() {
  const user        = useAuthStore((s) => s.user);
  const photoCamRef = useRef<HTMLInputElement>(null);
  const photoFileRef= useRef<HTMLInputElement>(null);
  const signCamRef  = useRef<HTMLInputElement>(null);
  const signFileRef = useRef<HTMLInputElement>(null);

  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState("");
  const [editing, setEditing] = useState(false);
  const [saving,  setSaving]  = useState(false);
  const [success, setSuccess] = useState("");
  const [form, setForm]       = useState({ first_name: "", last_name: "", phone: "" });
  const [photoUploading, setPhotoUploading] = useState(false);
  const [signUploading,  setSignUploading]  = useState(false);
  const [uploadError,    setUploadError]    = useState("");
  const [showPwdModal,   setShowPwdModal]   = useState(false);
  const [pwdForm,        setPwdForm]        = useState({ old_password: "", new_password: "", confirm_password: "" });
  const [pwdLoading,     setPwdLoading]     = useState(false);
  const [pwdError,       setPwdError]       = useState("");
  const [pwdSuccess,     setPwdSuccess]     = useState("");

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const res = await api.get("/accounts/profile/").then((r) => r.data);
        setProfile(res.data);
        setForm({ first_name: res.data.first_name, last_name: res.data.last_name, phone: res.data.phone });
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Failed to load profile.");
      } finally { setLoading(false); }
    })();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      await api.patch("/accounts/profile/", form);
      setProfile((p) => p ? { ...p, ...form, full_name: `${form.first_name} ${form.last_name}` } : p);
      setEditing(false);
      setSuccess("Profile updated!");
      setTimeout(() => setSuccess(""), 3000);
    } catch { setError("Failed to update profile."); }
    finally   { setSaving(false); }
  };

  const validateFile = (file: File, maxKB: number): string | null => {
    if (!["image/jpeg","image/png","image/webp"].includes(file.type))
      return "Only JPEG, PNG, WebP allowed.";
    if (file.size > maxKB * 1024)
      return `File must be under ${maxKB}KB.`;
    return null;
  };

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadError("");
    const err = validateFile(file, 50);
    if (err) { setUploadError(err); return; }
    try {
      setPhotoUploading(true);
      const fd = new FormData();
      fd.append("avatar", file);
      const res = await api.post("/auth/avatar/upload/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      }).then((r) => r.data);
      setProfile((p) => p ? { ...p, profile_photo: res.data?.profile_photo ?? p.profile_photo } : p);
      setSuccess("Photo updated!");
      setTimeout(() => setSuccess(""), 3000);
    } catch { setUploadError("Photo upload failed. Try again."); }
    finally   { setPhotoUploading(false); }
  };

  const handleSignUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadError("");
    const err = validateFile(file, 50);
    if (err) { setUploadError(err); return; }
    try {
      setSignUploading(true);
      const fd = new FormData();
      fd.append("signature", file);
      const res = await api.post("/auth/signature/upload/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      }).then((r) => r.data);
      setProfile((p) => p ? { ...p, signature: res.data?.signature ?? p.signature } : p);
      setSuccess("Signature updated!");
      setTimeout(() => setSuccess(""), 3000);
    } catch { setUploadError("Signature upload failed. Try again."); }
    finally   { setSignUploading(false); }
  };

  const handleChangePassword = async () => {
    setPwdError(""); setPwdSuccess("");
    if (!pwdForm.old_password || !pwdForm.new_password || !pwdForm.confirm_password) {
      setPwdError("All fields are required."); return;
    }
    if (pwdForm.new_password !== pwdForm.confirm_password) {
      setPwdError("Passwords do not match."); return;
    }
    if (pwdForm.new_password.length < 12) {
      setPwdError("Password must be at least 12 characters."); return;
    }
    try {
      setPwdLoading(true);
      await api.post("/auth/password/change/", pwdForm);
      setPwdSuccess("Password changed successfully!");
      setPwdForm({ old_password: "", new_password: "", confirm_password: "" });
      setTimeout(() => { setShowPwdModal(false); setPwdSuccess(""); }, 2000);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to change password.";
      setPwdError(msg);
    } finally { setPwdLoading(false); }
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600" />
    </div>
  );
  if (error && !profile) return (
    <div className="m-6 p-5 bg-red-50 border border-red-200 rounded-xl text-red-700">⚠️ {error}</div>
  );
  if (!profile) return null;

  const initials  = `${profile.first_name[0] ?? ""}${profile.last_name[0] ?? ""}`.toUpperCase();
  const isStudent = profile.role === "STUDENT";

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* ── Header Card ── */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white">
          <div className="flex items-center gap-5">
            {/* Avatar */}
            <div className="relative shrink-0">
              <div className="w-20 h-20 rounded-2xl bg-white/20 flex items-center justify-center text-3xl font-bold overflow-hidden">
                {profile.profile_photo
                  ? <img src={profile.profile_photo} alt="Photo" className="w-full h-full object-cover" />
                  : initials}
              </div>
              {photoUploading && (
                <div className="absolute inset-0 rounded-2xl bg-black/40 flex items-center justify-center">
                  <Loader2 className="h-6 w-6 text-white animate-spin" />
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold">{profile.full_name}</h1>
              <p className="text-blue-200 text-sm mt-0.5">{profile.email}</p>
              <div className="flex items-center gap-2 mt-2 flex-wrap">
                <span className="text-xs font-semibold px-3 py-1 rounded-full bg-white/20">
                  {ROLE_LABEL[profile.role] ?? profile.role}
                </span>
                {profile.is_verified && (
                  <span className="text-xs font-semibold px-3 py-1 rounded-full bg-green-400/30">✓ Verified</span>
                )}
              </div>
              {/* Photo upload buttons */}
              <div className="flex gap-2 mt-3">
                <button onClick={() => photoCamRef.current?.click()} disabled={photoUploading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg text-xs font-medium transition-colors disabled:opacity-50">
                  <Camera className="h-3.5 w-3.5" /> Camera
                </button>
                <button onClick={() => photoFileRef.current?.click()} disabled={photoUploading}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg text-xs font-medium transition-colors disabled:opacity-50">
                  <Upload className="h-3.5 w-3.5" /> Upload
                </button>
              </div>
              <p className="text-xs text-blue-200 mt-1.5">Max 50KB · JPEG, PNG, WebP</p>
            </div>
          </div>
        </div>

        {/* Hidden inputs — photo */}
        <input ref={photoCamRef}  type="file" accept="image/*" capture="user"        className="hidden" onChange={handlePhotoUpload} />
        <input ref={photoFileRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={handlePhotoUpload} />

        {/* Success / Error */}
        {success && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm font-medium">✅ {success}</div>
        )}
        {uploadError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">⚠️ {uploadError}</div>
        )}

        {/* ── Personal Information ── */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-gray-900">Personal Information</h2>
            {!editing
              ? <button onClick={() => setEditing(true)} className="px-4 py-2 bg-blue-50 text-blue-600 text-sm font-medium rounded-lg hover:bg-blue-100 transition-colors">✏️ Edit</button>
              : <div className="flex gap-2">
                  <button onClick={() => setEditing(false)} className="px-4 py-2 bg-gray-100 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-200">Cancel</button>
                  <button onClick={handleSave} disabled={saving} className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50">
                    {saving ? "Saving..." : "Save"}
                  </button>
                </div>}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field label="First Name"    value={form.first_name}  editing={editing} onChange={(v) => setForm((f) => ({ ...f, first_name: v }))} />
            <Field label="Last Name"     value={form.last_name}   editing={editing} onChange={(v) => setForm((f) => ({ ...f, last_name: v }))} />
            <Field label="Phone"         value={form.phone}       editing={editing} onChange={(v) => setForm((f) => ({ ...f, phone: v }))} />
            <Field label="Email"         value={profile.email}    editing={false}   onChange={() => {}} />
            <Field label="College"       value={profile.college_name} editing={false} onChange={() => {}} />
            <Field label="Role"          value={ROLE_LABEL[profile.role] ?? profile.role} editing={false} onChange={() => {}} />
            <Field label="Member Since"  value={new Date(profile.created_at).toLocaleDateString("en-IN", { year: "numeric", month: "long", day: "numeric" })} editing={false} onChange={() => {}} />
            <Field label="Status"        value={profile.is_active ? "Active" : "Inactive"} editing={false} onChange={() => {}} />
          </div>
        </div>

        {/* ── Signature — Students only ── */}
        {isStudent && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Signature</h2>
                <p className="text-xs text-gray-400 mt-0.5">Used on ID card and documents · max 50KB</p>
              </div>
              {signUploading && <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />}
            </div>

            {/* Signature preview */}
            {profile.signature ? (
              <div className="border border-gray-200 rounded-xl p-4 bg-gray-50 flex items-center justify-center min-h-[100px] mb-4">
                <img src={profile.signature} alt="Signature" className="max-h-24 object-contain" />
              </div>
            ) : (
              <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 flex flex-col items-center justify-center mb-4 bg-gray-50">
                <p className="text-sm text-gray-400">No signature uploaded yet</p>
              </div>
            )}

            {/* Signature upload buttons */}
            <div className="flex gap-3">
              <button onClick={() => signCamRef.current?.click()} disabled={signUploading}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors disabled:opacity-50">
                <Camera className="h-4 w-4" /> Camera
              </button>
              <button onClick={() => signFileRef.current?.click()} disabled={signUploading}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 transition-colors disabled:opacity-50">
                <Upload className="h-4 w-4" /> Upload File
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">JPEG, PNG, WebP · max 50KB</p>

            {/* Hidden inputs — signature */}
            <input ref={signCamRef}  type="file" accept="image/*" capture="environment" className="hidden" onChange={handleSignUpload} />
            <input ref={signFileRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={handleSignUpload} />
          </div>
        )}

        {/* ── Password Change Modal ── */}
        {showPwdModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
            <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
              <div className="flex items-center justify-between mb-5">
                <h3 className="text-lg font-semibold text-gray-900">Change Password</h3>
                <button onClick={() => { setShowPwdModal(false); setPwdError(""); setPwdSuccess(""); }}
                  className="text-gray-400 hover:text-gray-600 text-xl font-bold">✕</button>
              </div>
              {pwdError && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">⚠️ {pwdError}</div>}
              {pwdSuccess && <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-600">✅ {pwdSuccess}</div>}
              <div className="space-y-4">
                {(["old_password","new_password","confirm_password"] as const).map((field) => (
                  <div key={field}>
                    <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                      {field === "old_password" ? "Current Password" : field === "new_password" ? "New Password" : "Confirm New Password"}
                    </label>
                    <input type="password" value={pwdForm[field]}
                      onChange={(e) => setPwdForm((f) => ({ ...f, [field]: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="••••••••••••" />
                  </div>
                ))}
                <p className="text-xs text-gray-400">Minimum 12 characters required.</p>
              </div>
              <div className="flex gap-3 mt-6">
                <button onClick={() => { setShowPwdModal(false); setPwdError(""); }}
                  className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50">Cancel</button>
                <button onClick={handleChangePassword} disabled={pwdLoading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
                  {pwdLoading ? "Changing..." : "Change Password"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Account Security ── */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Security</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-medium text-gray-700">Password</p>
                <p className="text-xs text-gray-400">Last changed recently</p>
              </div>
              <button onClick={() => setShowPwdModal(true)} className="text-sm text-blue-600 font-medium hover:underline">Change</button>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-medium text-gray-700">Two-Factor Authentication</p>
                <p className="text-xs text-gray-400">Add extra security to your account</p>
              </div>
              <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gray-200 text-gray-600">Off</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

function Field({ label, value, editing, onChange }: {
  label: string; value: string; editing: boolean; onChange: (v: string) => void;
}) {
  return (
    <div>
      <p className="text-xs text-gray-400 uppercase tracking-wide font-medium mb-1">{label}</p>
      {editing
        ? <input type="text" value={value} onChange={(e) => onChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        : <p className="text-sm font-semibold text-gray-800">{value || "—"}</p>}
    </div>
  );
}
