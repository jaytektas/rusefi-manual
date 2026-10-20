#!/usr/bin/env python3
"""Which chapters need review because rusEFI changed under them?

    python3 -I tools/stale_chapters.py [--rusefi /path/to/rusefi] [--report reports/stale.md]

For every chapter listed in skills/state/verified.yaml (chapter: commit), this:
  1. collects the files its hidden source notes cite (STANDARD.md section 4);
  2. makes sure the verified commit exists in the (shallow) rusEFI clone, deepening it if needed;
  3. lists which of those files changed between the verified commit and HEAD, with a diff stat;
  4. regenerates the chapter's settings tables against the current official ini (tools/gen_settings.py
     --out <tmp>) and reports added, removed and changed rows;
  5. reports cited files that no longer exist.
Writes a Markdown report and prints a one-line verdict per chapter. Exit 1 if anything needs review.
"""
import argparse
import difflib
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "documentation/docs"
NOTE = re.compile(r"<!--\s*src:(.*?)-->", re.S)
SNIPPET = re.compile(r'--8<-- "reference/settings/_(\w+)\.table\.md"')


def git(repo, *args, check=True):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check).stdout


def ensure_commit(repo, commit):
    """Deepen a shallow clone until `commit` is present (a docs checkout is cloned --depth 1)."""
    for _ in range(12):
        if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"],
                          capture_output=True).returncode == 0:
            return True
        if git(repo, "rev-parse", "--is-shallow-repository").strip() != "true":
            return False
        subprocess.run(["git", "-C", str(repo), "fetch", "--quiet", "--deepen=300", "origin"], capture_output=True)
    return False


def cited_files(md_text):
    files = set()
    for note in NOTE.findall(md_text):
        for part in note.split(";"):
            path = part.strip().split(" ")[0].strip()
            if path:
                files.add(path)
    return sorted(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rusefi", default=os.environ.get("RUSEFI", str(ROOT.parent / "rusefi")))
    ap.add_argument("--report", default=str(ROOT / "reports/stale.md"))
    a = ap.parse_args()
    repo = pathlib.Path(a.rusefi)
    head = git(repo, "rev-parse", "--short", "HEAD").strip()

    verified = {}
    for line in (ROOT / "skills/state/verified.yaml").read_text().splitlines():
        line = line.split("#")[0].strip()
        if ":" in line:
            k, v = line.split(":", 1)
            verified[k.strip()] = v.strip()

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="gen_settings_"))
    subprocess.run([sys.executable, "-I", str(ROOT / "tools/gen_settings.py"), "--out", str(tmp), "--all"],
                   check=True, capture_output=True)

    out = [f"# Stale-chapter report\n", f"rusEFI checkout at `{head}`.\n"]
    any_stale = False
    for chapter, commit in sorted(verified.items()):
        md = (DOCS / chapter).read_text()
        files = cited_files(md)
        section = [f"\n## {chapter}\n", f"Verified against `{commit}`; {len(files)} cited files.\n"]
        reasons = []

        missing = [f for f in files if not (repo / f).exists()]
        if missing:
            reasons.append("cited files missing")
            section.append("\n**Cited files that no longer exist:**\n" + "".join(f"- `{f}`\n" for f in missing))

        if not ensure_commit(repo, commit):
            reasons.append("verified commit not found")
            section.append(f"\n**Cannot find commit `{commit}`** even after deepening the clone; review the whole chapter.\n")
        else:
            changed = [f for f in git(repo, "diff", "--name-only", commit, "HEAD", "--", *files).split() if f]
            if changed:
                reasons.append(f"{len(changed)} cited files changed")
                stat = git(repo, "diff", "--stat", commit, "HEAD", "--", *changed)
                log = git(repo, "log", "--oneline", f"{commit}..HEAD", "--", *changed)
                section.append("\n**Cited files changed since verification:**\n\n```\n" + stat + "```\n")
                section.append("\nCommits touching them:\n\n```\n" + (log or "(none listed)\n") + "```\n")

        for dialog in SNIPPET.findall(md):
            current = (DOCS / f"reference/settings/_{dialog}.table.md").read_text().splitlines()[2:]
            fresh = (tmp / f"_{dialog}.table.md").read_text().splitlines()[2:]
            if current != fresh:
                reasons.append(f"settings table {dialog} changed")
                diff = "\n".join(difflib.unified_diff(current, fresh, "in manual", "current ini", lineterm="", n=0))
                section.append(f"\n**Settings table `{dialog}` differs from the current ini:**\n\n```diff\n{diff}\n```\n")

        verdict = "needs review: " + ", ".join(reasons) if reasons else "up to date"
        any_stale |= bool(reasons)
        section.insert(1, f"**{verdict}**\n\n")
        out += section
        print(f"{chapter}: {verdict}")

    pathlib.Path(a.report).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(a.report).write_text("".join(out))
    print(f"report: {a.report}")
    sys.exit(1 if any_stale else 0)


if __name__ == "__main__":
    main()
