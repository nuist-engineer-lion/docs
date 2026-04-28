from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

SENSITIVE = re.compile(
    r"(token=|user-id=|doc-id=|table-id=|view-id=|src-token=|src-block-id=|ou_[a-z0-9]+|Spreadsheet token|Sheet ID：)",
    re.I,
)
MD_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
HTML_LINK = re.compile(r"\b(?:src|href)=(['\"])([^'\"]+)\1")


def is_external(link: str) -> bool:
    if link.startswith(("#", "mailto:", "tel:", "data:", "//")):
        return True
    parsed = urlparse(link)
    return bool(parsed.scheme)


def strip_fragment(link: str) -> str:
    return link.split("#", 1)[0]


def check_sensitive() -> list[str]:
    errors: list[str] = []
    for path in sorted(DOCS_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".html"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for idx, line in enumerate(text.splitlines(), start=1):
            if SENSITIVE.search(line):
                rel = path.relative_to(ROOT)
                errors.append(f"{rel}:{idx}: sensitive marker remains")
    return errors


def check_links() -> list[str]:
    errors: list[str] = []
    for path in sorted(DOCS_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        candidates = [m.group(3) for m in MD_LINK.finditer(text)]
        candidates.extend(m.group(2) for m in HTML_LINK.finditer(text))
        for link in candidates:
            if link.startswith("<") and link.endswith(">"):
                link = link[1:-1]
            target = strip_fragment(link)
            if not target or is_external(target):
                continue
            if target.startswith("/"):
                errors.append(f"{path.relative_to(ROOT)}: root-relative link is not portable: {link}")
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(DOCS_DIR.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: link escapes docs dir: {link}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing link target: {link}")
    return errors


def main() -> int:
    errors = check_sensitive() + check_links()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("content checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

