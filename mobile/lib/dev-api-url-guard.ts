/**
 * Dev-only: warns when EXPO_PUBLIC_API_URL is unreachable from Expo Go on a physical phone.
 * Web on the laptop can still work — the browser shares the PC network namespace.
 */

export function phoneLikelyCannotReachApiUrl(raw: string | undefined): string | null {
  if (!raw?.trim()) return null;
  const s = raw.trim().replace(/\/$/, "");

  let url: URL;
  try {
    url = new URL(s.includes("://") ? s : `http://${s}`);
  } catch {
    return null;
  }

  const h = url.hostname;

  if (h === "localhost" || h === "127.0.0.1") {
    return "API host is 127.0.0.1 / localhost — a phone cannot reach your PC Django over Wi‑Fi. Use Windows ipconfig IPv4 + USB adb reverse, or http://YOUR_WIFI_IP:8000/api/v1.";
  }

  /** RFC1918 172.16–172.31: includes Docker / default WSL2 vNIC — not routable from home Wi‑Fi phones. */
  if (/^172\.(1[6-9]|2\d|3[0-1])\./.test(h)) {
    return "API host is 172.x.x.x — almost always WSL/Docker-internal. Phones cannot open that. Put your PC Wi‑Fi IP in mobile/.env (same host that opens /health/ in phone Chrome).";
  }

  return null;
}
