#!/usr/bin/env python3
"""Build English 5-letter word lists from official ESDB/SCOWL hunspell en_US release.

Outputs:
- english_words_all.txt   (all 5-letter a-z words)
- english_words_unique.txt (5-letter a-z words with unique letters)
- english_words_meta.json (source metadata for traceability)
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

RELEASE_API = "https://api.github.com/repos/en-wl/wordlist/releases/latest"
ASSET_PATTERN = re.compile(r"^hunspell-en_US-\d{4}\.\d{2}\.\d{2}\.zip$")
WORD_RE = re.compile(r"^[a-z]{5}$")

OUT_ALL = Path("english_words_all.txt")
OUT_UNIQ = Path("english_words_unique.txt")
OUT_META = Path("english_words_meta.json")


def fetch_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "ordle-tool/1.0"})
    with urlopen(req, timeout=30) as resp:
        return json.load(resp)


def download_bytes(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "ordle-tool/1.0"})
    with urlopen(req, timeout=60) as resp:
        return resp.read()


def pick_asset(release: dict) -> dict:
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if ASSET_PATTERN.match(name):
            return asset
    raise RuntimeError("Could not find hunspell-en_US release asset.")


def parse_dic_from_zip(data: bytes) -> list[str]:
    zf = zipfile.ZipFile(BytesIO(data), "r")
    dic_name = None
    for name in zf.namelist():
        if name.lower().endswith(".dic"):
            dic_name = name
            break
    if not dic_name:
        raise RuntimeError("No .dic file found in hunspell release zip.")

    lines = zf.read(dic_name).decode("utf-8", errors="ignore").splitlines()
    if not lines:
        return []

    words: set[str] = set()
    for line in lines[1:]:  # first line is count
        entry = line.strip()
        if not entry:
            continue
        # Hunspell entries can be `word/FLAGS`.
        word = entry.split("/", 1)[0].lower()
        if WORD_RE.fullmatch(word):
            words.add(word)

    return sorted(words)


def main() -> int:
    print("Fetching latest ESDB release metadata...")
    release = fetch_json(RELEASE_API)
    asset = pick_asset(release)

    tag = release.get("tag_name", "unknown")
    asset_name = asset.get("name", "unknown")
    url = asset.get("browser_download_url")
    if not url:
        raise RuntimeError("Release asset has no download URL.")

    print(f"Downloading {asset_name}...")
    data = download_bytes(url)

    print("Extracting 5-letter words from hunspell dictionary...")
    all_words = parse_dic_from_zip(data)
    uniq_words = [w for w in all_words if len(set(w)) == 5]

    OUT_ALL.write_text("\n".join(all_words) + "\n", encoding="utf-8")
    OUT_UNIQ.write_text("\n".join(uniq_words) + "\n", encoding="utf-8")

    meta = {
        "source": "en-wl/wordlist",
        "release_tag": tag,
        "asset_name": asset_name,
        "asset_url": url,
        "word_filter": "^[a-z]{5}$",
        "all_words_count": len(all_words),
        "unique_words_count": len(uniq_words),
    }
    OUT_META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_ALL} ({len(all_words)} words)")
    print(f"Wrote {OUT_UNIQ} ({len(uniq_words)} words)")
    print(f"Wrote {OUT_META}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
