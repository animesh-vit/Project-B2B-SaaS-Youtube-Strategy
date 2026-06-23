#!/usr/bin/env python3
"""
Summarize raw LinkedIn text exports into clean markdown research files.

Default behavior:
  - Reads every .txt file in Linkedin_Text/
  - Splits each file into posts by "Post 1", "Post 2", etc.
  - Calls the OpenAI API for a concise summary of each post
  - Writes markdown files under Research/Linkedin_Posts/<author-slug>/

Usage:
  python Scripts/summarize_linkedin_posts.py
  python Scripts/summarize_linkedin_posts.py --model gpt-5-mini --force
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_ROOT = PROJECT_ROOT / "Linkedin_Text"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "Research" / "Linkedin_Posts"
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5-mini")
POST_HEADING_RE = re.compile(
    r"^\s*(?:---\s*)?post\s*(?P<number>\d+)?(?:\s*---)?\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class RawLinkedInPost:
    number: int
    content: str


@dataclass(frozen=True)
class AuthorPosts:
    author: str
    author_info: str
    source_file: Path
    posts: list[RawLinkedInPost]


def slugify(value: str, max_length: int = 90) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (slug[:max_length].strip("-") or "unknown")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u200b", "").replace("\ufeff", "")
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


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', "'") + '"'


def parse_author_file(path: Path) -> AuthorPosts:
    text = clean_text(path.read_text(encoding="utf-8"))
    author_match = re.search(r"^Author:\s*(?P<author>.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
    if not author_match:
        raise ValueError(f"{path} must include an 'Author:' line.")

    author = author_match.group("author").strip()
    post_matches = list(POST_HEADING_RE.finditer(text))
    if not post_matches:
        raise ValueError(f"{path} does not contain any 'Post 1' style sections.")

    info_start = author_match.end()
    author_info = clean_text(text[info_start : post_matches[0].start()])

    posts: list[RawLinkedInPost] = []
    for index, match in enumerate(post_matches):
        start = match.end()
        end = post_matches[index + 1].start() if index + 1 < len(post_matches) else len(text)
        content = clean_text(text[start:end])
        if not content:
            continue
        number_text = match.group("number")
        number = int(number_text) if number_text else len(posts) + 1
        posts.append(RawLinkedInPost(number=number, content=content))

    if not posts:
        raise ValueError(f"{path} does not contain any non-empty post content.")

    return AuthorPosts(author=author, author_info=author_info, source_file=path, posts=posts)


def summarize_post(client: Any, model: str, author_posts: AuthorPosts, post: RawLinkedInPost) -> str:
    prompt = f"""
Summarize this LinkedIn post for B2B SaaS marketing research.

Author: {author_posts.author}
Author context: {author_posts.author_info or "Unknown"}

Return only markdown with:
- 1 sentence explaining the core idea
- 3 compact bullets with useful strategic takeaways
- 1 short "Why it matters" sentence

