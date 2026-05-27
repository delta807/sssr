#!/usr/bin/env python3
"""
Process SSS-Class Suicide Hunter chapters 241-404
Extract structured data for timeline tracking
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

# Known characters/aliases for better extraction
KNOWN_CHARACTERS = {
    'Kim Gong-ja', 'Gong-ja', 'Kim Yul', 'Yul', 'Raviel Ivansia', 'Raviel',
    'Sylvia Evanail', 'Sylvia', 'Lady of Golden Silk', 'Lady of Silver Lily',
    'Bae Hu-ryeong', 'Sword Emperor', 'Zombie', 'Ja Soo-jung',
    'Estelle', 'Uburka', 'Blood Demon', 'Yoo Soo-ha', 'Soo-ha',
    'Director', 'Master', 'Hamustra', 'Crown Prince', 'Emperor',
    'Moon of Ivansia', 'Flower of High Society', 'Silver Tyrant',
    'Apostle of the Ox that Harvests Ruins', 'Constellation',
    'Musclehead Who Dreams of Sinning Against Heaven',
    'Devil King', 'Demon Lord', 'Four Demon Lords'
}

# Known skills/abilities
KNOWN_SKILLS = {
    'Earth Bone Dragon\'s Box', 'Hundred Ghosts Reincarnation',
    'Infernal Heavens Demonic Art', 'Infernal Heavens Formation',
    'Constellation', 'SSS-Class', 'regression', 'regressor',
    'aura', 'apostle', 'demigod', 'Hundred Ghosts'
}

# Known locations
KNOWN_LOCATIONS = {
    'Tower', 'Ivansia', 'Empire', 'Seosan', 'Imperial Palace',
    'Duke Family', 'Silver Bells Social Club', 'courtyard', 'hall'
}

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown"""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2].strip()
            
            # Parse simple YAML
            fm = {}
            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('[') and value.endswith(']'):
                        fm[key] = []
                    else:
                        try:
                            fm[key] = int(value)
                        except:
                            fm[key] = value
            return fm, body
    return {}, content

