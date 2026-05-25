"use client";

import { useState } from "react";
import { useAuthStore } from "@/store/auth-store";
import { useUIStore } from "@/store/ui-store";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    attendance: true,
    exams: true,
    fees: true,
    assignments: true,
  });
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const toggleTheme = (t: "light" | "dark") => {
    setTheme(t);
    document.documentElement.classList.toggle("dark", t === "dark");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-sm text-gray-500 mt-0.5">Manage your preferences</p>
        </div>

        {saved && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm font-medium">
            ✅ Settings saved successfully!
          </div>
        )}

        {/* Appearance */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Appearance</h2>
          <div className="flex gap-4">
            <button
              onClick={() => toggleTheme("light")}
              className={`flex-1 flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                theme === "light"
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <span className="text-2xl">☀️</span>
              <div className="text-left">
                <p className="font-medium text-gray-800">Light Mode</p>
                <p className="text-xs text-gray-500">Default theme</p>
              </div>
              {theme === "light" && <span className="ml-auto text-blue-500">✓</span>}
            </button>
            <button
              onClick={() => toggleTheme("dark")}
              className={`flex-1 flex items-center gap-3 p-4 rounded-xl border-2 transition-all ${
                theme === "dark"
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <span className="text-2xl">🌙</span>
              <div className="text-left">
                <p className="font-medium text-gray-800">Dark Mode</p>
                <p className="text-xs text-gray-500">Easy on eyes</p>
              </div>
              {theme === "dark" && <span className="ml-auto text-blue-500">✓</span>}
            </button>
          </div>
        </div>

        {/* Notifications */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Notifications</h2>
          <div className="space-y-3">
            {[
              { key: "email", label: "Email Notifications", desc: "Receive updates via email" },
              { key: "push", label: "Push Notifications", desc: "Browser push notifications" },
              { key: "sms", label: "SMS Notifications", desc: "Receive SMS alerts" },
              { key: "attendance", label: "Attendance Alerts", desc: "Low attendance warnings" },
              { key: "exams", label: "Exam Reminders", desc: "Upcoming exam notifications" },
              { key: "fees", label: "Fee Reminders", desc: "Payment due reminders" },
              { key: "assignments", label: "Assignment Alerts", desc: "New assignments and deadlines" },
            ].map((item) => (
              <div key={item.key} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div>
                  <p className="text-sm font-medium text-gray-700">{item.label}</p>
                  <p className="text-xs text-gray-400">{item.desc}</p>
                </div>
                <button
                  onClick={() => setNotifications((n) => ({ ...n, [item.key]: !n[item.key as keyof typeof n] }))}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    notifications[item.key as keyof typeof notifications]
                      ? "bg-blue-500"
                      : "bg-gray-300"
                  }`}
                >
                  <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-all ${
                    notifications[item.key as keyof typeof notifications] ? "left-7" : "left-1"
                  }`} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Account Info */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-medium text-gray-700">Email</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">Verified</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-medium text-gray-700">Role</p>
                <p className="text-xs text-gray-500">{user?.role}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          className="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors"
        >
          Save Settings
        </button>

      </div>
    </div>
  );
}
