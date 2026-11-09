#!/usr/bin/env python3
"""Submit changed (or all sitemap) URLs to IndexNow. Always exits 0."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "traversecitywinetour.com"
BASE = f"https://{HOST}"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH_LIMIT = 10_000
REPO_ROOT = Path(__file__).resolve().parent.parent

IGNORE_PREFIXES = ("admin/", "functions/")
SKIP_FILES = {"404.html"}


def find_key() -> tuple[str, str]:
    """Return (key, keyLocation) from the repo-root <key>.txt file."""
    keys = sorted(REPO_ROOT.glob("*.txt"))
    for path in keys:
        name = path.name
        if name in {"robots.txt"}:
            continue
        stem = path.stem
        if re.fullmatch(r"[0-9a-fA-F]{8,128}", stem):
            key = path.read_text(encoding="utf-8").strip()
            if key != stem:
                print(f"warning: key file {name} content does not match filename", file=sys.stderr)
            return key, f"{BASE}/{name}"
    raise FileNotFoundError("No IndexNow key file (<hex>.txt) found in site root")


def html_path_to_url(rel: str) -> str | None:
    """Map a repo-relative .html path to a clean extensionless canonical URL."""
    rel = rel.replace("\\", "/").lstrip("./")
    if not rel.endswith(".html"):
        return None
    if any(rel == p or rel.startswith(p) for p in IGNORE_PREFIXES):
        return None
    if rel in SKIP_FILES or Path(rel).name in SKIP_FILES:
        return None

    if rel == "index.html":
        return f"{BASE}/"

    parent = str(Path(rel).parent).replace("\\", "/")
    name = Path(rel).stem  # without .html

    if name == "index":
        # folder index → trailing slash
        if parent in (".", ""):
            return f"{BASE}/"
        return f"{BASE}/{parent}/"

    if parent in (".", ""):
        return f"{BASE}/{name}"
    return f"{BASE}/{parent}/{name}"


def changed_html_files(before: str, after: str) -> list[str]:
    """List .html files added or modified between two commits."""
    if not before or re.fullmatch(r"0+", before):
        # First push / unknown parent: compare against empty tree
        cmd = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "--diff-filter=AM", after]
    else:
        cmd = [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=AM",
            f"{before}...{after}",
        ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"git diff failed: {result.stderr.strip()}", file=sys.stderr)
        return []
    files = []
    for line in result.stdout.splitlines():
        path = line.strip()
        if path.endswith(".html"):
            files.append(path)
    return files


def urls_from_files(files: list[str]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for f in files:
        url = html_path_to_url(f)
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def urls_from_sitemap(sitemap_path: Path | None = None) -> list[str]:
    path = sitemap_path or (REPO_ROOT / "sitemap.xml")
    tree = ET.parse(path)
    root = tree.getroot()
    # Handle default namespace
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    urls: list[str] = []
    for loc in root.iter(f"{ns}loc"):
        if loc.text:
            urls.append(loc.text.strip())
    return urls


def fingerprint_for_wait(rel_path: str) -> tuple[str, str] | None:
    """Pick a URL and a short unique snippet from the local file to poll for."""
    url = html_path_to_url(rel_path)
    if not url:
        return None
    text = (REPO_ROOT / rel_path).read_text(encoding="utf-8", errors="replace")
    # Prefer canonical link — stable and unique per page
    m = re.search(r'rel="canonical"\s+href="([^"]+)"', text)
    if m:
        snippet = m.group(0)
        return url, snippet
    # Fallback: a mid-file line of decent length
    for line in text.splitlines():
        s = line.strip()
        if len(s) >= 40 and "<!DOCTYPE" not in s and "<html" not in s:
            return url, s[:120]
    return url, text[:80]


def wait_for_production(
    files: list[str],
    key: str,
    key_location: str,
    timeout_s: int = 300,
) -> None:
    """Poll until production serves new content (or key file), then continue."""
    probe: tuple[str, str] | None = None
    for f in files:
        probe = fingerprint_for_wait(f)
        if probe:
            break
    if not probe:
        # No HTML pages changed — wait for the key file (useful on first deploy)
        probe = (key_location, key)

    url, snippet = probe
    print(f"Waiting for production to serve: {url}")
    deadline = time.time() + timeout_s
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "tcwinetour-indexnow/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode("utf-8", errors="replace")
            if snippet in body:
                print(f"Production looks live (attempt {attempt})")
                return
            print(f"Attempt {attempt}: content not updated yet")
        except Exception as exc:  # noqa: BLE001 — best-effort wait
            print(f"Attempt {attempt}: fetch failed ({exc})")
        time.sleep(15)
    print(f"Timed out after {timeout_s}s waiting for production; submitting anyway")


def post_indexnow(key: str, key_location: str, url_list: list[str]) -> None:
    if not url_list:
        print("No URLs to submit; skipping IndexNow POST")
        return

    # Cap and chunk at 10,000
    chunks = [url_list[i : i + BATCH_LIMIT] for i in range(0, len(url_list), BATCH_LIMIT)]
    print(f"Submitting {len(url_list)} URL(s) in {len(chunks)} batch(es)")

    for i, chunk in enumerate(chunks, 1):
        payload = {
            "host": HOST,
            "key": key,
            "keyLocation": key_location,
            "urlList": chunk,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            INDEXNOW_ENDPOINT,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "tcwinetour-indexnow/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                print(f"Batch {i}/{len(chunks)}: HTTP {resp.status}")
                print(f"Response body: {body!r}")
                print(f"URLs ({len(chunk)}):")
                for u in chunk:
                    print(f"  {u}")
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            print(f"Batch {i}/{len(chunks)}: HTTP {exc.code}")
            print(f"Response body: {err_body!r}")
        except Exception as exc:  # noqa: BLE001 — never fail the deploy
            print(f"Batch {i}/{len(chunks)}: request failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit URLs to IndexNow")
    parser.add_argument(
        "--mode",
        choices=("changed", "all"),
        default="changed",
        help="changed: git diff HTML; all: every sitemap.xml URL",
    )
    parser.add_argument("--before", default=os.environ.get("INDEXNOW_BEFORE", ""))
    parser.add_argument("--after", default=os.environ.get("INDEXNOW_AFTER", "HEAD"))
    parser.add_argument("--skip-wait", action="store_true", help="Do not poll production first")
    parser.add_argument("--wait-timeout", type=int, default=300)
    parser.add_argument("--map-only", action="store_true", help="Print mapped URLs and exit")
    parser.add_argument("--files", nargs="*", help="Explicit file list (for tests)")
    args = parser.parse_args()

    try:
        key, key_location = find_key()
        print(f"IndexNow keyLocation: {key_location}")

        files: list[str] = []
        if args.mode == "all":
            urls = urls_from_sitemap()
            print(f"Loaded {len(urls)} URL(s) from sitemap.xml")
        else:
            files = list(args.files) if args.files else changed_html_files(args.before, args.after)
            print(f"Changed HTML files ({len(files)}):")
            for f in files:
                print(f"  {f}")
            urls = urls_from_files(files)

        print(f"Mapped URL list ({len(urls)}):")
        for u in urls:
            print(f"  {u}")

        if args.map_only:
            return 0

        if not args.skip_wait:
            wait_files = files if args.mode == "changed" else []
            wait_for_production(wait_files, key, key_location, args.wait_timeout)

        post_indexnow(key, key_location, urls)
    except Exception as exc:  # noqa: BLE001 — never fail the deploy
        print(f"IndexNow error (ignored): {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
