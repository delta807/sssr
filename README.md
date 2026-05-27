# SSS-Class Suicide Hunter - Timeline Tracker

A static site for tracking the complex timeline, characters, and events in the Korean novel **SSS-Class Suicide Hunter**.

## Features

### Timeline Views
1. **Branch Timeline** - Git-style vertical timeline showing chapter progression with loop and death markers
2. **Network Graph** - Character relationship visualization showing connections between characters across chapters
3. **Floor Grid** - Matrix view showing floor progression across different time loops

### Data Tracking
- Characters and aliases
- Key plot events (deaths, skill acquisitions, battles, revelations)
- Floor/level progression in the Tower
- Time loop/regression events
- Cause-effect chains

## Architecture

```
├── scraper/           # Python scraper for novelfire.net
│   ├── scrape.py     # Rate-limited HTTP fetcher
│   ├── parse.py      # HTML parser (JSON/Markdown/CSV output)
│   └── requirements.txt
├── data/             # Scraped and parsed data
│   ├── raw/          # Verbatim HTML
│   ├── json/         # Structured JSON per chapter
│   ├── md/           # Markdown with YAML frontmatter
│   └── csv/          # Aggregated timeline.csv
├── site/             # Astro static site
│   ├── src/
│   │   ├── layouts/
│   │   └── pages/
│   └── public/data/  # Chapter JSON files
└── .github/workflows/# GitHub Actions deployment
```

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 20+

### Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r scraper/requirements.txt
   ```

2. **Install Node dependencies:**
   ```bash
   cd site
   npm install
   ```

3. **Scrape chapters (optional - data already included):**
   ```bash
   python scraper/scrape.py --start 1 --end 404
   python scraper/parse.py --start 1 --end 404
   ```

4. **Copy data to site:**
   ```bash
   cp data/json/*.json site/public/data/
   ```

5. **Run development server:**
   ```bash
   cd site
   npm run dev
   ```

6. **Build for production:**
   ```bash
   cd site
   npm run build
   ```

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when pushing to the `main` branch.

### Manual Deployment

1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Push to main branch or trigger workflow manually

## Data Format

### JSON Structure
```json
{
  "chapter": 1,
  "title": "1 - The Greatest Envy",
  "content": "...",
  "metadata": {
    "word_count": 2311,
    "source_url": "https://novelfire.net/..."
  },
  "annotations": {
    "characters": ["Kim Gongja", "Flame Emperor"],
    "events": ["Kim discovers S-rank skill"],
    "locations": ["Kim's apartment"],
    "skills": ["I want to become just like you (S+)"],
    "deaths": [],
    "loops": [],
    "cause_effect": ["Kim's envy → awakens skill"]
  }
}
```

## License

Personal project for tracking SSS-Class Suicide Hunter novel content.
