import { jwtVerify } from "jose/jwt/verify";

import type { Role } from "./constants";

export type JwtSession = {
  role: Role;
  userId: string;
  email?: string;
  collegeId?: string;
};

export async function verifyAccessToken(token: string): Promise<JwtSession | null> {
  const secret = process.env.JWT_SECRET_KEY;
  if (!secret) {
    console.error("JWT_SECRET_KEY is not set");
    return null;
  }

  try {
    const { payload } = await jwtVerify(token, new TextEncoder().encode(secret), {
      algorithms: ["HS256"],
      clockTolerance: 60,
    });

    const role = payload.role as Role | undefined;
    const rawId = payload.user_id ?? payload.sub;
    const userId = rawId === undefined || rawId === null ? undefined : String(rawId);
    if (!role || !userId) return null;

    const collegeRaw = payload.college_id;
    const collegeId =
      collegeRaw === undefined || collegeRaw === null ? undefined : String(collegeRaw);

    return {
      role,
      userId,
      email: typeof payload.email === "string" ? payload.email : undefined,
      collegeId,
    };
  } catch {
    return null;
  }
}
