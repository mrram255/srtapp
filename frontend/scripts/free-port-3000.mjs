#!/usr/bin/env node
/**
 * Frees port 3000 for local `npm run dev` by stopping the Docker frontend container if it is running.
 */
import { execSync } from "child_process";

function containerRunning(name) {
  try {
    const out = execSync(`docker inspect -f '{{.State.Running}}' ${name} 2>/dev/null`, {
      encoding: "utf8",
    }).trim();
    return out === "true";
  } catch {
    return false;
  }
}

if (containerRunning("srtapp-frontend")) {
  console.log("[dev] Stopping Docker srtapp-frontend so local Next.js can use port 3000…");
  execSync("docker stop srtapp-frontend", { stdio: "inherit" });
} else {
  console.log("[dev] Port 3000: no Docker srtapp-frontend container running.");
}
