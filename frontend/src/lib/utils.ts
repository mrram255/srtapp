import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(date));
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
  }).format(amount);
}

export function getRoleColor(role: string): string {
  const colors: Record<string, string> = {
    SUPER_ADMIN: "bg-accent text-white",
    ADMIN: "bg-primary text-primary-foreground",
    HOD: "bg-secondary text-secondary-foreground",
    TEACHER: "bg-gold text-primary",
    STUDENT: "bg-success text-white",
    PARENT: "bg-info text-white",
    ACCOUNTANT: "bg-warning text-primary",
    LIBRARIAN: "bg-muted text-foreground",
    SECURITY: "bg-error text-white",
  };
  return colors[role] ?? "bg-muted text-foreground";
}

export function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
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
  return labels[role] ?? role;
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}…`;
}

export function generateAvatarFallback(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}
