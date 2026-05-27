#!/usr/bin/env python3
"""
SSS-Class Suicide Hunter - Chapter Scraper
Rate-limited HTTP fetcher with retry logic and resume capability.
"""

import time
import random
import json
import os
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class ChapterScraper:
    BASE_URL = "https://novelfire.net/book/sss-class-suicide-hunter"
    
    def __init__(
        self,
        output_dir: str = "data/raw",
        delay_min: float = 3.0,
        delay_max: float = 5.0,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_retries = max_retries
        self.timeout = timeout
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
        })
        
        self.stats = {
            "total": 0,
            "success": 0,
            "skipped": 0,
            "failed": 0,
            "start_time": None,
            "end_time": None,
        }
    
    def _sleep(self):
        """Random delay between requests to avoid rate limiting."""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)
    
    def _fetch(self, url: str, retries: int = 0) -> str | None:
        """Fetch URL with exponential backoff retry."""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            if retries < self.max_retries:
                wait = 2 ** retries + random.uniform(0, 1)
                print(f"  Retry {retries + 1}/{self.max_retries} after {wait:.1f}s: {e}")
                time.sleep(wait)
                return self._fetch(url, retries + 1)
            else:
                print(f"  Failed after {self.max_retries} retries: {e}")
                return None
    
    def _get_output_path(self, chapter: int) -> Path:
        """Get output path for a chapter."""
        return self.output_dir / f"chapter-{chapter:03d}.html"
    
    def chapter_exists(self, chapter: int) -> bool:
        """Check if chapter was already downloaded."""
        path = self._get_output_path(chapter)
        return path.exists() and path.stat().st_size > 1000
    
    def scrape_chapter(self, chapter: int) -> bool:
        """Scrape a single chapter. Returns True if successful."""
        self.stats["total"] += 1
        
        if self.chapter_exists(chapter):
            print(f"[SKIP] Chapter {chapter} already downloaded")
            self.stats["skipped"] += 1
            return True
        
        url = f"{self.BASE_URL}/chapter-{chapter}"
        
        self._sleep()
        html = self._fetch(url)
        
        if html is None:
            self.stats["failed"] += 1
            return False
        
        # Save raw HTML
        output_path = self._get_output_path(chapter)
        output_path.write_text(html, encoding="utf-8")
        
        self.stats["success"] += 1
        print(f"[OK] Chapter {chapter} saved ({len(html):,} bytes)")
        return True
    
    def scrape_range(self, start: int, end: int) -> None:
        """Scrape a range of chapters."""
        self.stats["start_time"] = datetime.now().isoformat()
        print(f"\n{'='*60}")
        print(f"Scraping chapters {start}-{end}")
        print(f"Output: {self.output_dir.absolute()}")
        print(f"Delay: {self.delay_min}-{self.delay_max}s between requests")
        print(f"{'='*60}\n")
        
        for chapter in range(start, end + 1):
            self.scrape_chapter(chapter)
            print()
        
        self.stats["end_time"] = datetime.now().isoformat()
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print scrape summary."""
        print(f"\n{'='*60}")
        print("SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total:     {self.stats['total']}")
        print(f"Success:   {self.stats['success']}")
        print(f"Skipped:   {self.stats['skipped']}")
        print(f"Failed:    {self.stats['failed']}")
        print(f"Started:   {self.stats['start_time']}")
        print(f"Ended:     {self.stats['end_time']}")
        print(f"{'='*60}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scrape SSS-Class Suicide Hunter chapters")
    parser.add_argument("--start", type=int, default=1, help="Start chapter (default: 1)")
    parser.add_argument("--end", type=int, default=404, help="End chapter (default: 404)")
    parser.add_argument("--delay-min", type=float, default=3.0, help="Minimum delay in seconds")
    parser.add_argument("--delay-max", type=float, default=5.0, help="Maximum delay in seconds")
    args = parser.parse_args()
    
    scraper = ChapterScraper(delay_min=args.delay_min, delay_max=args.delay_max)
    scraper.scrape_range(args.start, args.end)


if __name__ == "__main__":
    main()
