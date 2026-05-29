import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency = "INR"): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(date: string | Date, format = "DD/MM/YYYY"): string {
  const d = new Date(date);
  if (format === "DD/MM/YYYY") {
    return d.toLocaleDateString("en-IN", { day: "2-digit", month: "2-digit", year: "numeric" });
  }
  return d.toLocaleDateString("en-IN");
}

export function truncate(str: string, length = 50): string {
  return str.length > length ? `${str.substring(0, length)}...` : str;
}

export function getInitials(name: string): string {
  return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}

export function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    super_admin: "Super Admin",
    principal: "Principal",
    vice_principal: "Vice Principal",
    registrar: "Registrar",
    accountant: "Accountant",
    cashier: "Cashier",
    admission_officer: "Admission Officer",
    hod: "Head of Department",
    teacher: "Teacher",
    student: "Student",
    parent: "Parent",
    librarian: "Librarian",
    hostel_warden: "Hostel Warden",
    coe: "Controller of Examinations",
  };
  return labels[role] ?? role.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function generateAvatarFallback(name: string): string {
  return getInitials(name);
}
