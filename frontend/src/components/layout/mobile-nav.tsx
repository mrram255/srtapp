"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  CalendarCheck,
  GraduationCap,
  LayoutDashboard,
  Menu,
  Users,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";

const mobileNavItems = [
  {
    label: "Home",
    href: "/dashboard",
    icon: LayoutDashboard,
    roles: [
      "SUPER_ADMIN",
      "ADMIN",
      "HOD",
      "TEACHER",
      "STUDENT",
      "PARENT",
      "ACCOUNTANT",
      "LIBRARIAN",
      "SECURITY",
    ],
  },
  {
    label: "Students",
    href: "/dashboard/students",
    icon: GraduationCap,
    roles: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER"],
  },
  {
    label: "Teachers",
    href: "/dashboard/teachers",
    icon: Users,
    roles: ["SUPER_ADMIN", "ADMIN", "HOD"],
  },
  {
    label: "Academics",
    href: "/dashboard/academics",
    icon: BookOpen,
    roles: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT"],
  },
  {
    label: "Attendance",
    href: "/dashboard/attendance",
    icon: CalendarCheck,
    roles: ["SUPER_ADMIN", "ADMIN", "HOD", "TEACHER", "STUDENT", "PARENT"],
  },
  {
    label: "More",
    href: "/menu",
    icon: Menu,
    roles: [
      "SUPER_ADMIN",
      "ADMIN",
      "HOD",
      "TEACHER",
      "STUDENT",
      "PARENT",
      "ACCOUNTANT",
      "LIBRARIAN",
      "SECURITY",
    ],
  },
];

export function MobileNav() {
  const pathname = usePathname();
  const { user } = useAuthStore();

  const filteredItems = mobileNavItems.filter((item) => item.roles.includes(user?.role ?? ""));

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-surface lg:hidden">
      <ul className="flex items-center justify-around">
        {filteredItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                className={cn(
                  "flex flex-col items-center gap-1 py-2 text-xs font-medium transition-colors",
                  isActive ? "text-accent" : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
