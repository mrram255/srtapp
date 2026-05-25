import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ACCESS_COOKIE, ROLE_HOME_SEGMENT } from "@/lib/auth/constants";
import { verifyAccessToken } from "@/lib/auth/jwt";

export default async function DashboardHomePage() {
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;
  if (!token) redirect("/login");

  const session = await verifyAccessToken(token);
  if (!session) redirect("/login");

  const segment = ROLE_HOME_SEGMENT[session.role] ?? "student";
  redirect(`/dashboard/${segment}`);
}