Post:
{post.content}
""".strip()

    response = client.responses.create(
        model=model,
        instructions=(
            "You create concise research notes from LinkedIn posts. "
            "Keep the language plain, specific, and faithful to the source. "
            "Do not invent details that are not present in the post."
        ),
        input=prompt,
    )
    return clean_text(response.output_text)


def build_post_markdown(
    author_posts: AuthorPosts,
    post: RawLinkedInPost,
    summary: str,
    model: str,
) -> str:
    now = datetime.now().date().isoformat()
    title = f"{author_posts.author} LinkedIn Post {post.number}"

    return "\n".join(
        [
            "---",
            f"title: {yaml_quote(title)}",
            f"author: {yaml_quote(author_posts.author)}",
            "source: LinkedIn",
            f"source_file: {yaml_quote(str(author_posts.source_file.relative_to(PROJECT_ROOT)))}",
            f"post_number: {post.number}",
            f"summary_model: {yaml_quote(model)}",
            f"captured_on: {now}",
            "---",
            "",
            f"# {title}",
            "",
            "## Summary",
            "",
            summary or "_Summary unavailable._",
            "",
            "## Raw Post",
            "",
            post.content,
            "",
        ]
    )


def build_author_index(author_posts: AuthorPosts, post_files: list[Path]) -> str:
    now = datetime.now().date().isoformat()
    lines = [
        "---",
        f"title: {yaml_quote(author_posts.author + ' LinkedIn Posts')}",
        f"author: {yaml_quote(author_posts.author)}",
        "source: LinkedIn",
        f"last_updated: {now}",
        "---",
        "",
        f"# {author_posts.author} - LinkedIn Posts",
        "",
        "## Author Info",
        "",
        author_posts.author_info or "_No author information found in the source file._",
        "",
        "## Posts",
        "",
    ]

    for path in post_files:
        lines.append(f"- [{path.stem}]({path.name})")

    lines.append("")
    return "\n".join(lines)


def write_author_posts(
    client: Any,
    author_posts: AuthorPosts,
    output_root: Path,
    model: str,
    force: bool,
) -> list[Path]:
    author_dir = output_root / slugify(author_posts.author)
    author_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    post_files: list[Path] = []
    for post in author_posts.posts:
        post_path = author_dir / f"post-{post.number:03d}.md"
        post_files.append(post_path)

        if post_path.exists() and not force:
            continue

        summary = summarize_post(client, model, author_posts, post)
        markdown = build_post_markdown(author_posts, post, summary, model)
        post_path.write_text(markdown, encoding="utf-8")
        written.append(post_path)

    index_path = author_dir / "index.md"
    index_path.write_text(build_author_index(author_posts, post_files), encoding="utf-8")
    written.append(index_path)
    return written


def preview_author_posts(author_posts: AuthorPosts, output_root: Path) -> list[Path]:
    author_dir = output_root / slugify(author_posts.author)
    post_files = [author_dir / f"post-{post.number:03d}.md" for post in author_posts.posts]
    return [*post_files, author_dir / "index.md"]


def make_openai_client() -> Any:
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The openai package is not installed. Run: pip install -r Scripts/requirements.txt"
        ) from exc

    return OpenAI()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize raw LinkedIn txt files into markdown files organized by author."
    )
    parser.add_argument("--input-root", default=str(DEFAULT_INPUT_ROOT), help="Folder containing raw LinkedIn .txt files.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Folder where markdown files are written.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model to use. Defaults to OPENAI_MODEL or gpt-5-mini.")
    parser.add_argument("--force", action="store_true", help="Regenerate summaries for existing post markdown files.")
    parser.add_argument("--limit", type=int, help="Only process the first N input files.")
    parser.add_argument("--dry-run", action="store_true", help="Parse files and show planned outputs without calling the API.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_root = Path(args.input_root)
    output_root = Path(args.output_root)

    if not input_root.exists():
        print(f"Input folder not found: {input_root}", file=sys.stderr)
        return 2

    source_files = sorted(input_root.glob("*.txt"))
    if args.limit is not None:
        source_files = source_files[: args.limit]
    if not source_files:
        print(f"No .txt files found in {input_root}", file=sys.stderr)
        return 2

    if not args.dry_run and not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is required to generate summaries.", file=sys.stderr)
        return 2

    client = None
    if not args.dry_run:
        try:
            client = make_openai_client()
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    total_posts = 0
    total_written = 0

    for source_file in source_files:
        try:
            author_posts = parse_author_file(source_file)
            if args.dry_run:
                written = preview_author_posts(author_posts, output_root)
                for output_path in written:
                    print(f"Would write: {output_path}")
            else:
                written = write_author_posts(
                    client=client,
                    author_posts=author_posts,
                    output_root=output_root,
                    model=args.model,
                    force=args.force,
                )
        except Exception as exc:
            print(f"Failed: {source_file}: {exc}", file=sys.stderr)
            return 1

        total_posts += len(author_posts.posts)
        total_written += len(written)
        action = "planned" if args.dry_run else "written"
        print(f"{author_posts.author}: {len(author_posts.posts)} post(s), {len(written)} file(s) {action}")

    final_action = "planned" if args.dry_run else "wrote"
    print(f"Done. Processed {total_posts} post(s); {final_action} {total_written} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
