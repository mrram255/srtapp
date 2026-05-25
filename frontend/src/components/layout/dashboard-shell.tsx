"use client";

import type { ReactNode } from "react";

import { MobileNav } from "@/components/layout/mobile-nav";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function DashboardShell({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <aside className="hidden shrink-0 lg:block">
        <Sidebar />
      </aside>
      <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto pb-[4.75rem] lg:pb-6">
          <div className="mx-auto max-w-7xl px-4 py-4 lg:px-6 lg:py-6">{children}</div>
        </main>
        <MobileNav />
      </div>
    </div>
  );
}
