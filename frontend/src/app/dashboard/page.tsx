import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ACCESS_COOKIE } from "@/lib/auth/constants";
import { verifyAccessToken } from "@/lib/auth/jwt";
import { resolveDashboardPath } from "@/lib/auth/role-routes";

export default async function DashboardHomePage() {
  const cookieStore = await cookies();
  const token = cookieStore.get(ACCESS_COOKIE)?.value;
  if (!token) redirect("/login");

  const session = await verifyAccessToken(token);
  if (!session) redirect("/login");

  redirect(resolveDashboardPath(session.role, session.roleSlug));
}
