"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3, BedDouble, Bell, BookOpen, Briefcase, Bus,
  CalendarCheck, CalendarDays, ChevronLeft, ChevronRight,
  Clock, DollarSign, FileText, GraduationCap, LayoutDashboard,
  Library, LogOut, MessageSquare, School, Settings, ShieldCheck,
  Users, UtensilsCrossed,
} from "lucide-react";
import { cn, getRoleLabel } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { useUIStore } from "@/store/ui-store";
import { useRouter } from "next/navigation";

interface NavItem {
  label: string;
  href: string;
  icon: ReactNode;
  roles: string[];
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT","LIBRARIAN","SECURITY"] },
  { label: "Students", href: "/dashboard/students", icon: <GraduationCap className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER"] },
  { label: "Teachers", href: "/dashboard/teachers", icon: <Users className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD"] },
  { label: "Academics", href: "/dashboard/academics", icon: <BookOpen className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Timetable", href: "/dashboard/timetable", icon: <Clock className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Attendance", href: "/dashboard/attendance", icon: <CalendarCheck className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT"] },
  { label: "Assignments", href: "/dashboard/assignments", icon: <FileText className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Study Materials", href: "/dashboard/study-materials", icon: <BookOpen className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Analytics", href: "/dashboard/analytics", icon: <BarChart3 className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","ACCOUNTANT","LIBRARIAN","PARENT"] },
  { label: "Forum", href: "/dashboard/forum", icon: <MessageSquare className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Exams", href: "/dashboard/exams", icon: <FileText className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Finance", href: "/dashboard/finance", icon: <DollarSign className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","ACCOUNTANT"] },
  { label: "Library", href: "/dashboard/library", icon: <Library className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","LIBRARIAN","TEACHER","STUDENT"] },
  { label: "Notifications", href: "/dashboard/notifications", icon: <Bell className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT","LIBRARIAN","SECURITY"] },
  { label: "Messages", href: "/dashboard/messages", icon: <MessageSquare className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT"] },
  { label: "Admissions", href: "/dashboard/admissions", icon: <School className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","ACCOUNTANT"] },
  { label: "Hostel", href: "/dashboard/hostel", icon: <BedDouble className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","STUDENT","PARENT"] },
  { label: "Transport", href: "/dashboard/transport", icon: <Bus className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","STUDENT","PARENT"] },
  { label: "Placements", href: "/dashboard/placements", icon: <Briefcase className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Mess", href: "/dashboard/mess", icon: <UtensilsCrossed className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Events", href: "/dashboard/events", icon: <CalendarDays className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT"] },
  { label: "Reports", href: "/dashboard/reports", icon: <BarChart3 className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","ACCOUNTANT"] },
  { label: "Gate Log", href: "/dashboard/gate", icon: <ShieldCheck className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","SECURITY"] },
  { label: "ID Card", href: "/dashboard/id-card", icon: <ShieldCheck className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Settings", href: "/dashboard/settings", icon: <Settings className="h-5 w-5" />, roles: ["SUPER_ADMIN","ADMIN"] },
  { label: "Users", href: "/dashboard/users", icon: <Users className="h-5 w-5" />, roles: ["SUPER_ADMIN"] },
  { label: "Roles", href: "/dashboard/roles", icon: <ShieldCheck className="h-5 w-5" />, roles: ["SUPER_ADMIN"] },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const sidebarOpen = useUIStore((s) => s.sidebarOpen);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const filteredNavItems = navItems.filter((item) => item.roles.includes(user?.role ?? ""));
  const appLabel = process.env.NEXT_PUBLIC_APP_NAME ?? "SRTAPP";

  return (
    <div className={cn("flex h-screen flex-col border-r border-border bg-surface transition-all duration-300", sidebarOpen ? "w-64" : "w-20")}>
      <div className="flex h-16 items-center justify-between border-b border-border px-4">
        <Link href="/dashboard" className="flex min-w-0 items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full overflow-hidden bg-white border border-gray-200 shadow-sm">
            <img src="/logo.png" alt="SRT College" className="w-9 h-9 object-contain" onError={(e) => { e.currentTarget.style.display="none"; }} />
          </div>
          {sidebarOpen ? (
            <div className="flex min-w-0 flex-col">
              <span className="truncate font-display text-sm font-bold text-primary">SRT College, Dhmari</span>
              <span className="truncate text-[10px] text-muted-foreground">{getRoleLabel(user?.role ?? "")}</span>
            </div>
          ) : null}
        </Link>
        <button type="button" onClick={toggleSidebar} className="hidden shrink-0 rounded-lg p-1.5 text-muted-foreground hover:bg-muted lg:block">
          {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-1">
          {filteredNavItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <li key={item.href}>
                <Link href={item.href} className={cn("flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors", isActive ? "bg-accent/10 text-accent" : "text-muted-foreground hover:bg-muted hover:text-foreground")} title={!sidebarOpen ? item.label : undefined}>
                  <span className={cn("shrink-0", isActive && "text-accent")}>{item.icon}</span>
                  {sidebarOpen ? <span>{item.label}</span> : null}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

    </div>
  );
}
