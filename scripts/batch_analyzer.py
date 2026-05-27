#!/usr/bin/env python3
"""
SSS-Class Suicide Hunter - Batch Chapter Analyzer
Prepares batches of chapters for subagent analysis.
"""

import json
import glob
from pathlib import Path
from datetime import datetime


def load_chapter_md(chapter_num: int) -> dict:
    """Load a chapter markdown file and extract content."""
    md_path = Path(f"data/md/chapter-{chapter_num:03d}.md")
    if not md_path.exists():
        return None
    
    content = md_path.read_text(encoding="utf-8")
    
    # Split frontmatter and content
    parts = content.split("---", 2)
    if len(parts) >= 3:
        frontmatter = parts[1].strip()
        body = parts[2].strip()
    else:
        frontmatter = ""
        body = content
    
    # Parse basic info from frontmatter
    chapter_info = {"chapter": chapter_num, "body": body}
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in ["chapter", "title", "word_count"]:
                if key == "chapter":
                    chapter_info[key] = int(value)
                elif key == "word_count":
                    chapter_info[key] = int(value)
                else:
                    chapter_info[key] = value
    
    return chapter_info


def create_batch(chapters: list[int]) -> str:
    """Create analysis prompt for a batch of chapters."""
    batch_data = []
    for ch_num in chapters:
        ch = load_chapter_md(ch_num)
        if ch:
            batch_data.append(ch)
    
    # Format as analysis input
    output = []
    output.append("# SSS-Class Suicide Hunter - Chapter Batch Analysis")
    output.append(f"\nBatch contains chapters: {', '.join(map(str, chapters))}")
    output.append(f"Analysis date: {datetime.now().isoformat()}")
    output.append("\n" + "="*60)
    
    for ch in batch_data:
        output.append(f"\n## Chapter {ch['chapter']}: {ch.get('title', 'Unknown')}")
        output.append(f"Word count: {ch.get('word_count', 0)}")
        output.append("\n### Content:\n")
        # Limit content length to avoid overwhelming the analyzer
        body = ch['body']
        if len(body) > 5000:
            body = body[:5000] + "\n\n[... content truncated for analysis ...]"
        output.append(body)
        output.append("\n" + "-"*60)
    
    return "\n".join(output)


def save_batch_prompt(batch_num: int, chapters: list[int], prompt: str) -> None:
    """Save batch prompt to file."""
    batch_dir = Path("data/batches")
    batch_dir.mkdir(exist_ok=True)
    
    output_path = batch_dir / f"batch-{batch_num:03d}.md"
    output_path.write_text(prompt, encoding="utf-8")
    print(f"Saved batch {batch_num}: chapters {chapters[0]}-{chapters[-1]} ({len(chapters)} chapters)")


def main():
    # Configuration
    batch_size = 15
    total_chapters = 404
    
    print(f"Preparing batches of {batch_size} chapters (total: {total_chapters})")
    print(f"Output directory: data/batches/")
    print()
    
    batch_num = 1
    for start in range(1, total_chapters + 1, batch_size):
        end = min(start + batch_size - 1, total_chapters)
        chapters = list(range(start, end + 1))
        
        prompt = create_batch(chapters)
        save_batch_prompt(batch_num, chapters, prompt)
        
        batch_num += 1
    
    print(f"\nCreated {batch_num - 1} batch files for analysis")


if __name__ == "__main__":
    main()
