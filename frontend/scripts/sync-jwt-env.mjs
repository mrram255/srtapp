#!/usr/bin/env node
/**
 * Keeps frontend JWT_SECRET_KEY in sync with backend/.env so middleware
 * can verify Django-issued tokens (most common cause of "login then kicked out").
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const backendEnv = path.resolve(root, "..", "backend", ".env");
const frontendEnv = path.resolve(root, ".env.local");

function readKey(filePath, key) {
  if (!fs.existsSync(filePath)) return "";
  const text = fs.readFileSync(filePath, "utf8");
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq < 0) continue;
    const name = trimmed.slice(0, eq).trim();
    if (name === key) return trimmed.slice(eq + 1).trim();
  }
  return "";
}

const jwt =
  readKey(backendEnv, "JWT_SECRET_KEY") || readKey(backendEnv, "DJANGO_SECRET_KEY");

if (!jwt) {
  console.warn("[sync-jwt-env] No JWT_SECRET_KEY or DJANGO_SECRET_KEY in backend/.env — skip.");
  process.exit(0);
}

let local = fs.existsSync(frontendEnv) ? fs.readFileSync(frontendEnv, "utf8") : "";
const keyLine = `JWT_SECRET_KEY=${jwt}`;

if (/^JWT_SECRET_KEY=/m.test(local)) {
  local = local.replace(/^JWT_SECRET_KEY=.*$/m, keyLine);
} else {
  local = `${local.trimEnd()}\n${keyLine}\n`;
}

const current = readKey(frontendEnv, "JWT_SECRET_KEY");
if (current === jwt) {
  process.exit(0);
}

fs.writeFileSync(frontendEnv, local.endsWith("\n") ? local : `${local}\n`);
console.log("[sync-jwt-env] Updated frontend/.env.local JWT_SECRET_KEY from backend/.env");
