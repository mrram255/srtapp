#!/usr/bin/env node
/**
 * Picks a reachable LAN IP for Metro / Expo QR (skips Docker-style 172.17–172.19 bridges).
 * On WSL2, prefers Windows IPv4 Wi‑Fi / Ethernet DHCP addresses via powershell.exe.
 *
 * Honour existing: REACT_NATIVE_PACKAGER_HOSTNAME
 * Usage (from mobile/): node scripts/dev-server-host.cjs [args...]
 * Examples:
 *   node scripts/dev-server-host.cjs expo start --lan
 *   npm start
 */

const { spawnSync, execSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

function isProbablyDockerBridge(ip) {
  const m = /^172\.(\d+)\./.exec(ip);
  if (!m) return false;
  const second = Number(m[1]);
  return second >= 17 && second <= 31;
}

function scoreIp(ip) {
  if (/^192\.168\.\d+\.\d+$/.test(ip)) return 100;
  if (/^10\.\d+\.\d+\.\d+$/.test(ip)) return 80;
  const m = /^172\.(\d+)\.\d+\.\d+$/.exec(ip);
  if (m) {
    const s = Number(m[1]);
    if (s >= 16 && s <= 31 && !isProbablyDockerBridge(ip)) return 60;
    if (s >= 16 && s <= 31) return 45;
  }
  return 10;
}

function pickFromOsIfaces() {
  const nets = os.networkInterfaces();
  const cand = [];
  for (const name of Object.keys(nets)) {
    for (const a of nets[name] ?? []) {
      if (a.internal || a.family !== "IPv4") continue;
      const ip = a.address;
      if (ip.startsWith("127.")) continue;
      cand.push({ ip, name, score: scoreIp(ip) });
    }
  }
  cand.sort((a, b) => {
    const ab = scoreIp(a.ip) + (isProbablyDockerBridge(a.ip) ? -80 : 0);
    const bb = scoreIp(b.ip) + (isProbablyDockerBridge(b.ip) ? -80 : 0);
    return bb - ab;
  });
  return cand[0]?.ip;
}

function isWsl() {
  try {
    const v = fs.readFileSync("/proc/version", "utf8");
    return /\bMicrosoft\b/i.test(v);
  } catch {
    return false;
  }
}

/** Windows LAN IPv4 via PowerShell (WSL2 → Windows host). */
function windowsLanIpFromWslPowerShell() {
  if (process.platform !== "linux" || !isWsl()) return undefined;

  const attempts = [
    /** Prefer Preferred + lowest metric — no DHCP filter (covers static IPs). */
    "(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue " +
      "| Where-Object { $_.IPAddress -match '^(192\\\\.168\\\\.|10\\\\.)' -and ($_.AddressState -eq 'Preferred') } " +
      "| Sort-Object InterfaceMetric | Select-Object -First 1 -ExpandProperty IPAddress)",
    /** Any non-duplicate 192.168.* */
    "(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue " +
      "| Where-Object { $_.IPAddress -like '192.168.*' } " +
      "| Sort-Object InterfaceMetric | Select-Object -First 1 -ExpandProperty IPAddress)",
    /** Fallback: DHCP / manual origins */
    "(Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue " +
      "| Where-Object { $_.IPAddress -match '^(192\\\\.168\\\\.|10\\\\.)' -and ($_.PrefixOrigin -match 'Dhcp|Manual|RouterAdvertisement') } " +
      "| Sort-Object InterfaceMetric | Select-Object -First 1 -ExpandProperty IPAddress)",
  ];

  for (const ps of attempts) {
    try {
      const out = execSync(`powershell.exe -NoProfile -Command "${ps}"`, {
        encoding: "utf8",
        timeout: 15_000,
        stdio: ["ignore", "pipe", "pipe"],
      }).trim();
      const ip = out
        .split(/\r?\n/)
        .map((s) => s.trim())
        .find((s) => /^(?:192\.168\.|10\.)/.test(s));
      if (ip && !ip.startsWith("10.255.") /** WSL shim */) return ip;
    } catch {
      /* try next */
    }
  }

  return undefined;
}

/** Parse `cmd.exe ipconfig` when PowerShell/Get-NetIPAddress is blocked or fails. */
function windowsLanIpFromCmdIpconfig() {
  if (process.platform !== "linux" || !isWsl()) return undefined;
  try {
    const out = execSync("cmd.exe /c ipconfig", {
      encoding: "utf8",
      timeout: 20_000,
      stdio: ["ignore", "pipe", "pipe"],
    });
    const ips = [];
    for (const m of out.matchAll(/\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b/g)) {
      ips.push(m[1]);
    }
    const uniq = [...new Set(ips)].filter((ip) => {
      if (ip.startsWith("127.")) return false;
      if (ip.startsWith("169.254.")) return false;
      if (/^224\.|^239\./.test(ip)) return false;
      /** WSL/host virtual — not your Wi‑Fi */
      if (ip.startsWith("10.255.")) return false;
      if (isProbablyDockerBridge(ip)) return false;
      return /^192\.168\.|^10\./.test(ip);
    });

    const c192 = uniq.find((ip) => /^192\.168\./.test(ip));
    if (c192) return c192;
    const c10 = uniq.find((ip) => /^10\./.test(ip));
    if (c10) return c10;
    return undefined;
  } catch {
    return undefined;
  }
}

function pickLinuxRouteSrcIp() {
  try {
    const out = execSync("ip -4 route get 1.1.1.1", { encoding: "utf8" });
    const m = /\bsrc\s+(\d+\.\d+\.\d+\.\d+)/.exec(out);
    return m?.[1];
  } catch {
    return undefined;
  }
}

function listPreferredLanFromOsIfaces() {
  const nets = os.networkInterfaces();
  const cand = [];
  for (const name of Object.keys(nets)) {
    for (const a of nets[name] ?? []) {
      if (a.internal || a.family !== "IPv4") continue;
      const ip = a.address;
      if (ip.startsWith("127.")) continue;
      if (/^192\.168\.\d+\.\d+$/.test(ip)) cand.push({ ip, score: 100 });
      else if (/^10\.\d+\.\d+\.\d+$/.test(ip)) cand.push({ ip, score: 80 });
    }
  }
  cand.sort((a, b) => b.score - a.score);
  return cand.map((c) => c.ip);
}

function resolvePackagerHost() {
  const existing = process.env.REACT_NATIVE_PACKAGER_HOSTNAME?.trim();
  if (existing) return existing;

  const winsPs = windowsLanIpFromWslPowerShell();
  if (winsPs) return winsPs;

  const winsCmd = windowsLanIpFromCmdIpconfig();
  if (winsCmd) return winsCmd;

  const preferredIfaces = listPreferredLanFromOsIfaces();
  if (preferredIfaces.length > 0) return preferredIfaces[0];

  const routeIp = pickLinuxRouteSrcIp();
  if (routeIp && !/^127\./.test(routeIp)) {
    /** Last resort — may be unreachable from phone (Docker / WSL). */
    if (!isProbablyDockerBridge(routeIp)) return routeIp;
  }

  const fallbackIface = pickFromOsIfaces();
  if (fallbackIface) {
    console.error(
      "\n[SRTAPP mobile] WARN: QR may show a LAN IP phones cannot reach (Docker/WSL). " +
        "Set REACT_NATIVE_PACKAGER_HOSTNAME to your PC Wi‑Fi IPv4 from ipconfig, or use adb reverse.\n",
    );
    return fallbackIface;
  }

  return routeIp ?? "127.0.0.1";
}

function argsFromProcess() {
  const raw = process.argv.slice(2);
  if (!raw.length) return ["expo", "start", "--lan"];

  /** Support: npm run start -- expo start ... */
  let i = 0;
  if (raw[i] === "--") i++;

  /** Allow: npm run start -- expo start … */
  if (raw.slice(i).length === 1 && raw[raw.length - 1] === "") return ["expo", "start", "--lan"];

  return raw.slice(i);
}

const host = resolvePackagerHost();
const env = { ...process.env, REACT_NATIVE_PACKAGER_HOSTNAME: host };

// eslint-disable-next-line no-console
console.error(`\n[SRTAPP mobile] Expo / Metro packager hostname: ${host}\n`);

const args = argsFromProcess();
const isWin = process.platform === "win32";
const cwd = path.resolve(__dirname, "..");

const result = spawnSync(isWin ? "npx.cmd" : "npx", args, {
  cwd,
  env,
  stdio: "inherit",
  shell: isWin,
});

process.exit(typeof result.status === "number" ? result.status : 1);
