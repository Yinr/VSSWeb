import argparse
import json
import re
import sys
from pathlib import Path


def normalize_version(value):
    parts = [int(part) for part in re.findall(r"\d+", value)]
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])


def main():
    parser = argparse.ArgumentParser(description="Check update package version against release tag")
    parser.add_argument("tag", help="release tag, for example v0.1")
    parser.add_argument(
        "--version-file",
        default=".update-files/version.txt",
        help="path to update package version file",
    )
    args = parser.parse_args()

    tag_version = args.tag[1:] if args.tag.startswith("v") else args.tag

    try:
        update_info = json.loads(Path(args.version_file).read_text(encoding="utf-8"))
        update_version = str(update_info.get("version", ""))
    except Exception as err:
        print(f"Failed to read {args.version_file}: {err}", file=sys.stderr)
        return 1

    if normalize_version(update_version) != normalize_version(tag_version):
        print(
            f"{args.version_file} version {update_version!r} "
            f"does not match tag {args.tag!r} semantically",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
