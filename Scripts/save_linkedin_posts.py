#!/usr/bin/env python3
"""
Save manually copied LinkedIn posts as grouped markdown files by author.

Examples:
  python Scripts/save_linkedin_posts.py --author "Ross Simmonds" --info-file ross-info.txt --post-file post-1.txt --post-file post-2.txt
  python Scripts/save_linkedin_posts.py --author "Ross Simmonds" --interactive

Output:
  Research/Linkedin_Posts/ross-simmonds/ross-simmonds-linkedin-posts.md
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "Research" / "Linkedin_Posts"
POSTS_MARKER = "<!-- posts:start -->"


@dataclass(frozen=True)
class LinkedInPost:
    content: str
    source_url: str = ""
    post_date: str = ""
    note: str = ""


def slugify(value: str, max_length: int = 90) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (slug[:max_length].strip("-") or "unknown-author")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]

    cleaned: list[str] = []
    blank_seen = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if not blank_seen:
                cleaned.append("")
            blank_seen = True
            continue
        cleaned.append(stripped)
        blank_seen = False

    return "\n".join(cleaned).strip()


def read_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def read_multiline(prompt: str) -> str:
    print(prompt)
    print("Paste text below. Type END on its own line when finished.")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def parse_post_file(path: str) -> LinkedInPost:
    text = read_text_file(path)
    return LinkedInPost(content=text)


def build_header(author: str, general_info: str) -> str:
    now = datetime.now().date().isoformat()
    info = clean_text(general_info) or "_Add general author information here._"

    return "\n".join(
        [
            "---",
            f'title: "{author.replace(chr(34), chr(39))} LinkedIn Posts"',
            f'author: "{author.replace(chr(34), chr(39))}"',
            "source: LinkedIn",
            f"created: {now}",
            f"last_updated: {now}",
            "---",
            "",
            f"# {author} - LinkedIn Posts",
            "",
            "## General Info",
            "",
            info,
            "",
            "## Posts",
            "",
            POSTS_MARKER,
            "",
        ]
    )


def build_post_markdown(post: LinkedInPost, number: int) -> str:
    captured_on = datetime.now().date().isoformat()
    content = clean_text(post.content)

    lines = [
        f"### Post {number}",
        "",
        f"- Captured on: {captured_on}",
    ]

    if post.post_date:
        lines.append(f"- Posted on: {post.post_date}")
    if post.source_url:
        lines.append(f"- Source URL: {post.source_url}")
    if post.note:
        lines.append(f"- Note: {post.note}")

    lines.extend(["", content or "_No post content provided._", ""])
    return "\n".join(lines)


def count_existing_posts(markdown: str) -> int:
    return len(re.findall(r"^### Post \d+", markdown, flags=re.MULTILINE))


def update_last_updated(markdown: str) -> str:
    today = datetime.now().date().isoformat()
    return re.sub(r"^last_updated: .*$", f"last_updated: {today}", markdown, flags=re.MULTILINE)


def save_author_posts(author: str, general_info: str, posts: list[LinkedInPost], output_root: Path) -> Path:
    author_slug = slugify(author)
    author_dir = output_root / author_slug
    author_dir.mkdir(parents=True, exist_ok=True)

    output_path = author_dir / f"{author_slug}-linkedin-posts.md"
    if output_path.exists():
        markdown = output_path.read_text(encoding="utf-8")
        if POSTS_MARKER not in markdown:
            markdown = markdown.rstrip() + f"\n\n## Posts\n\n{POSTS_MARKER}\n\n"
        markdown = update_last_updated(markdown)
    else:
        markdown = build_header(author, general_info)

    next_post_number = count_existing_posts(markdown) + 1
    additions = []
    for offset, post in enumerate(posts):
        additions.append(build_post_markdown(post, next_post_number + offset))

    if additions:
        markdown = markdown.rstrip() + "\n\n" + "\n\n".join(additions) + "\n"

    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Save manually copied LinkedIn posts into one grouped markdown file per author."
    )
    parser.add_argument("--author", required=True, help="LinkedIn post author name.")
    parser.add_argument("--info", default="", help="General author info text.")
    parser.add_argument("--info-file", help="Text file containing general author info.")
    parser.add_argument("--post", action="append", help="Copied LinkedIn post text. Repeat for multiple posts.")
    parser.add_argument("--post-file", action="append", help="Text file containing copied post text. Repeat for multiple posts.")
    parser.add_argument("--source-url", action="append", help="Optional source URL for each --post, in the same order.")
    parser.add_argument("--post-date", action="append", help="Optional posted date for each --post, in the same order.")
    parser.add_argument("--note", action="append", help="Optional note for each --post, in the same order.")
    parser.add_argument("--interactive", action="store_true", help="Paste general info and posts directly into the terminal.")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Folder where author subfolders should be created.",
    )
    return parser.parse_args()


def collect_posts(args: argparse.Namespace) -> tuple[str, list[LinkedInPost]]:
    general_info = args.info or ""
    if args.info_file:
        general_info = read_text_file(args.info_file)

    posts: list[LinkedInPost] = []
    source_urls = args.source_url or []
    post_dates = args.post_date or []
    notes = args.note or []

    for index, raw_post in enumerate(args.post or []):
        posts.append(
            LinkedInPost(
                content=raw_post,
                source_url=source_urls[index] if index < len(source_urls) else "",
                post_date=post_dates[index] if index < len(post_dates) else "",
                note=notes[index] if index < len(notes) else "",
            )
        )

    for path in args.post_file or []:
        posts.append(parse_post_file(path))

    if args.interactive:
        if not general_info:
            general_info = read_multiline("General author info")

        while True:
            raw_post = read_multiline(f"LinkedIn post {len(posts) + 1}")
            if raw_post:
                posts.append(LinkedInPost(content=raw_post))

            another = input("Add another post for this author? [y/N]: ").strip().lower()
            if another != "y":
                break

    return general_info, posts


def main() -> int:
    args = parse_args()
    general_info, posts = collect_posts(args)

    if not posts:
        print("Input error: provide at least one --post, --post-file, or use --interactive.", file=sys.stderr)
        return 2

    output_path = save_author_posts(
        author=args.author.strip(),
        general_info=general_info,
        posts=posts,
        output_root=Path(args.output_root),
    )
    print(f"Saved {len(posts)} post(s): {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
