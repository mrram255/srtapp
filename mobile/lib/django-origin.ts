/** API base ends with `/api/v1` — Django root is one level up (`/health/`, `/manage-portal/`). */
export function djangoOriginFromApiV1Base(apiBaseURL: string): string {
  const s = apiBaseURL.trim().replace(/\/$/, "");
  const withScheme = /^https?:\/\//i.test(s) ? s : `http://${s}`;
  return withScheme.replace(/\/api\/v1$/i, "").replace(/\/$/, "") || withScheme;
}
