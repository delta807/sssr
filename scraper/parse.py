#!/usr/bin/env python3
"""
SSS-Class Suicide Hunter - Chapter Parser
Parses raw HTML into structured JSON, Markdown, and CSV formats.
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup


class ChapterParser:
    def __init__(
        self,
        raw_dir: str = "data/raw",
        json_dir: str = "data/json",
        md_dir: str = "data/md",
        csv_path: str = "data/csv/timeline.csv",
    ):
        self.raw_dir = Path(raw_dir)
        self.json_dir = Path(json_dir)
        self.md_dir = Path(md_dir)
        self.csv_path = Path(csv_path)
        
        # Create output directories
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.md_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV if it doesn't exist
        self._init_csv()
    
    def _init_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "chapter",
                    "title",
                    "word_count",
                    "characters",
                    "events",
                    "source_url",
                    "parsed_at",
                ])
    
    def parse_chapter(self, chapter_num: int) -> dict[str, Any] | None:
        """Parse a single chapter HTML file into structured data."""
        raw_path = self.raw_dir / f"chapter-{chapter_num:03d}.html"
        
        if not raw_path.exists():
            print(f"[SKIP] Chapter {chapter_num} raw file not found")
            return None
        
        html = raw_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "lxml")
        
        # Extract chapter info
        chapter_title = self._extract_title(soup)
        content = self._extract_content(soup)
        word_count = len(content.split())
        
        data = {
            "chapter": chapter_num,
            "title": chapter_title,
            "content": content,
            "metadata": {
                "word_count": word_count,
                "character_count": len(content),
                "source_url": f"https://novelfire.net/book/sss-class-suicide-hunter/chapter-{chapter_num}",
                "parsed_at": datetime.now().isoformat(),
            },
            "annotations": {
                "characters": [],
                "events": [],
                "locations": [],
                "skills": [],
                "deaths": [],
                "loops": [],
                "cause_effect": [],
                "notes": "",
            },
        }
        
        return data
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract chapter title from HTML."""
        # Try multiple selectors
        selectors = [
            "h1 .chapter-title",
            ".chapter-title",
            "h1 span:last-child",
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                # Clean up title
                title = re.sub(r'^Chapter\s+\d+\s*[-–]\s*', '', title)
                return title
        
        # Fallback to page title
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text()
            # Extract just the chapter title part
            match = re.search(r'Chapter\s+\d+\s*[-–]\s*(.+?)(?:\s*-\s*Novel|$)', title)
            if match:
                return match.group(1).strip()
            return title.strip()
        
        return f"Chapter {chapter_num}"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract chapter content text from HTML."""
        content_div = soup.select_one("#content")
        if not content_div:
            return ""
        
        # Get text from all paragraphs
        paragraphs = content_div.find_all("p")
        texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        
        return "\n\n".join(texts)
    
    def save_json(self, data: dict[str, Any]) -> None:
        """Save chapter data as JSON."""
        output_path = self.json_dir / f"chapter-{data['chapter']:03d}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  [JSON] Saved: {output_path}")
    
    def save_markdown(self, data: dict[str, Any]) -> None:
        """Save chapter data as Markdown with YAML frontmatter."""
        output_path = self.md_dir / f"chapter-{data['chapter']:03d}.md"
        
        # YAML frontmatter
        frontmatter = {
            "chapter": data["chapter"],
            "title": data["title"],
            "word_count": data["metadata"]["word_count"],
            "character_count": data["metadata"]["character_count"],
            "source_url": data["metadata"]["source_url"],
            "parsed_at": data["metadata"]["parsed_at"],
            "characters": data["annotations"]["characters"],
            "events": data["annotations"]["events"],
            "locations": data["annotations"]["locations"],
            "skills": data["annotations"]["skills"],
            "deaths": data["annotations"]["deaths"],
            "loops": data["annotations"]["loops"],
            "cause_effect": data["annotations"]["cause_effect"],
        }
        
        yaml_lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                if value:
                    yaml_lines.append(f"{key}:")
                    for item in value:
                        yaml_lines.append(f"  - {item}")
                else:
                    yaml_lines.append(f"{key}: []")
            else:
                yaml_lines.append(f"{key}: {value}")
        yaml_lines.append("---")
        
        # Content body
        content = data["content"]
        
        markdown = "\n".join(yaml_lines) + "\n\n" + content + "\n"
        
        output_path.write_text(markdown, encoding="utf-8")
        print(f"  [MD] Saved: {output_path}")
    
    def append_csv(self, data: dict[str, Any]) -> None:
        """Append chapter data to CSV."""
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                data["chapter"],
                data["title"],
                data["metadata"]["word_count"],
                json.dumps(data["annotations"]["characters"]),
                json.dumps(data["annotations"]["events"]),
                data["metadata"]["source_url"],
                data["metadata"]["parsed_at"],
            ])
        print(f"  [CSV] Appended row for chapter {data['chapter']}")
    
    def process_chapter(self, chapter_num: int) -> bool:
        """Process a single chapter: parse and save all formats."""
        print(f"\n[Process] Chapter {chapter_num}")
        
        data = self.parse_chapter(chapter_num)
        if data is None:
            return False
        
        self.save_json(data)
        self.save_markdown(data)
        self.append_csv(data)
        
        return True
    
    def process_range(self, start: int, end: int) -> None:
        """Process a range of chapters."""
        print(f"\n{'='*60}")
        print(f"Processing chapters {start}-{end}")
        print(f"Output: JSON={self.json_dir}, MD={self.md_dir}, CSV={self.csv_path}")
        print(f"{'='*60}")
        
        success = 0
        failed = 0
        
        for chapter in range(start, end + 1):
            if self.process_chapter(chapter):
                success += 1
            else:
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"PROCESSING COMPLETE")
        print(f"Success: {success}, Failed: {failed}")
        print(f"{'='*60}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse SSS-Class Suicide Hunter chapters")
    parser.add_argument("--start", type=int, default=1, help="Start chapter (default: 1)")
    parser.add_argument("--end", type=int, default=404, help="End chapter (default: 404)")
    args = parser.parse_args()
    
    chapter_parser = ChapterParser()
    chapter_parser.process_range(args.start, args.end)


if __name__ == "__main__":
    main()
