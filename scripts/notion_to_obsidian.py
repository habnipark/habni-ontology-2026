#!/usr/bin/env python3
"""Notion → Obsidian migration script.
Fetches data from Notion API and creates Obsidian-compatible markdown files.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
VAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vault")
NOTION_VERSION = "2022-06-28"


def notion_request(endpoint, method="GET", data=None):
    """Make a request to the Notion API."""
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def query_database(db_id):
    """Fetch all pages from a Notion database (handles pagination)."""
    all_results = []
    has_more = True
    start_cursor = None
    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor
        data = notion_request(f"databases/{db_id}/query", method="POST", data=payload)
        all_results.extend(data["results"])
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")
    return all_results


def get_page_blocks(page_id, recursive=True):
    """Fetch all blocks (content) of a Notion page, recursively fetching children."""
    all_blocks = []
    has_more = True
    start_cursor = None
    while has_more:
        endpoint = f"blocks/{page_id}/children?page_size=100"
        if start_cursor:
            endpoint += f"&start_cursor={start_cursor}"
        data = notion_request(endpoint)
        for block in data["results"]:
            all_blocks.append(block)
            if recursive and block.get("has_children", False):
                try:
                    children = get_page_blocks(block["id"], recursive=True)
                    block["_children"] = children
                except Exception:
                    block["_children"] = []
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")
    return all_blocks


def blocks_to_markdown(blocks, indent=0):
    """Convert Notion blocks to markdown text, handling nested children."""
    lines = []
    prefix = "  " * indent
    for block in blocks:
        btype = block["type"]
        children = block.get("_children", [])

        if btype == "paragraph":
            text = rich_text_to_md(block["paragraph"].get("rich_text", []))
            lines.append(f"{prefix}{text}")
            lines.append("")
        elif btype in ("heading_1", "heading_2", "heading_3"):
            level = int(btype[-1])
            text = rich_text_to_md(block[btype].get("rich_text", []))
            lines.append(f"{'#' * (level + 1)} {text}")
            lines.append("")
        elif btype == "bulleted_list_item":
            text = rich_text_to_md(block[btype].get("rich_text", []))
            lines.append(f"{prefix}- {text}")
        elif btype == "numbered_list_item":
            text = rich_text_to_md(block[btype].get("rich_text", []))
            lines.append(f"{prefix}1. {text}")
        elif btype == "to_do":
            checked = block[btype].get("checked", False)
            text = rich_text_to_md(block[btype].get("rich_text", []))
            mark = "x" if checked else " "
            lines.append(f"{prefix}- [{mark}] {text}")
        elif btype == "code":
            text = rich_text_to_md(block[btype].get("rich_text", []))
            lang = block[btype].get("language", "")
            lines.append(f"{prefix}```{lang}")
            lines.append(text)
            lines.append(f"{prefix}```")
            lines.append("")
        elif btype == "quote":
            text = rich_text_to_md(block[btype].get("rich_text", []))
            lines.append(f"{prefix}> {text}")
            lines.append("")
        elif btype == "divider":
            lines.append(f"{prefix}---")
            lines.append("")
        elif btype == "callout":
            text = rich_text_to_md(block[btype].get("rich_text", []))
            lines.append(f"{prefix}> {text}")
            lines.append("")
        elif btype == "toggle":
            text = rich_text_to_md(block[btype].get("rich_text", []))
            lines.append(f"{prefix}**{text}**")
            lines.append("")
        elif btype == "bookmark":
            url = block[btype].get("url", "")
            if url:
                lines.append(f"{prefix}[Bookmark]({url})")
                lines.append("")
        elif btype == "embed":
            url = block[btype].get("url", "")
            if url:
                lines.append(f"{prefix}[Embed]({url})")
                lines.append("")
        elif btype == "table":
            lines.append(f"{prefix}<!-- table omitted -->")
            lines.append("")
        elif btype == "column_list":
            pass  # Process children below
        elif btype == "column":
            pass  # Process children below

        # Process nested children
        if children:
            child_md = blocks_to_markdown(children, indent=indent + 1 if btype in ("toggle", "bulleted_list_item", "numbered_list_item") else indent)
            if child_md.strip():
                lines.append(child_md)

    return "\n".join(lines)


def rich_text_to_md(rich_text_array):
    """Convert Notion rich text array to markdown."""
    parts = []
    for rt in rich_text_array:
        text = rt.get("plain_text", "")
        annotations = rt.get("annotations", {})
        href = rt.get("href")
        if annotations.get("code"):
            text = f"`{text}`"
        if annotations.get("bold"):
            text = f"**{text}**"
        if annotations.get("italic"):
            text = f"*{text}*"
        if annotations.get("strikethrough"):
            text = f"~~{text}~~"
        if href:
            text = f"[{text}]({href})"
        parts.append(text)
    return "".join(parts)


def sanitize_filename(name):
    """Remove or replace characters that are invalid in filenames."""
    name = name.strip()
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name[:100]  # Limit length


def write_note(folder, filename, frontmatter, body):
    """Write a markdown note to the vault."""
    folder_path = os.path.join(VAULT_PATH, folder)
    os.makedirs(folder_path, exist_ok=True)
    filepath = os.path.join(folder_path, f"{filename}.md")

    lines = ["---"]
    for key, value in frontmatter.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f'  - "{item}"' if isinstance(item, str) and "[[" in item else f"  - {item}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif value is None or value == "":
            lines.append(f'{key}: ""')
        else:
            lines.append(f'{key}: "{value}"' if isinstance(value, str) else f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append(body)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


# ─── BOOK DB Migration ───

def migrate_books():
    """Migrate BOOK database to 3-Resource notes."""
    print("📚 Fetching BOOK database...")
    db_id = "c6261736-e9a4-4dc4-9ce1-ad8b720ba0cb"
    pages = query_database(db_id)
    print(f"   Found {len(pages)} entries")

    migrated = 0
    skipped = 0

    for page in pages:
        props = page["properties"]

        # Extract title
        title_parts = props.get("Name", {}).get("title", [])
        title = "".join([t["plain_text"] for t in title_parts]).strip()
        if not title:
            skipped += 1
            continue

        # Extract properties
        status_obj = props.get("Status", {}).get("status")
        status = status_obj.get("name", "") if status_obj else ""

        tags_obj = props.get("Tags", {}).get("multi_select", [])
        year_tags = [t["name"] for t in tags_obj]

        start_obj = props.get("Start", {}).get("date")
        start_date = start_obj.get("start", "") if start_obj else ""

        fin_obj = props.get("Fin", {}).get("date")
        fin_date = fin_obj.get("start", "") if fin_obj else ""

        # Map to ontology
        if status == "Done" or status == "완료" or fin_date:
            learning_status = "solid"
        elif status == "In progress" or status == "진행 중" or start_date:
            learning_status = "in-progress"
        else:
            learning_status = "not-started"

        read_date = fin_date or start_date or ""
        created = page.get("created_time", "")[:10]

        # Fetch page content
        try:
            blocks = get_page_blocks(page["id"])
            body_content = blocks_to_markdown(blocks)
        except Exception:
            body_content = ""

        frontmatter = {
            "type": "resource",
            "category": "life",
            "tags": [f"reading/{'tech' if any(k in title for k in ['마케팅', '해킹', 'IT', 'HTML', '데이터', '기획']) else 'nonfiction'}"] + [f"reading/year/{y}" for y in year_tags],
            "learning-need": False,
            "learning-status": learning_status,
            "visibility": "blog-safe",
            "created": created,
            "updated": created,
            "resource-type": "book",
            "author": "",
            "rating": "",
            "read-date": read_date,
            "key-concepts": [],
        }

        body = f"# {title}\n\n"
        if body_content.strip():
            body += f"## Notes\n\n{body_content}\n"
        else:
            body += "## Summary\n\n\n## Key Takeaways\n\n\n## Notes\n\n"

        filename = sanitize_filename(title)
        filepath = write_note("3-Resource", filename, frontmatter, body)
        migrated += 1

    print(f"   ✅ Migrated: {migrated}, Skipped (no title): {skipped}")
    return migrated


# ─── Media DB Migration ───

def migrate_media():
    """Migrate Media database to 3-Resource notes. Merges content into existing BOOK DB notes."""
    print("🎬 Fetching Media database...")
    db_id = "145de45c-4820-4608-9a3b-90df4a248ef1"
    pages = query_database(db_id)
    print(f"   Found {len(pages)} entries")

    migrated = 0
    merged = 0
    skipped = 0

    for page in pages:
        props = page["properties"]

        title_parts = props.get("Name", {}).get("title", [])
        title = "".join([t["plain_text"] for t in title_parts]).strip()
        if not title:
            skipped += 1
            continue

        filename = sanitize_filename(title)
        existing_path = os.path.join(VAULT_PATH, "3-Resource", f"{filename}.md")
        is_merge = os.path.exists(existing_path)

        # Extract properties
        score_obj = props.get("Score /5", {}).get("select")
        score = len(score_obj.get("name", "")) // 2 if score_obj and score_obj.get("name") else ""

        author_parts = props.get("Author", {}).get("rich_text", [])
        author = "".join([t["plain_text"] for t in author_parts]).strip()

        status_obj = props.get("Status", {}).get("select")
        status = status_obj.get("name", "") if status_obj else ""

        category_parts = props.get("\x08category", {}).get("rich_text", [])
        media_category = "".join([t["plain_text"] for t in category_parts]).strip()

        review_parts = props.get("\x08Review", {}).get("rich_text", [])
        review = "".join([t["plain_text"] for t in review_parts]).strip()

        oneline_parts = props.get("한줄평", {}).get("rich_text", [])
        oneline = "".join([t["plain_text"] for t in oneline_parts]).strip()

        created = page.get("created_time", "")[:10]

        if status in ("Done", "완료"):
            learning_status = "solid"
        elif status in ("In progress", "진행 중", "Reading"):
            learning_status = "in-progress"
        else:
            learning_status = "not-started"

        frontmatter = {
            "type": "resource",
            "category": "life",
            "tags": ["reading/nonfiction"],
            "learning-need": False,
            "learning-status": learning_status,
            "visibility": "blog-safe",
            "created": created,
            "updated": created,
            "resource-type": "book",
            "author": author,
            "rating": score if score else "",
            "read-date": "",
            "key-concepts": [],
        }

        # Fetch page content (Media DB has the actual content)
        try:
            blocks = get_page_blocks(page["id"])
            body_content = blocks_to_markdown(blocks)
        except Exception:
            body_content = ""

        if is_merge:
            # Merge: read existing note, append Media DB content
            with open(existing_path, "r", encoding="utf-8") as f:
                existing = f.read()

            # Update frontmatter with Media DB's richer data
            # Read existing frontmatter, update author/rating
            additions = []
            if author:
                existing = re.sub(r'author: ".*"', f'author: "{author}"', existing)
            if score:
                existing = re.sub(r'rating: ".*"', f'rating: {score}', existing)

            # Append content
            new_content = ""
            if oneline:
                new_content += f"\n> {oneline}\n"
            if review:
                new_content += f"\n## Review\n\n{review}\n"
            if body_content.strip():
                new_content += f"\n## Content\n\n{body_content}\n"

            if new_content.strip():
                existing = existing.rstrip() + "\n" + new_content

            with open(existing_path, "w", encoding="utf-8") as f:
                f.write(existing)
            merged += 1
        else:
            # New note from Media DB only
            body = f"# {title}\n\n"
            if oneline:
                body += f"> {oneline}\n\n"
            if review:
                body += f"## Review\n\n{review}\n\n"
            if body_content.strip():
                body += f"## Content\n\n{body_content}\n"
            else:
                body += "## Key Takeaways\n\n\n## Notes\n\n"

            write_note("3-Resource", filename, frontmatter, body)
            migrated += 1

    print(f"   ✅ New: {migrated}, Merged into existing: {merged}, Skipped: {skipped}")
    return migrated + merged


# ─── GA4 Curriculum Migration ───

def migrate_ga4_curriculum():
    """Migrate GA4 curriculum to 1-Concept and 2-Project notes."""
    print("📊 Fetching GA4 커리큘럼...")

    # GA4 문제상황별 커리큘럼
    db_id = "54a21290-a023-40b6-993d-67fe2544eb6b"
    pages = query_database(db_id)
    print(f"   Found {len(pages)} curriculum entries")

    migrated = 0
    for page in pages:
        props = page["properties"]

        title_parts = props.get("카테고리", {}).get("title", [])
        title = "".join([t["plain_text"] for t in title_parts]).strip()
        if not title:
            continue

        problem_parts = props.get("문제상황", {}).get("rich_text", [])
        problem = "".join([t["plain_text"] for t in problem_parts]).strip()

        tags_obj = props.get("태그", {}).get("multi_select", [])
        ga4_tags = [t["name"] for t in tags_obj]

        link_parts = props.get("커리큘럼 바로가기", {}).get("rich_text", [])
        link = "".join([t["plain_text"] for t in link_parts]).strip()

        created = page.get("created_time", "")[:10]

        frontmatter = {
            "type": "concept",
            "category": "career",
            "tags": ["marketing/analytics/GA4"] + [f"GA4/{t}" for t in ga4_tags],
            "learning-need": True,
            "learning-status": "not-started",
            "visibility": "private",
            "created": created,
            "updated": created,
            "domain": "web-analytics",
            "related-concepts": ["[[GA4]]"],
            "summary": problem[:100] if problem else title,
            "source": "company",
        }

        body = f"# GA4 커리큘럼: {title}\n\n"
        body += f"## 문제상황\n\n{problem}\n\n"
        body += f"## 관련 기능\n\n"
        for tag in ga4_tags:
            body += f"- {tag}\n"
        body += f"\n## 학습 노트\n\n<!-- 학습 후 정리 -->\n"

        filename = sanitize_filename(f"GA4-{title}")
        write_note("1-Concept", filename, frontmatter, body)
        migrated += 1

    # 전체 커리큘럼 구조
    db_id2 = "028d38dd-8623-4f32-84a2-dfb5f81c646a"
    pages2 = query_database(db_id2)
    print(f"   Found {len(pages2)} curriculum structure entries")

    for page in pages2:
        props = page["properties"]

        title_parts = props.get("이름", {}).get("title", [])
        title = "".join([t["plain_text"] for t in title_parts]).strip()
        if not title:
            continue

        chapter_obj = props.get("챕터", {}).get("select")
        chapter = chapter_obj.get("name", "") if chapter_obj else ""

        created = page.get("created_time", "")[:10]

        # Fetch page content
        try:
            blocks = get_page_blocks(page["id"])
            body_content = blocks_to_markdown(blocks)
        except Exception:
            body_content = ""

        frontmatter = {
            "type": "concept",
            "category": "career",
            "tags": ["marketing/analytics/GA4"],
            "learning-need": True,
            "learning-status": "not-started",
            "visibility": "private",
            "created": created,
            "updated": created,
            "domain": "web-analytics",
            "related-concepts": ["[[GA4]]"],
            "summary": f"GA4 커리큘럼 {chapter}: {title}" if chapter else title,
            "source": "company",
        }

        body = f"# {title}\n\n"
        if chapter:
            body += f"**챕터**: {chapter}\n\n"
        if body_content.strip():
            body += f"{body_content}\n"
        else:
            body += "## 학습 노트\n\n<!-- 학습 후 정리 -->\n"

        filename = sanitize_filename(f"GA4-커리큘럼-{title}")
        write_note("1-Concept", filename, frontmatter, body)
        migrated += 1

    print(f"   ✅ Migrated: {migrated}")
    return migrated


# ─── GA4 Specs Migration ───

def migrate_ga4_specs():
    """Migrate GA4 Specs/Events/Parameters to 1-Concept notes."""
    print("📋 Fetching GA4 Specs...")

    # Specs DB
    db_id = "d00e918c-4eb7-482a-a5fe-6f74829863a1"
    pages = query_database(db_id)
    print(f"   Found {len(pages)} spec entries")

    migrated = 0
    for page in pages:
        props = page["properties"]

        title_parts = props.get("Name", {}).get("title", [])
        title = "".join([t["plain_text"] for t in title_parts]).strip()
        if not title:
            continue

        desc_parts = props.get("Description", {}).get("rich_text", [])
        description = "".join([t["plain_text"] for t in desc_parts]).strip()

        created = page.get("created_time", "")[:10]

        # Fetch page content
        try:
            blocks = get_page_blocks(page["id"])
            body_content = blocks_to_markdown(blocks)
        except Exception:
            body_content = ""

        frontmatter = {
            "type": "concept",
            "category": "career",
            "tags": ["marketing/analytics/GA4", "marketing/data-setup/tracking"],
            "learning-need": True,
            "learning-status": "not-started",
            "visibility": "private",
            "created": created,
            "updated": created,
            "domain": "web-analytics",
            "related-concepts": ["[[GA4]]"],
            "summary": description[:100] if description else title,
            "source": "company",
        }

        body = f"# {title}\n\n"
        if description:
            body += f"## Description\n\n{description}\n\n"
        if body_content.strip():
            body += f"## Details\n\n{body_content}\n"
        else:
            body += "## 학습 노트\n\n<!-- 학습 후 정리 -->\n"

        filename = sanitize_filename(f"GA4-Spec-{title}")
        write_note("1-Concept", filename, frontmatter, body)
        migrated += 1

    print(f"   ✅ Migrated: {migrated}")
    return migrated


# ─── Main ───

def main():
    if not NOTION_API_KEY:
        print("❌ NOTION_API_KEY environment variable not set")
        sys.exit(1)

    print("=" * 50)
    print("Notion → Obsidian Migration")
    print(f"Vault: {VAULT_PATH}")
    print("=" * 50)
    print()

    total = 0
    total += migrate_books()
    print()
    total += migrate_media()
    print()
    total += migrate_ga4_curriculum()
    print()
    total += migrate_ga4_specs()
    print()

    print("=" * 50)
    print(f"🎉 Total migrated: {total} notes")
    print("=" * 50)


if __name__ == "__main__":
    main()
