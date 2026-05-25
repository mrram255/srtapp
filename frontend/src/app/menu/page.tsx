"use client";
import Link from "next/link";
import { useAuthStore } from "@/store/auth-store";
import {
  GraduationCap, Users, BookOpen, CalendarCheck, FileText,
  Activity, Library, Bell, MessageSquare, DollarSign,
  School, BedDouble, Bus, Briefcase, UtensilsCrossed,
  CalendarDays, BarChart3, ShieldCheck, Settings, LayoutDashboard,
} from "lucide-react";

const allModules = [
  { label: "Dashboard",      href: "/dashboard",                    icon: LayoutDashboard, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT","LIBRARIAN","SECURITY"] },
  { label: "Students",       href: "/dashboard/students",           icon: GraduationCap,   roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER"] },
  { label: "Teachers",       href: "/dashboard/teachers",           icon: Users,           roles: ["SUPER_ADMIN","ADMIN","HOD"] },
  { label: "Assignments",    href: "/dashboard/assignments",        icon: FileText,        roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Study Materials",href: "/dashboard/study-materials",    icon: BookOpen,        roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Analytics",      href: "/dashboard/analytics",          icon: BarChart3,       roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","ACCOUNTANT","LIBRARIAN","PARENT"] },
  { label: "Forum",          href: "/dashboard/forum",              icon: MessageSquare,   roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Timetable",      href: "/dashboard/timetable",          icon: CalendarCheck,   roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Exams",          href: "/dashboard/exams",              icon: Activity,        roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Attendance",     href: "/dashboard/attendance",         icon: CalendarCheck,   roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT"] },
  { label: "Finance",        href: "/dashboard/finance",            icon: DollarSign,      roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","ACCOUNTANT"] },
  { label: "Library",        href: "/dashboard/library",            icon: Library,         roles: ["SUPER_ADMIN","ADMIN","HOD","LIBRARIAN","TEACHER","STUDENT"] },
  { label: "Notifications",  href: "/dashboard/notifications",      icon: Bell,            roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT","LIBRARIAN","SECURITY"] },
  { label: "Messages",       href: "/dashboard/messages",           icon: MessageSquare,   roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT"] },
  { label: "Admissions",     href: "/dashboard/admissions",         icon: School,          roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","ACCOUNTANT"] },
  { label: "Hostel",         href: "/dashboard/hostel",             icon: BedDouble,       roles: ["SUPER_ADMIN","ADMIN","STUDENT","PARENT"] },
  { label: "Transport",      href: "/dashboard/transport",          icon: Bus,             roles: ["SUPER_ADMIN","ADMIN","STUDENT","PARENT"] },
  { label: "Placements",     href: "/dashboard/placements",         icon: Briefcase,       roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Mess",           href: "/dashboard/mess",               icon: UtensilsCrossed, roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Events",         href: "/dashboard/events",             icon: CalendarDays,    roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT"] },
  { label: "Reports",        href: "/dashboard/reports",            icon: BarChart3,       roles: ["SUPER_ADMIN","ADMIN","HOD","ACCOUNTANT"] },
  { label: "Gate Log",       href: "/dashboard/gate",               icon: ShieldCheck,     roles: ["SUPER_ADMIN","ADMIN","SECURITY"] },
  { label: "ID Card",        href: "/dashboard/id-card",            icon: ShieldCheck,     roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT"] },
  { label: "Profile",        href: "/dashboard/profile",            icon: Users,           roles: ["SUPER_ADMIN","ADMIN","HOD","TEACHER","STUDENT","PARENT","ACCOUNTANT","LIBRARIAN","SECURITY"] },
  { label: "Settings",       href: "/dashboard/settings",           icon: Settings,        roles: ["SUPER_ADMIN","ADMIN"] },
];

export default function MenuPage() {
  const { user } = useAuthStore();
  const role = user?.role ?? "";
  const modules = allModules.filter((m) => m.roles.includes(role));

  return (
    <div className="p-4 pb-24 max-w-lg mx-auto">
      <h1 className="font-display text-xl font-bold text-foreground mb-1">All Modules</h1>
      <p className="text-xs text-muted-foreground mb-5">Tap any module to open it</p>
      <div className="grid grid-cols-3 gap-3">
        {modules.map((mod) => {
          const Icon = mod.icon;
          return (
            <Link key={mod.href} href={mod.href}
              className="flex flex-col items-center gap-2 p-4 rounded-2xl border border-border bg-surface hover:bg-muted hover:shadow-sm transition-all active:scale-95">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-accent/10">
                <Icon className="h-5 w-5 text-accent" />
              </div>
              <span className="text-xs font-medium text-center text-foreground leading-tight">{mod.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
