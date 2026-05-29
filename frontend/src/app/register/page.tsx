"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AlertCircle, Eye, EyeOff, Loader2, School, CheckCircle, Camera, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

const STEPS = ["register", "verify", "upload"] as const;
type Step = typeof STEPS[number];

export default function RegisterPage() {
  const router = useRouter();
  const appLabel = process.env.NEXT_PUBLIC_APP_NAME ?? "SRTAPP";
  const photoCamRef  = useRef<HTMLInputElement>(null);
  const photoFileRef = useRef<HTMLInputElement>(null);
  const signCamRef   = useRef<HTMLInputElement>(null);
  const signFileRef  = useRef<HTMLInputElement>(null);

  const [step, setStep]               = useState<Step>("register");
  const [isLoading, setIsLoading]     = useState(false);
  const [error, setError]             = useState("");
  const [showPwd, setShowPwd]         = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState("");
  const [tempToken, setTempToken]     = useState("");
  const [otp, setOtp]                 = useState("");

  const [photoFile, setPhotoFile]     = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [signFile, setSignFile]       = useState<File | null>(null);
  const [signPreview, setSignPreview] = useState<string | null>(null);
  const [uploading, setUploading]     = useState(false);

  const [form, setForm] = useState({
    first_name: "", last_name: "",
    email: "", phone: "",
    password: "", confirm_password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  /* ── Step 1: Register ── */
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm_password) { setError("Passwords do not match."); return; }
    setIsLoading(true);
    try {
      const res  = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form }),
      });
      const data = await res.json() as { ok?: boolean; message?: string };
      if (!res.ok) { setError(data.message ?? "Registration failed."); return; }
      setRegisteredEmail(form.email);
      setStep("verify");
    } catch { setError("Network error. Please try again."); }
    finally   { setIsLoading(false); }
  };

  /* ── Step 2: OTP Verify + auto-login ── */
  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const vRes  = await fetch("/api/auth/verify-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: registeredEmail, otp }),
      });
      const vData = await vRes.json() as { ok?: boolean; message?: string };
      if (!vRes.ok) { setError(vData.message ?? "Verification failed."); return; }

      /* Auto-login to get Bearer token for uploads */
      const lRes  = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: registeredEmail, password: form.password }),
      });
      if (lRes.ok) {
        const lData = await lRes.json() as { access?: string };
        if (lData.access) setTempToken(lData.access);
      }
      setStep("upload");
    } catch { setError("Network error. Please try again."); }
    finally   { setIsLoading(false); }
  };

  /* ── File picker helper ── */
  const pickFile = (
    e: React.ChangeEvent<HTMLInputElement>,
    maxMB: number,
    setFile: (f: File) => void,
    setPreview: (s: string) => void,
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Only JPEG, PNG or WebP allowed."); return;
    }
    if (file.size > maxMB * 1024 * 1024) {
      setError(`File must be under 50KB.`); return;
    }
    setError("");
    setFile(file);
    setPreview(URL.createObjectURL(file));
  };

  /* ── Step 3: Upload photo + signature ── */
  const handleUploadFinish = async () => {
    setUploading(true);
    setError("");
    const apiBase = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1").replace(/\/$/, "");
    const headers = { Authorization: `Bearer ${tempToken}` };

    try {
      if (photoFile && tempToken) {
        const fd = new FormData();
        fd.append("avatar", photoFile);
        await fetch(`${apiBase}/auth/avatar/upload/`, { method: "POST", headers, body: fd });
      }
      if (signFile && tempToken) {
        const fd = new FormData();
        fd.append("signature", signFile);
        await fetch(`${apiBase}/auth/signature/upload/`, { method: "POST", headers, body: fd });
      }
    } catch { /* silently ignore — user can re-upload later */ }
    finally {
      setUploading(false);
      router.push("/login?verified=1");
    }
  };

  const stepIdx   = STEPS.indexOf(step);
  const stepTitle = ["Join " + appLabel, "Verify Email", "Upload Photo & Signature"][stepIdx];
  const stepSub   = [
    "Create your student account",
    `OTP sent to ${registeredEmail}`,
    "Add your photo and signature",
  ][stepIdx];

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md space-y-6">

        {/* Header */}
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-accent shadow-lg">
            <School className="h-8 w-8 text-white" />
          </div>
          <p className="mt-4 text-xs font-medium text-muted-foreground uppercase tracking-widest">
            Step {stepIdx + 1} of 3
          </p>
          <h2 className="mt-1 font-display text-3xl font-bold tracking-tight text-primary">{stepTitle}</h2>
          <p className="mt-2 text-sm text-muted-foreground">{stepSub}</p>
        </div>

        {/* Progress bar */}
        <div className="flex gap-2">
          {STEPS.map((s, i) => (
            <div key={s} className={cn("h-1.5 flex-1 rounded-full transition-all",
              i < stepIdx ? "bg-accent/50" : i === stepIdx ? "bg-accent" : "bg-gray-200")} />
          ))}
        </div>

        <div className="rounded-2xl border border-border bg-surface p-8 shadow-card">
          {error && (
            <div className="mb-5 flex items-center gap-2 rounded-lg bg-error/10 p-3 text-sm text-error">
              <AlertCircle className="h-4 w-4 shrink-0" />{error}
            </div>
          )}

          {/* ── Step 1 ── */}
          {step === "register" && (
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                {(["first_name","last_name"] as const).map((f) => (
                  <div key={f}>
                    <label className="block text-sm font-medium text-foreground capitalize">
                      {f === "first_name" ? "First Name" : "Last Name"}
                    </label>
                    <input name={f} type="text" required value={form[f]} onChange={handleChange}
                      className="mt-1 block w-full rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none focus:border-accent focus:ring-1 focus:ring-accent"
                      placeholder={f === "first_name" ? "Rahul" : "Sharma"} />
                  </div>
                ))}
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">Email</label>
                <input name="email" type="email" required value={form.email} onChange={handleChange}
                  className="mt-1 block w-full rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none focus:border-accent focus:ring-1 focus:ring-accent"
                  placeholder="you@college.edu" />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">Phone</label>
                <input name="phone" type="tel" required value={form.phone} onChange={handleChange}
                  className="mt-1 block w-full rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none focus:border-accent focus:ring-1 focus:ring-accent"
                  placeholder="+91 9999999999" />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">Password</label>
                <div className="relative mt-1">
                  <input name="password" type={showPwd ? "text" : "password"} required value={form.password} onChange={handleChange}
                    className="block w-full rounded-lg border border-input bg-background px-4 py-3 pr-12 text-sm outline-none focus:border-accent focus:ring-1 focus:ring-accent"
                    placeholder="Min 12 characters" />
                  <button type="button" tabIndex={-1} onClick={() => setShowPwd(!showPwd)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
                    {showPwd ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground">Confirm Password</label>
                <input name="confirm_password" type="password" required value={form.confirm_password} onChange={handleChange}
                  className="mt-1 block w-full rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none focus:border-accent focus:ring-1 focus:ring-accent"
                  placeholder="Repeat password" />
              </div>
              <button type="submit" disabled={isLoading}
                className={cn("flex w-full items-center justify-center rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-accent/90 mt-2",
                  isLoading && "cursor-not-allowed opacity-70")}>
                {isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating account…</> : "Create Account"}
              </button>
            </form>
          )}

          {/* ── Step 2 ── */}
          {step === "verify" && (
            <form onSubmit={handleVerify} className="space-y-6">
              <div className="text-center py-2">
                <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
                <p className="text-sm text-gray-500">Enter the 6-digit OTP sent to your email</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground text-center">OTP Code</label>
                <input type="text" maxLength={6} required value={otp} onChange={(e) => setOtp(e.target.value)}
                  className="mt-2 block w-full rounded-lg border border-input bg-background px-4 py-3 text-center tracking-widest text-lg outline-none focus:border-accent focus:ring-1 focus:ring-accent"
                  placeholder="000000" />
              </div>
              <button type="submit" disabled={isLoading}
                className={cn("flex w-full items-center justify-center rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-accent/90",
                  isLoading && "cursor-not-allowed opacity-70")}>
                {isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Verifying…</> : "Verify Email"}
              </button>
              <button type="button" onClick={() => setStep("register")}
                className="w-full text-sm text-muted-foreground hover:text-foreground text-center">
                ← Back to registration
              </button>
            </form>
          )}

          {/* ── Step 3 ── */}
          {step === "upload" && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">

                {/* Photo */}
                <div className="flex flex-col items-center gap-2">
                  <p className="text-sm font-medium text-gray-700">Profile Photo</p>
                  <div onClick={() => photoFileRef.current?.click()}
                    className="w-full aspect-square rounded-xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-accent transition-colors overflow-hidden bg-gray-50">
                    {photoPreview
                      /* eslint-disable-next-line @next/next/no-img-element */
                      ? <img src={photoPreview} alt="Photo" className="w-full h-full object-cover" />
                      : <><Camera className="h-7 w-7 text-gray-400 mb-1" /><span className="text-xs text-gray-400">Click to upload</span></>}
                  </div>
                  <p className="text-xs text-gray-400 text-center">JPEG/PNG/WebP · max 50KB</p>
                  <div className="flex gap-1 w-full">
                    <button type="button" onClick={() => photoCamRef.current?.click()}
                      className="flex-1 flex items-center justify-center gap-1 py-1.5 border border-gray-200 rounded-lg text-xs text-gray-500 hover:bg-gray-50">
                      <Camera className="h-3.5 w-3.5" />Camera
                    </button>
                    <button type="button" onClick={() => photoFileRef.current?.click()}
                      className="flex-1 flex items-center justify-center gap-1 py-1.5 border border-gray-200 rounded-lg text-xs text-gray-500 hover:bg-gray-50">
                      <Upload className="h-3.5 w-3.5" />Upload
                    </button>
                  </div>
                  <input ref={photoCamRef} type="file" accept="image/*" capture="user" className="hidden" onChange={(e) => pickFile(e, 0.05, setPhotoFile, setPhotoPreview)} />
                  <input ref={photoFileRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => pickFile(e, 0.05, setPhotoFile, setPhotoPreview)} />
                </div>

                {/* Signature */}
                <div className="flex flex-col items-center gap-2">
                  <p className="text-sm font-medium text-gray-700">Signature</p>
                  <div onClick={() => signFileRef.current?.click()}
                    className="w-full aspect-square rounded-xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-accent transition-colors overflow-hidden bg-gray-50">
                    {signPreview
                      /* eslint-disable-next-line @next/next/no-img-element */
                      ? <img src={signPreview} alt="Signature" className="w-full h-full object-contain p-2" />
                      : <><Camera className="h-7 w-7 text-gray-400 mb-1" /><span className="text-xs text-gray-400">Click to upload</span></>}
                  </div>
                  <p className="text-xs text-gray-400 text-center">JPEG/PNG/WebP · max 50KB</p>
                  <div className="flex gap-1 w-full">
                    <button type="button" onClick={() => signCamRef.current?.click()}
                      className="flex-1 flex items-center justify-center gap-1 py-1.5 border border-gray-200 rounded-lg text-xs text-gray-500 hover:bg-gray-50">
                      <Camera className="h-3.5 w-3.5" />Camera
                    </button>
                    <button type="button" onClick={() => signFileRef.current?.click()}
                      className="flex-1 flex items-center justify-center gap-1 py-1.5 border border-gray-200 rounded-lg text-xs text-gray-500 hover:bg-gray-50">
                      <Upload className="h-3.5 w-3.5" />Upload
                    </button>
                  </div>
                  <input ref={signCamRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={(e) => pickFile(e, 0.05, setSignFile, setSignPreview)} />
                  <input ref={signFileRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => pickFile(e, 0.05, setSignFile, setSignPreview)} />
                </div>
              </div>

              <button onClick={handleUploadFinish} disabled={uploading}
                className={cn("flex w-full items-center justify-center rounded-lg bg-accent px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-accent/90",
                  uploading && "cursor-not-allowed opacity-70")}>
                {uploading
                  ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Uploading…</>
                  : (photoFile || signFile) ? "Upload & Finish" : "Skip & Finish"}
              </button>
            </div>
          )}
        </div>

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-accent hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
