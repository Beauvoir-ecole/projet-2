#!/usr/bin/env python3
"""Pre-commit secret scanner.

Blocks a commit when a likely secret is found in the staged changes:
an API key, password, token, a database connection string that embeds
credentials, a private key, or a committed ``.env`` file. Placeholder
values (those used in ``.env.example``) are ignored to avoid false alarms.

Enable it once per clone with:

    git config core.hooksPath hooks
"""
import re
import subprocess
import sys

# Files we never scan: they are meant to hold placeholder examples, and the
# scanner itself contains the very patterns it looks for.
SKIP_FILES = {".env.example", "check_secrets.py"}

# Substrings that mark an obviously fake value, so we don't flag examples.
PLACEHOLDERS = (
    "change-me", "changeme", "your", "ton-", "ton_", "remplace",
    "user:password", "username", "<password", "<pass", "<user",
    "xxxx", "example", "placeholder", "dev-only",
)

# (human label, compiled regex) pairs describing what a secret looks like.
PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("credentials in a URL", re.compile(r"://[^/\s:@]+:[^/\s@]+@")),
    ("hard-coded secret", re.compile(
        r"(?i)(secret_key|password|passwd|api_key|apikey|access_token|token)"
        r"\s*[=:]\s*['\"]?([A-Za-z0-9/+_\-]{16,})"
    )),
]


def staged_files():
    """Return the paths added, copied or modified in the staged changes."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def looks_like_placeholder(line):
    low = line.lower()
    return any(token in low for token in PLACEHOLDERS)


def scan(path):
    """Return a list of (line_number, label, snippet) findings for one file."""
    if path == ".env" or path.endswith("/.env"):
        return [(0, "committed .env file", path)]
    if path.rsplit("/", 1)[-1] in SKIP_FILES:
        return []
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except (OSError, UnicodeDecodeError):
        return []  # binary or unreadable file — nothing to scan
    findings = []
    for number, line in enumerate(lines, 1):
        if looks_like_placeholder(line):
            continue
        for label, pattern in PATTERNS:
            if pattern.search(line):
                findings.append((number, label, line.strip()))
    return findings


def main():
    problems = []
    for path in staged_files():
        for number, label, _snippet in scan(path):
            problems.append((path, number, label))
    if problems:
        print("\n  Commit bloque : un secret a peut-etre ete detecte.\n")
        for path, number, label in problems:
            where = f"{path}:{number}" if number else path
            print(f"  - {where} -> {label}")
        print(
            "\nNe commite jamais de secret (cle, mot de passe, URL de base).\n"
            "Mets-les dans .env (deja ignore par git).\n"
            "Si c'est une fausse alerte : git commit --no-verify\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
