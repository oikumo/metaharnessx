// MHX orthogonal guard — advise + mirror existing denies; CI is authority.
//
// User runs zero commands: this plugin fires on tool/session events and shells
// out to the Python stdlib core (policy lives in scripts/mhx/preflight.py).
// Dumb bridge: no predicates here, no new hard gates. Throws ONLY where
// opencode.jsonc already denies (.env read, git push/pull/fetch, protected
// destinations). Everything else fail-open with log; CI owns rejection.

import { spawnSync } from "child_process";
import { existsSync } from "fs";
import { join } from "path";

function hasMhx(cwd) {
  try {
    return existsSync(join(cwd, ".mhx", "MHX.yaml"));
  } catch {
    return false;
  }
}

function runMhx(cwd, args) {
  try {
    const r = spawnSync("uv", ["run", "python", "scripts/mhx.py", ...args], {
      cwd,
      timeout: 20000,
      encoding: "utf-8",
    });
    try {
      return JSON.parse(r.stdout);
    } catch {
      return { ok: true, raw: String(r.stdout || "") + String(r.stderr || "") };
    }
  } catch (e) {
    return { ok: true, error: String(e).slice(0, 500) };
  }
}

export const MhxAuto = async ({ project, client, $, directory, worktree }) => {
  const cwd = worktree ?? directory ?? process.cwd();

  const log = async (level, message, extra) => {
    try {
      await client.app.log({
        body: { service: "mhx-auto", level, message, extra },
      });
    } catch {
      // never break the agent on logging failure
    }
  };

  return {
    "tool.execute.before": async (input, output) => {
      if (!hasMhx(cwd)) return;
      try {
        const tool = input.tool;
        const args = output.args ?? {};

        if (tool === "read" && typeof args.filePath === "string") {
          if (/(^|\/)\.env(\..*)?$/.test(args.filePath)) {
            throw new Error(
              "MHX protect: .env* hard=true — refused (mirrors opencode.jsonc deny; CI rejects)"
            );
          }
          return;
        }

        if (
          tool === "edit" ||
          tool === "write" ||
          tool === "patch" ||
          tool === "multiedit"
        ) {
          const p = args.filePath ?? args.path ?? "";
          const v = runMhx(cwd, [
            "preflight",
            "--tool",
            "edit",
            "--path",
            String(p),
            "--json",
          ]);
          if (v.would_be === "would-deny-at-CI") {
            throw new Error(
              `MHX preflight would-deny-at-CI: ${v.clearing_action ?? "choose a non-protected destination"}`
            );
          }
          return;
        }

        if (tool === "bash") {
          const cmd = String(args.command ?? "");
          if (/\bgit\s+(push|pull|fetch)\b/.test(cmd)) {
            throw new Error(
              "MHX deny: git push/pull/fetch via agent shell — use CI workflow (mirrors opencode.jsonc deny)"
            );
          }
          if (
            />>|<<|sed -i|perl -pi|open\(\)\.write|fs\.writeFile|make generate/.test(
              cmd
            )
          ) {
            await log(
              "warn",
              "MHX preflight: possible repo write via bash; CI diff-scan backstops",
              { cmd: cmd.slice(0, 300) }
            );
          }
        }
      } catch (e) {
        if (e && /MHX (protect|deny|preflight would-deny)/.test(e.message || "")) {
          throw e;
        }
        // fail-open: MHX must never break the agent; CI owns rejection
      }
    },

    event: async ({ event }) => {
      if (!hasMhx(cwd)) return;
      try {
        if (event?.type === "session.created") {
          const r = runMhx(cwd, [
            "reconcile",
            "--project",
            "mhx-v1",
            "--json",
          ]);
          await log(
            "info",
            `MHX resume: CURRENT=${r.current ?? "unknown"} findings=${(r.findings ?? []).join("; ") || "none"}`,
            { current: r.current }
          );
        }
        if (event?.type === "session.idle") {
          const v = runMhx(cwd, ["verify", "--json"]);
          if (v.verdict && v.verdict !== "pass") {
            await log(
              "warn",
              `MHX evidence ${v.verdict}: agent runs auto --phase after before push; CI re-executes`,
              { verdict: v.verdict }
            );
          }
        }
      } catch {
        // fail-open
      }
    },
  };
};