def extract_characters(text):
    """Extract character names from text"""
    characters = set()
    
    # Check for known characters
    for char in KNOWN_CHARACTERS:
        if char in text:
            characters.add(char)
    
    # Extract names with titles
    patterns = [
        r'(?:Young Miss|Lady|Lord|Sir|Master|Family Head|Daddy|Father|Daughter|Son) ([A-Z][a-z]+)',
        r'([A-Z][a-z]+) (?:Ivansia|Evanail)',
        r'His (?:Majesty|Highness) the (?:Emperor|Crown Prince)',
        r'(?:The )?(?:Lady|Lord) of (?:Silver Lily|Golden Silk)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = ' '.join(match)
            characters.add(match)
    
    return sorted(list(characters))

def extract_events(text):
    """Extract key plot events"""
    events = []
    
    # Look for action patterns
    event_patterns = [
        (r'(?:killed|died|death|murdered|slain)', 'Death/Murder'),
        (r'(?:skill activated|skill acquired|learned|obtained)', 'Skill Acquisition'),
        (r'(?:battle|fought|clashed|attacked|defended)', 'Battle'),
        (r'(?:revelation|revealed|discovered|learned that|realized)', 'Revelation'),
        (r'(?:apologized|forgave|reconciled)', 'Emotional Resolution'),
        (r'(?:resurrected|revived|came back to life)', 'Resurrection'),
        (r'(?:confessed|declared|proposed|accepted)', 'Declaration/Proposal'),
    ]
    
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        sentence = sentence.strip()
        for pattern, event_type in event_patterns:
            if re.search(pattern, sentence, re.IGNORECASE) and len(sentence) > 20:
                # Clean up the sentence
                clean = sentence.replace('\n', ' ').strip()
                if clean and clean not in events:
                    events.append(clean)
                break
    
    return events[:10]  # Limit to 10 most relevant

def extract_locations(text):
    """Extract locations mentioned"""
    locations = set()
    
    for loc in KNOWN_LOCATIONS:
        if loc in text:
            locations.add(loc)
    
    # Pattern for locations
    loc_patterns = [
        r'(?:in|at|to|from) the ([A-Z][a-z]+ (?:Palace|Hall|Tower|Court|Garden|Village|City|Empire|Kingdom))',
        r'(?:in|at|to|from) ([A-Z][a-z]+ (?:Palace|Hall|Tower|Court|Garden|Village|City|Empire|Kingdom))',
    ]
    
    for pattern in loc_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            locations.add(match)
    
    return sorted(list(locations))

def extract_skills(text):
    """Extract skills/abilities mentioned"""
    skills = set()
    
    for skill in KNOWN_SKILLS:
        if skill in text:
            skills.add(skill)
    
    # Pattern for skill mentions
    skill_patterns = [
        r'\[(.*?)\]',
        r'(?:skill|ability|power|art|technique|magic) called [\"\']([^\"\']+)[\"\']',
        r'(?:the|a|an) ([A-Z][a-z]+ (?:Art|Technique|Skill|Magic|Power|Ability))',
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = ' '.join(match)
            if len(match) > 2 and len(match) < 100:
                skills.add(match)
    
    return sorted(list(skills))

def extract_deaths(text):
    """Extract death descriptions"""
    deaths = []
    
    death_patterns = [
        r'[^.!?]*(?:died|death|killed|murdered|slain|executed|perished)[^.!?]*[.!?]',
        r'[^.!?]*(?:lost (?:his|her|their) life)[^.!?]*[.!?]',
    ]
    
    for pattern in death_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean = match.strip().replace('\n', ' ')
            if clean and clean not in deaths:
                deaths.append(clean)
    
    return deaths[:5]

def extract_loops(text):
    """Extract time loop/regression events"""
    loops = []
    
    loop_patterns = [
        r'[^.!?]*(?:regression|regressor|repeating|loop|cycle|returned to the past|went back)[^.!?]*[.!?]',
        r'[^.!?]*(?:first life|previous life|past life|lives before)[^.!?]*[.!?]',
        r'[^.!?]*(?:eternal repetition|repeating life|time loop)[^.!?]*[.!?]',
    ]
    
    for pattern in loop_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean = match.strip().replace('\n', ' ')
            if clean and clean not in loops:
                loops.append(clean)
    
    return loops[:5]

def extract_cause_effect(text):
    """Extract cause-effect relationships"""
    cause_effects = []
    
    ce_patterns = [
        r'[^.!?]*(?:because|since|as a result|therefore|thus|led to|caused|resulted in)[^.!?]*[.!?]',
        r'[^.!?]*(?:if.*then|when.*resulted|after.*before)[^.!?]*[.!?]',
    ]
    
    for pattern in ce_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean = match.strip().replace('\n', ' ')
            if len(clean) > 30 and clean not in cause_effects:
                cause_effects.append(clean)
    
    return cause_effects[:5]

def process_chapter(chapter_num):
    """Process a single chapter and return structured data"""
    filepath = f'/Users/laptop/Projects/shows/sssr/data/md/chapter-{chapter_num:03d}.md'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None
    
    fm, body = extract_frontmatter(content)
    
    # Extract all elements
    chapter_data = {
        "chapter": chapter_num,
        "characters": extract_characters(body),
        "events": extract_events(body),
        "locations": extract_locations(body),
        "skills": extract_skills(body),
        "deaths": extract_deaths(body),
        "loops": extract_loops(body),
        "cause_effect": extract_cause_effect(body),
        "notes": f"Word count: {fm.get('word_count', 'N/A')}. " + 
                 ("Contains significant character development." if len(body) > 3000 else "Standard chapter length.")
    }
    
    return chapter_data

def process_batch(batch_num, start_chapter, end_chapter):
    """Process a batch of chapters and save to JSON"""
    chapters = []
    
    for ch_num in range(start_chapter, end_chapter + 1):
        data = process_chapter(ch_num)
        if data:
            chapters.append(data)
            print(f"  Processed chapter {ch_num}")
        else:
            print(f"  Missing chapter {ch_num}")
    
    batch_data = {
        "batch": batch_num,
        "chapters": chapters
    }
    
    output_path = f'/Users/laptop/Projects/shows/sssr/data/batch_results/batch-{batch_num:03d}.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved batch {batch_num} with {len(chapters)} chapters to {output_path}")
    return batch_data

if __name__ == '__main__':
    # Define batches
    batches = [
        (17, 241, 255),
        (18, 256, 270),
        (19, 271, 285),
        (20, 286, 300),
        (21, 301, 315),
        (22, 316, 330),
        (23, 331, 345),
        (24, 346, 360),
        (25, 361, 375),
        (26, 376, 390),
        (27, 391, 404),
    ]
    
    for batch_num, start, end in batches:
        print(f"\nProcessing batch {batch_num} (chapters {start}-{end})...")
        process_batch(batch_num, start, end)
    
    print("\nAll batches processed!")
