import { execSync } from "node:child_process";
import type { InternalHookHandler } from "openclaw/plugin-sdk/hooks/internal-hooks.js";

const handler: InternalHookHandler = async (event) => {
  if (event.type !== "gateway" || event.action !== "startup") {
    return;
  }

  console.log("[atlas-gate-session] Gateway startup detected, running session checks...");

  try {
    const result = execSync("atlas-gate session 2>&1", {
      timeout: 30_000,
      encoding: "utf-8",
      env: {
        ...process.env,
        PATH: `/home/ubuntu/clawd/bin:${process.env.PATH}`,
      },
    });

    const trimmed = result.trim();
    console.log(`[atlas-gate-session] Result:\n${trimmed}`);

    // Only push a message if there are issues worth surfacing
    if (
      trimmed.includes("⚠️") ||
      trimmed.includes("❌") ||
      trimmed.includes("STALE") ||
      trimmed.includes("NOT RUNNING")
    ) {
      event.messages.push(`🏛️ **Session Gate:** Issues detected at startup\n\n${trimmed}`);
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`[atlas-gate-session] Failed: ${msg}`);
    // Don't block gateway startup on hook failure
  }
};

export default handler;
