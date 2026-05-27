# SSS-Class Suicide Hunter - Timeline Site Redesign Plan

## Problem
Current site shows raw text per chapter. Need rich visualizations for:
- Multi-loop timeline (branches for each regression)
- Character tracking (alive/dead status per loop)
- Death records with causes
- Floor progression grid
- Character relationship network
- Search/filter

## Implementation Plan

### Phase 1: Data Enhancement (5 min)
- Create loop detection from chapter annotations
- Build character database with appearances per loop
- Extract floor progression data
- Build death records with chapter references

### Phase 2: Visual Timeline (15 min)
- Horizontal timeline with chapters on X-axis
- Different colors for different loops/arcs
- Death markers (red dots)
- Loop markers (gold diamonds)
- Floor progression indicators
- Chapter cards on click/hover

### Phase 3: Character Dashboard (10 min)
- Character list with status badges
- Filter by alive/dead/unknown
- Appearance frequency
- Death count per character
- Relationship indicators

### Phase 4: Death Records (10 min)
- Visual death log
- Group by character or chapter
- Death cause analysis
- Loop context for each death

### Phase 5: Floor Grid (5 min)
- Grid: Floors × Loops
- Chapter density visualization
- Progress indicators

### Phase 6: Network Graph (15 min)
- D3.js force-directed graph
- Character nodes
- Relationship edges (co-appearance)
- Death connections
- Filter by chapter range

### Phase 7: Search & Filter (5 min)
- Real-time search
- Filter by type (character, event, death, skill)
- Chapter range slider
- Loop filter

## Tech Stack
- Keep Astro static site
- Add D3.js for network graph
- Custom CSS for timeline
- No external frameworks (keep it lightweight)

## Data Structure Enhancements
```javascript
// loops.js - Extracted from annotations
const loops = [
  {
    id: "loop-1",
    name: "Initial Timeline",
    startChapter: 1,
    endChapter: 5,
    description: "Kim's original timeline before any regressions",
    deaths: [
      { chapter: 3, character: "Kim Gongja", cause: "Burned by Flame Emperor" },
      { chapter: 3, character: "Saintess", cause: "Burned by Flame Emperor" }
    ],
    keyEvents: ["Skill awakening", "First death"]
  },
  {
    id: "loop-2", 
    name: "24h Regression",
    startChapter: 4,
    endChapter: 6,
    parentLoop: "loop-1",
    divergenceChapter: 4,
    description: "First regression - 24 hours back",
    deaths: [
      { chapter: 5, character: "Kim Gongja", cause: "Suicide x4091", type: "self" },
      { chapter: 6, character: "Kim Gongja", cause: "Sword Saint's test" }
    ]
  }
  // ... more loops
];

// characters.js
const characters = [
  {
    id: "kim-gongja",
    name: "Kim Gongja",
    aliases: ["Death King"],
    firstAppearance: 1,
    status: "alive",
    deaths: 15,  // total across all loops
    skills: ["I Want To Become Just Like You", "Returner's Clockwork Watch"],
    loopStatus: {
      "loop-1": "dead",
      "loop-2": "dead",
      "loop-3": "alive"
    }
  }
];

// floors.js
const floors = [
  { number: 1, chapters: [1, 2, 3], loops: ["loop-1", "loop-2"] },
  { number: 10, chapters: [50, 51, 52], loops: ["loop-5"] }
];
```

## UI Layout
```
[Header]
[Tab Bar: Timeline | Characters | Deaths | Floors | Network]
[Search Bar + Filters]
[Main Content Area]
[Stats Footer]
```

## Timeline View Layout
```
Time →
|----|----|----|----|----|----|----|----|
Loop 1 ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
       💀 Ch.3 (Kim, Saintess)

Loop 2 ░░████░░░░░░░░░░░░░░░░░░░░░░░░░░░░
       💀 Ch.5 (Kim x4091)
       💀 Ch.6 (Kim - Sword Saint)
       
Loop 3 ░░░░████████░░░░░░░░░░░░░░░░░░░░░░
       💀 Ch.8 (Kim - Flame Emperor)
       ✨ Ch.10 (New skill acquired)
```

## File Changes
1. `site/src/pages/index.astro` - Complete rewrite with new components
2. `site/public/js/data-processor.js` - Data enhancement
3. `site/public/js/timeline.js` - Timeline visualization
4. `site/public/js/characters.js` - Character dashboard
5. `site/public/js/deaths.js` - Death records
6. `site/public/js/floors.js` - Floor grid
7. `site/public/js/network.js` - Network graph (D3.js)
8. `site/public/js/search.js` - Search/filter

## Key Features Per View

### Timeline View
- Horizontal scrollable timeline
- Loop lanes (each loop is a row)
- Chapter markers
- Death indicators (red dots with hover details)
- Loop markers (gold diamonds)
- Floor transitions (vertical lines)
- Click chapter for details popup

### Characters View
- Grid of character cards
- Status: Alive (green), Dead (red), Unknown (gray)
- Death count badge
- First appearance chapter
- Click for character detail modal
- Filter by status, sort by deaths/appearances

### Deaths View
- Chronological death log
- Visual timeline with deaths
- Group by: Character, Chapter, Cause
- Death type: Murder, Suicide, Natural, Skill-related
- Statistics: Total deaths, most killed character, etc.

### Floors View
- Grid: Rows = Floors, Cols = Loops
- Cell color intensity = chapter count
- Hover shows chapters in that floor/loop
- Click for chapter list

### Network View
- D3.js force-directed graph
- Nodes = Characters (sized by appearances)
- Edges = Co-appearances (thicker = more co-appearances)
- Color = Character status
- Death connections = dashed red lines
- Zoom, pan, drag
- Filter by loop, chapter range

## Success Criteria
- [ ] Timeline shows loop branches visually
- [ ] Characters have alive/dead status per loop
- [ ] Deaths are visualized with causes
- [ ] Floor grid shows progression
- [ ] Network graph shows relationships
- [ ] Search works across all data
- [ ] Mobile responsive
- [ ] Loads under 5 seconds
