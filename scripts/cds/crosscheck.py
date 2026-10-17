from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, check_year, extract_dir  # noqa: E402
from prompt import build_prompt  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug")
    parser.add_argument("year")
    parser.add_argument("--model", default="gpt-6.1-sol")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()

    year = check_year(args.year)
    codex = shutil.which("codex")
    if not codex:
        raise SystemExit("codex CLI not found on PATH")

    out = extract_dir(args.slug) / f"{year}.codex.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    prompt = build_prompt(args.slug, year, "codex")

    command = [
        codex, "exec",
        "--sandbox", "workspace-write",
        "--skip-git-repo-check",
        "--ephemeral",
        "-C", str(ROOT),
        "-o", str(out.with_suffix(".log")),
    ]
    command += ["-m", args.model, "-"]

    subprocess.run(command, input=prompt, text=True, encoding="utf-8", timeout=args.timeout, check=True)
    if not out.exists():
        raise SystemExit(f"codex finished without writing {out}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
