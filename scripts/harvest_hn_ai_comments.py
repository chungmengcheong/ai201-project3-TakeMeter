#!/usr/bin/env python3
"""Harvest HN AI/LLM discussion comments for the TakeMeter labeling task.

The script uses the public HN Algolia API:
  - /api/v1/search to find high-engagement AI/LLM-related stories
  - /api/v1/items/{id} to fetch each story's comment tree

Outputs:
  - raw JSON containing story hits, full item payloads, and normalized comments
  - candidate CSV with all qualified comments
  - 200-row labeling CSV with assignment-ready text and blank labels
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
import urllib.parse
import urllib.request
from collections import OrderedDict
from pathlib import Path
from typing import Any


SEARCH_ENDPOINT = "https://hn.algolia.com/api/v1/search"
ITEM_ENDPOINT = "https://hn.algolia.com/api/v1/items/{item_id}"

DEFAULT_QUERIES = [
    "LLM",
    "AI agents",
    "OpenAI",
    "Claude",
    "ChatGPT",
    "Cursor AI",
    "coding agents",
    "generative AI",
    "large language models",
    "AI coding",
]

AI_RELEVANCE_RE = re.compile(
    r"\b("
    r"AI|LLM|LLMs|OpenAI|Anthropic|Claude|ChatGPT|GPT|Copilot|Cursor|"
    r"agent|agents|agentic|generative AI|large language model|"
    r"DeepSeek|Gemini|Llama|Mistral"
    r")\b",
    flags=re.IGNORECASE,
)
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


def fetch_json(url: str, delay_seconds: float) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "takemeter-class-project/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)
    if delay_seconds:
        time.sleep(delay_seconds)
    return data


def clean_hn_html(text: str | None) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<p>", "\n\n", text)
    text = TAG_RE.sub("", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def story_relevance_text(hit: dict[str, Any]) -> str:
    parts = [
        hit.get("title") or "",
        clean_hn_html(hit.get("story_text")),
        hit.get("url") or "",
    ]
    return " ".join(parts)


def is_ai_related_story(hit: dict[str, Any]) -> bool:
    return bool(AI_RELEVANCE_RE.search(story_relevance_text(hit)))


def search_stories(
    queries: list[str],
    hits_per_query: int,
    min_story_points: int,
    min_story_comments: int,
    delay_seconds: float,
) -> tuple[OrderedDict[str, dict[str, Any]], list[dict[str, Any]]]:
    stories: OrderedDict[str, dict[str, Any]] = OrderedDict()
    raw_hits: list[dict[str, Any]] = []

    for query in queries:
        params = urllib.parse.urlencode(
            {"query": query, "tags": "story", "hitsPerPage": hits_per_query}
        )
        data = fetch_json(f"{SEARCH_ENDPOINT}?{params}", delay_seconds)
        for hit in data.get("hits", []):
            raw_hits.append({"query": query, "hit": hit})

            points = hit.get("points") or 0
            num_comments = hit.get("num_comments") or 0
            if points < min_story_points or num_comments < min_story_comments:
                continue
            if not is_ai_related_story(hit):
                continue

            story_id = str(hit["objectID"])
            if story_id in stories:
                stories[story_id]["matched_queries"].append(query)
                continue

            stories[story_id] = {
                "story_id": story_id,
                "title": hit.get("title") or "",
                "url": hit.get("url") or "",
                "author": hit.get("author") or "",
                "points": points,
                "num_comments": num_comments,
                "created_at": hit.get("created_at") or "",
                "matched_queries": [query],
                "search_hit": hit,
            }

    return stories, raw_hits


def collect_top_level_comments(
    story: dict[str, Any],
    item_payload: dict[str, Any],
    max_comments_per_story: int,
    min_comment_chars: int,
) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    children = item_payload.get("children") or []

    for rank, child in enumerate(children, start=1):
        comment_text = clean_hn_html(child.get("text"))
        if len(comment_text) < min_comment_chars:
            continue

        story_title = story["title"]
        combined_text = f"Post title: {story_title}\n\nComment: {comment_text}"
        comment_id = str(child.get("id") or "")

        comments.append(
            {
                "text": combined_text,
                "label": "",
                "notes": "",
                "comment_text": comment_text,
                "story_title": story_title,
                "story_id": story["story_id"],
                "comment_id": comment_id,
                "comment_url": f"https://news.ycombinator.com/item?id={comment_id}",
                "story_url": f"https://news.ycombinator.com/item?id={story['story_id']}",
                "source_url": story["url"],
                "story_points": story["points"],
                "story_num_comments": story["num_comments"],
                "story_author": story["author"],
                "comment_author": child.get("author") or "",
                "comment_rank": rank,
                "comment_reply_count": len(child.get("children") or []),
                "matched_queries": "|".join(story["matched_queries"]),
                "text_chars": len(combined_text),
                "comment_chars": len(comment_text),
            }
        )

        if len(comments) >= max_comments_per_story:
            break

    return comments


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "text",
        "label",
        "notes",
        "comment_text",
        "story_title",
        "story_id",
        "comment_id",
        "comment_url",
        "story_url",
        "source_url",
        "story_points",
        "story_num_comments",
        "story_author",
        "comment_author",
        "comment_rank",
        "comment_reply_count",
        "matched_queries",
        "text_chars",
        "comment_chars",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hits-per-query", type=int, default=80)
    parser.add_argument("--min-story-points", type=int, default=50)
    parser.add_argument("--min-story-comments", type=int, default=20)
    parser.add_argument("--max-stories", type=int, default=80)
    parser.add_argument("--max-comments-per-story", type=int, default=10)
    parser.add_argument("--shortlist-comments-per-story", type=int, default=5)
    parser.add_argument("--min-comment-chars", type=int, default=120)
    parser.add_argument("--shortlist-size", type=int, default=200)
    parser.add_argument("--delay-seconds", type=float, default=0.05)
    parser.add_argument("--raw-out", default="data/raw/hn_ai_comments_raw.json")
    parser.add_argument("--candidates-out", default="data/processed/hn_ai_comments_candidates.csv")
    parser.add_argument("--shortlist-out", default="data/processed/hn_ai_comments_shortlist_200.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stories, raw_hits = search_stories(
        DEFAULT_QUERIES,
        args.hits_per_query,
        args.min_story_points,
        args.min_story_comments,
        args.delay_seconds,
    )

    selected_stories = list(stories.values())[: args.max_stories]
    raw_items: dict[str, Any] = {}
    all_comments: list[dict[str, Any]] = []

    for story in selected_stories:
        item = fetch_json(ITEM_ENDPOINT.format(item_id=story["story_id"]), args.delay_seconds)
        raw_items[story["story_id"]] = item
        all_comments.extend(
            collect_top_level_comments(
                story,
                item,
                args.max_comments_per_story,
                args.min_comment_chars,
            )
        )

    # Keep the shortlist spread across stories. We collect a larger candidate pool
    # per story, then cap the shortlist to fewer comments per story so the final
    # 200 examples are not dominated by a few huge discussions.
    story_counts: dict[str, int] = {}
    shortlist: list[dict[str, Any]] = []
    for comment in all_comments:
        story_id = comment["story_id"]
        if story_counts.get(story_id, 0) >= args.shortlist_comments_per_story:
            continue
        shortlist.append(comment)
        story_counts[story_id] = story_counts.get(story_id, 0) + 1
        if len(shortlist) >= args.shortlist_size:
            break

    raw_payload = {
        "metadata": {
            "source": "HN Algolia API",
            "search_endpoint": SEARCH_ENDPOINT,
            "item_endpoint": ITEM_ENDPOINT,
            "queries": DEFAULT_QUERIES,
            "hits_per_query": args.hits_per_query,
            "min_story_points": args.min_story_points,
            "min_story_comments": args.min_story_comments,
            "max_stories": args.max_stories,
            "max_comments_per_story": args.max_comments_per_story,
            "shortlist_comments_per_story": args.shortlist_comments_per_story,
            "min_comment_chars": args.min_comment_chars,
            "shortlist_size": args.shortlist_size,
            "stories_found": len(stories),
            "stories_fetched": len(selected_stories),
            "candidate_comments": len(all_comments),
            "shortlisted_comments": len(shortlist),
        },
        "raw_search_hits": raw_hits,
        "stories": selected_stories,
        "raw_items": raw_items,
        "normalized_comments": all_comments,
    }

    write_json(Path(args.raw_out), raw_payload)
    write_csv(Path(args.candidates_out), all_comments)
    write_csv(Path(args.shortlist_out), shortlist)

    print(f"Stories found: {len(stories)}")
    print(f"Stories fetched: {len(selected_stories)}")
    print(f"Candidate comments: {len(all_comments)}")
    print(f"Shortlisted comments: {len(shortlist)}")
    print(f"Raw JSON: {args.raw_out}")
    print(f"Candidate CSV: {args.candidates_out}")
    print(f"Shortlist CSV: {args.shortlist_out}")


if __name__ == "__main__":
    main()
