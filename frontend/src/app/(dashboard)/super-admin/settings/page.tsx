"use client";

import { useEffect, useState } from "react";
import { notificationsApi } from "@/lib/api/notifications";

const TABS = ["General", "Notifications", "Security"] as const;

export default function SuperAdminSettingsPage() {
  const [tab, setTab] = useState<(typeof TABS)[number]>("General");
  const [prefs, setPrefs] = useState({
    email_enabled: true,
    sms_enabled: true,
    push_enabled: true,
  });
  const [saved, setSaved] = useState(false);

  const loadPrefs = async () => {
    try {
      const r = await notificationsApi.getPreferences();
      if (r.data) setPrefs({
        email_enabled: r.data.email_enabled,
        sms_enabled: r.data.sms_enabled,
        push_enabled: r.data.push_enabled,
      });
    } catch {
      /* ignore */
    }
  };

  useEffect(() => {
    void loadPrefs();
  }, []);

  const save = async () => {
    await notificationsApi.updatePreferences(prefs);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="flex gap-2 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium ${tab === t ? "border-b-2 border-accent text-accent" : "text-muted-foreground"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "General" && (
        <p className="text-sm text-muted-foreground">Institution profile is managed under Institution config.</p>
      )}

      {tab === "Notifications" && (
        <div className="max-w-md space-y-4">
          {(["email_enabled", "sms_enabled", "push_enabled"] as const).map((key) => (
            <label key={key} className="flex items-center justify-between rounded-lg border border-border p-3">
              <span className="capitalize">{key.replace("_enabled", "")}</span>
              <input
                type="checkbox"
                checked={prefs[key]}
                onChange={(e) => setPrefs((p) => ({ ...p, [key]: e.target.checked }))}
              />
            </label>
          ))}
          <button type="button" onClick={() => void save()} className="rounded-lg bg-accent px-4 py-2 text-sm text-white">
            Save preferences
          </button>
          {saved && <p className="text-sm text-green-600">Saved.</p>}
        </div>
      )}

      {tab === "Security" && (
        <p className="text-sm text-muted-foreground">Session timeout and 2FA are configured at the platform level.</p>
      )}
    </div>
  );
}
