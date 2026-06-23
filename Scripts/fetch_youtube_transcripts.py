#!/usr/bin/env python3
"""
Fetch YouTube transcripts and save clean markdown files by expert name.

Examples:
  python Scripts/fetch_youtube_transcripts.py --item "April Dunford|https://youtu.be/abc123"
  python Scripts/fetch_youtube_transcripts.py --input batch.csv

CSV format:
  expert,url
  April Dunford,https://www.youtube.com/watch?v=abc123
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse

try:
    from youtube_transcript_api import (
        NoTranscriptFound,
        TranscriptsDisabled,
        YouTubeTranscriptApi,
    )
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: youtube-transcript-api\n"
        "Install it with: pip install -r Scripts/requirements.txt"
    ) from exc

try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "Research" / "YouTube_Transcripts"


@dataclass(frozen=True)
class VideoJob:
    expert: str
    url: str


def extract_video_id(url_or_id: str) -> str:
    """Extract a YouTube video ID from youtube.com, youtu.be, shorts, embed, or raw IDs."""
    value = url_or_id.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower().replace("www.", "")

    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
            if video_id:
                return video_id

        path_parts = [part for part in parsed.path.split("/") if part]
        if len(path_parts) >= 2 and path_parts[0] in {"shorts", "embed", "live"}:
            return path_parts[1]

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
        if video_id:
            return video_id

    raise ValueError(f"Could not extract a YouTube video ID from: {url_or_id}")


def slugify(value: str, max_length: int = 90) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (slug[:max_length].strip("-") or "untitled")


def format_date(upload_date: str | None) -> str:
    if not upload_date:
        return "Unknown"
    try:
        return datetime.strptime(upload_date, "%Y%m%d").date().isoformat()
    except ValueError:
        return upload_date


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "Unknown"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_transcript(transcript_items: Iterable[dict], words_per_paragraph: int = 90) -> str:
    paragraphs: list[str] = []
    words: list[str] = []

    for item in transcript_items:
        text = clean_text(str(item.get("text", "")))
        if not text:
            continue
        words.extend(text.split())
        if len(words) >= words_per_paragraph:
            paragraphs.append(" ".join(words))
            words = []

    if words:
        paragraphs.append(" ".join(words))

    return "\n\n".join(paragraphs)


def fetch_transcript(video_id: str, languages: list[str]) -> tuple[str, str]:
    api = YouTubeTranscriptApi()
    try:
        fetched = api.fetch(video_id, languages=languages)
        transcript_items = fetched.to_raw_data()
        language = getattr(fetched, "language_code", languages[0] if languages else "unknown")
    except AttributeError:
        transcript_items = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        language = languages[0] if languages else "unknown"
    except (NoTranscriptFound, TranscriptsDisabled):
        transcript_list = api.list(video_id)
        transcript = transcript_list.find_transcript(languages)
        fetched = transcript.fetch()
        transcript_items = fetched.to_raw_data() if hasattr(fetched, "to_raw_data") else fetched
        language = getattr(transcript, "language_code", languages[0] if languages else "unknown")

    return chunk_transcript(transcript_items), language


def fetch_metadata(url: str, video_id: str) -> dict:
    if YoutubeDL is None:
        return {
            "title": video_id,
            "webpage_url": url,
            "note": "Install yt-dlp to fetch title, upload date, views, channel, and other metadata.",
        }

    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }
    with YoutubeDL(options) as ydl:
        return ydl.extract_info(url, download=False) or {}


def build_markdown(expert: str, url: str, video_id: str, metadata: dict, transcript: str, language: str) -> str:
    title = metadata.get("title") or video_id
    webpage_url = metadata.get("webpage_url") or url
    upload_date = format_date(metadata.get("upload_date"))
    view_count = metadata.get("view_count")
    like_count = metadata.get("like_count")
    channel = metadata.get("channel") or metadata.get("uploader") or "Unknown"
    duration = metadata.get("duration_string") or format_duration(metadata.get("duration"))
    description = clean_text((metadata.get("description") or "").splitlines()[0]) if metadata.get("description") else ""
    tags = metadata.get("tags") or []
    categories = metadata.get("categories") or []

    frontmatter = [
        "---",
        f'title: "{str(title).replace(chr(34), chr(39))}"',
        f'expert: "{expert.replace(chr(34), chr(39))}"',
        f"video_id: {video_id}",
        f"url: {webpage_url}",
        f"upload_date: {upload_date}",
        f"views: {view_count if view_count is not None else 'Unknown'}",
        f"likes: {like_count if like_count is not None else 'Unknown'}",
        f'channel: "{str(channel).replace(chr(34), chr(39))}"',
        f"duration: {duration}",
        f"transcript_language: {language}",
        "---",
        "",
    ]

    details = [
        f"# {title}",
        "",
        "## Video Information",
        "",
        f"- Expert: {expert}",
        f"- Channel: {channel}",
        f"- URL: {webpage_url}",
        f"- Video ID: {video_id}",
        f"- Upload date: {upload_date}",
        f"- Views: {view_count:,}" if isinstance(view_count, int) else "- Views: Unknown",
        f"- Likes: {like_count:,}" if isinstance(like_count, int) else "- Likes: Unknown",
        f"- Duration: {duration}",
        f"- Transcript language: {language}",
    ]

    if categories:
        details.append(f"- Categories: {', '.join(map(str, categories))}")
    if tags:
        details.append(f"- Tags: {', '.join(map(str, tags[:20]))}")
    if description:
        details.extend(["", "## Description", "", description])

    details.extend(["", "## Transcript", "", transcript or "_No transcript text returned._", ""])
    return "\n".join(frontmatter + details)


def parse_item(raw_item: str) -> VideoJob:
    if "|" not in raw_item:
        raise ValueError('Each --item must look like "Expert Name|https://youtube..."')
    expert, url = raw_item.split("|", 1)
    expert = expert.strip()
    url = url.strip()
    if not expert or not url:
        raise ValueError('Each --item must include both expert and URL, separated by "|".')
    return VideoJob(expert=expert, url=url)


def load_jobs(args: argparse.Namespace) -> list[VideoJob]:
    jobs: list[VideoJob] = []

    for item in args.item or []:
        jobs.append(parse_item(item))

    if args.input:
        with Path(args.input).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"expert", "url"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("CSV must contain headers: expert,url")
            for row in reader:
                expert = (row.get("expert") or "").strip()
                url = (row.get("url") or "").strip()
                if expert and url:
                    jobs.append(VideoJob(expert=expert, url=url))

    if not jobs:
        raise ValueError("Provide at least one --item or an --input CSV.")

    return jobs


def save_video(job: VideoJob, output_root: Path, languages: list[str]) -> Path:
    video_id = extract_video_id(job.url)
    metadata = fetch_metadata(job.url, video_id)
    transcript, language = fetch_transcript(video_id, languages)

    title = metadata.get("title") or video_id
    expert_dir = output_root / slugify(job.expert)
    expert_dir.mkdir(parents=True, exist_ok=True)

    upload_date = format_date(metadata.get("upload_date"))
    date_prefix = upload_date if upload_date != "Unknown" else datetime.now().date().isoformat()
    filename = f"{date_prefix}-{slugify(str(title))}-{video_id}.md"
    output_path = expert_dir / filename
    output_path.write_text(
        build_markdown(job.expert, job.url, video_id, metadata, transcript, language),
        encoding="utf-8",
    )
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch YouTube transcripts and save markdown files under Research/YouTube_Transcripts."
    )
    parser.add_argument(
        "--item",
        action="append",
        help='Batch item in the form "Expert Name|YouTube URL". Repeat for multiple videos.',
    )
    parser.add_argument("--input", help="CSV file with headers: expert,url")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Folder where expert subfolders should be created.",
    )
    parser.add_argument(
        "--languages",
        default="en,en-US,en-GB",
        help="Comma-separated transcript language preferences.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root)
    languages = [lang.strip() for lang in args.languages.split(",") if lang.strip()]

    try:
        jobs = load_jobs(args)
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    failures = 0
    for job in jobs:
        try:
            output_path = save_video(job, output_root, languages)
            print(f"Saved: {output_path}")
        except Exception as exc:
            failures += 1
            print(f"Failed: {job.url} ({job.expert}) - {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
