import { jwtVerify } from "jose/jwt/verify";

export type JwtSession = {
  role: string;
  roleSlug?: string;
  userId: string;
  email?: string;
  collegeId?: string;
};

/** Read signing secret once; must match backend JWT_SIGNING_KEY. */
export function getJwtSecret(): Uint8Array | null {
  const raw = process.env.JWT_SECRET_KEY?.trim();
  if (!raw) {
    if (process.env.NODE_ENV === "development") {
      console.error(
        "[auth] JWT_SECRET_KEY missing in frontend env. Run: npm run auth:sync (or copy from backend/.env).",
      );
    }
    return null;
  }
  return new TextEncoder().encode(raw);
}

function normalizeRole(value: unknown): string | null {
  if (typeof value !== "string" || !value.trim()) return null;
  return value.trim().toUpperCase().replace(/-/g, "_");
}

export async function verifyAccessToken(token: string): Promise<JwtSession | null> {
  const secret = getJwtSecret();
  if (!secret) return null;

  try {
    const { payload } = await jwtVerify(token, secret, {
      algorithms: ["HS256"],
      clockTolerance: 60,
    });

    const role = normalizeRole(payload.role);
    const rawId = payload.user_id ?? payload.sub;
    const userId = rawId === undefined || rawId === null ? undefined : String(rawId);
    if (!role || !userId) return null;

    const collegeRaw = payload.college_id;
    const collegeId =
      collegeRaw === undefined || collegeRaw === null ? undefined : String(collegeRaw);

    const roleSlug =
      typeof payload.role_slug === "string" && payload.role_slug.trim()
        ? payload.role_slug.trim().toLowerCase()
        : undefined;

    return {
      role,
      roleSlug,
      userId,
      email: typeof payload.email === "string" ? payload.email : undefined,
      collegeId,
    };
  } catch {
    return null;
  }
}
