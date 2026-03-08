import { execSync } from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";
import type { InternalHookHandler } from "openclaw/plugin-sdk/hooks/internal-hooks.js";

const TASK_TYPES = [
  "coding",
  "research",
  "communication",
  "planning",
  "tool_exec",
  "tool_mcp",
] as const;

/**
 * Simple heuristic task classifier based on conversation content.
 * No LLM call needed — fast keyword matching is good enough.
 */
function classifyTask(text: string): {
  type: string;
  result: "success" | "partial" | "failure";
  summary: string;
} {
  const lower = text.toLowerCase();

  // Classify task type by keyword frequency
  let type = "planning"; // default
  const scores: Record<string, number> = {
    coding: 0,
    research: 0,
    communication: 0,
    planning: 0,
    tool_exec: 0,
    tool_mcp: 0,
  };

  // Coding signals
  if (lower.includes("function ") || lower.includes("const ") || lower.includes("import "))
    scores.coding += 3;
  if (lower.includes("bug") || lower.includes("error") || lower.includes("fix"))
    scores.coding += 2;
  if (lower.includes("```")) scores.coding += 2;
  if (lower.includes("build") || lower.includes("implement")) scores.coding += 1;

  // Research signals
  if (lower.includes("research") || lower.includes("search") || lower.includes("found"))
    scores.research += 3;
  if (lower.includes("article") || lower.includes("paper") || lower.includes("source"))
    scores.research += 2;
  if (lower.includes("web_search") || lower.includes("web_fetch")) scores.research += 3;

  // Communication signals
  if (lower.includes("email") || lower.includes("message") || lower.includes("telegram"))
    scores.communication += 3;
  if (lower.includes("send") || lower.includes("reply") || lower.includes("draft"))
    scores.communication += 2;

  // Tool signals
  if (lower.includes("mcporter") || lower.includes("mcp")) scores.tool_mcp += 3;
  if (lower.includes("exec") || lower.includes("command")) scores.tool_exec += 2;

  // Find highest scoring type
  let maxScore = 0;
  for (const [t, s] of Object.entries(scores)) {
    if (s > maxScore) {
      maxScore = s;
      type = t;
    }
  }

  // Infer result
  let result: "success" | "partial" | "failure" = "success";
  if (
    lower.includes("failed") ||
    lower.includes("couldn't") ||
    lower.includes("error") ||
    lower.includes("broken")
  ) {
    result = "partial";
  }
  if (
    lower.includes("gave up") ||
    lower.includes("can't fix") ||
    lower.includes("blocked")
  ) {
    result = "failure";
  }

  // Generate summary from last user message (crude but effective)
  const userMessages = text.match(/\[user\].*?(?=\[|$)/gs) || [];
  const lastUser = userMessages[userMessages.length - 1] || "";
  const summary =
    lastUser
      .replace(/\[user\]\s*/i, "")
      .trim()
      .slice(0, 120) || "Session work";

  return { type, result, summary };
}

const handler: InternalHookHandler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log("[atlas-gate-post] Session reset detected, capturing outcome...");

  try {
    // Try to read the session transcript
    const sessionId = event.context?.sessionId as string | undefined;
    const sessionFile = event.context?.sessionFile as string | undefined;

    let transcriptText = "";

    if (sessionFile && fs.existsSync(sessionFile)) {
      // Read last 50 lines of transcript
      const content = fs.readFileSync(sessionFile, "utf-8");
      const lines = content.split("\n").filter(Boolean);
      const lastLines = lines.slice(-50);

      // Extract role and content from JSONL
      for (const line of lastLines) {
        try {
          const parsed = JSON.parse(line);
          if (parsed.role && parsed.content) {
            const contentText =
              typeof parsed.content === "string"
                ? parsed.content
                : Array.isArray(parsed.content)
                  ? parsed.content
                      .filter((c: any) => c.type === "text")
                      .map((c: any) => c.text)
                      .join(" ")
                  : "";
            transcriptText += `[${parsed.role}] ${contentText.slice(0, 500)}\n`;
          }
        } catch {
          // Skip malformed lines
        }
      }
    }

    if (!transcriptText || transcriptText.length < 50) {
      console.log("[atlas-gate-post] Transcript too short, skipping outcome capture");
      return;
    }

    // Skip heartbeat-only sessions
    if (
      transcriptText.includes("HEARTBEAT_OK") &&
      !transcriptText.includes("[user]") 
    ) {
      console.log("[atlas-gate-post] Heartbeat-only session, skipping");
      return;
    }

    const { type, result, summary } = classifyTask(transcriptText);

    console.log(`[atlas-gate-post] Classified: type=${type} result=${result} summary="${summary}"`);

    // Run atlas-gate post
    const escapedSummary = summary.replace(/"/g, '\\"').replace(/\n/g, " ");
    const cmd = `atlas-gate post ${type} ${result} "${escapedSummary}"`;

    const output = execSync(cmd, {
      timeout: 15_000,
      encoding: "utf-8",
      env: {
        ...process.env,
        PATH: `/home/ubuntu/clawd/bin:${process.env.PATH}`,
      },
    });

    console.log(`[atlas-gate-post] Logged: ${output.trim()}`);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`[atlas-gate-post] Failed: ${msg}`);
    // Don't block session reset on hook failure
  }
};

export default handler;
