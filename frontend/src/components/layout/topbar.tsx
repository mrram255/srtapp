"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Bell, ChevronDown, LogOut, Menu, Moon, Search, Settings, Sun, User,
} from "lucide-react";
import { generateAvatarFallback } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { useUIStore } from "@/store/ui-store";

export function Topbar() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.classList.toggle("dark", next === "dark");
  };

  const handleLogout = async () => {
    setShowProfileMenu(false);
    await logout();
    router.push("/login");
    router.refresh();
  };

  const displayName =
    [user?.first_name, user?.last_name].filter(Boolean).join(" ").trim() || user?.email || "User";

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-surface px-4 lg:px-6">
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={toggleSidebar}
          className="rounded-lg p-2 text-muted-foreground hover:bg-muted lg:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="hidden items-center md:flex">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search…"
              className="h-10 w-64 rounded-lg border border-input bg-background py-2 pl-10 pr-4 text-sm outline-none ring-ring focus-visible:ring-2"
              aria-label="Search"
            />
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={toggleTheme}
          className="rounded-lg p-2 text-muted-foreground hover:bg-muted"
          aria-label="Toggle theme"
        >
          {theme === "light" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
        </button>

        <div className="relative">
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative rounded-lg p-2 text-muted-foreground hover:bg-muted"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-accent" aria-hidden />
          </button>
          {showNotifications && (
            <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-xl border border-border bg-surface shadow-elevated">
              <div className="border-b border-border p-4">
                <h3 className="font-semibold text-foreground">Notifications</h3>
              </div>
              <div className="max-h-96 overflow-y-auto p-2">
                <div className="rounded-lg p-3 hover:bg-muted">
                  <p className="text-sm font-medium text-foreground">New assignment</p>
                  <p className="mt-1 text-xs text-muted-foreground">You have a new assignment posted.</p>
                  <p className="mt-1 text-xs text-muted-foreground">2 hours ago</p>
                </div>
                <div className="rounded-lg p-3 hover:bg-muted">
                  <p className="text-sm font-medium text-foreground">Fee reminder</p>
                  <p className="mt-1 text-xs text-muted-foreground">Semester fee due soon.</p>
                  <p className="mt-1 text-xs text-muted-foreground">5 hours ago</p>
                </div>
              </div>
              <div className="border-t border-border p-3">
                <Link
                  href="/dashboard/notifications"
                  className="block text-center text-sm text-accent hover:underline"
                  onClick={() => setShowNotifications(false)}
                >
                  View all
                </Link>
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <button
            type="button"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2 rounded-lg p-2 hover:bg-muted"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent text-sm font-bold text-white overflow-hidden">
              {user?.profile_photo
                ? <img src={user.profile_photo} alt={displayName} className="w-full h-full object-cover" onError={(e) => { e.currentTarget.style.display="none"; e.currentTarget.nextElementSibling?.removeAttribute("style"); }} />
                : null}
              <span style={user?.profile_photo ? {display:"none"} : {}}>{generateAvatarFallback(displayName)}</span>
            </div>
            <div className="hidden text-left md:block">
              <p className="text-sm font-medium text-foreground">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-xl border border-border bg-surface shadow-elevated">
              <div className="border-b border-border p-4">
                <p className="font-semibold text-foreground">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <div className="p-2">
                <Link
                  href="/dashboard/profile"
                  className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-foreground hover:bg-muted"
                  onClick={() => setShowProfileMenu(false)}
                >
                  <User className="h-4 w-4" />
                  Profile
                </Link>
                <Link
                  href="/dashboard/settings"
                  className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-foreground hover:bg-muted"
                  onClick={() => setShowProfileMenu(false)}
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </Link>
                <button
                  type="button"
                  onClick={() => void handleLogout()}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-error hover:bg-error/10"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
