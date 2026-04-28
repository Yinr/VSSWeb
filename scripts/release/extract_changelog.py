import argparse
import re
import sys
from pathlib import Path


def extract_changelog(changelog_path, tag):
    changelog = changelog_path.read_text(encoding="utf-8")
    pattern = rf"^## \[{re.escape(tag)}\][^\n]*\n(?P<body>.*?)(?=^## \[|\Z)"
    match = re.search(pattern, changelog, flags=re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"{changelog_path} does not contain a section for {tag}")

    body = match.group("body").strip()
    if not body:
        raise ValueError(f"{changelog_path} section for {tag} is empty")

    return body + "\n"


def main():
    parser = argparse.ArgumentParser(description="Extract a release section from CHANGELOG.md")
    parser.add_argument("tag", help="release tag, for example v0.1")
    parser.add_argument("--changelog", default="CHANGELOG.md", help="path to changelog file")
    parser.add_argument("--output", default="release-body.md", help="output markdown file")
    args = parser.parse_args()

    try:
        body = extract_changelog(Path(args.changelog), args.tag)
    except Exception as err:
        print(err, file=sys.stderr)
        return 1

    Path(args.output).write_text(body, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
