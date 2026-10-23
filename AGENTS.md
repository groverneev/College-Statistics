# College Statistics

Next.js application for publishing Common Data Set statistics.

## Project Rules

- Work directly in the main repository; do not create git worktrees.
- Commit only when asked. Do not add a `Co-Authored-By: __model_name__` trailer.
- To add a college or new CDS years, follow `.claude/skills/add-college/SKILL.md`.
- Do not write data-update notes or reports anywhere in the repo (no `docs/` files). Summarize what you did in your final message only.
- Never show data-source, attribution, or methodology text on the site: no "Data sources" sections, source links, "Source: CDS…/IPEDS…" labels, footnotes, or caveat text under charts (e.g. explaining what net price covers). Do not add `sources`/`notes` fields to school JSON or the schema for this purpose. Just publish the numbers. Why: it adds clutter that no outside visitor cares about.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
