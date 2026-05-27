#!/usr/bin/env python3
"""
Merge subagent analysis into chapter JSON files.
Reads batch result files and updates chapter JSON annotations.
"""

import json
from pathlib import Path
from datetime import datetime


def load_chapter_json(chapter_num: int) -> dict:
    """Load a chapter JSON file."""
    json_path = Path(f"data/json/chapter-{chapter_num:03d}.json")
    if not json_path.exists():
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_chapter_json(chapter_num: int, data: dict) -> None:
    """Save a chapter JSON file."""
    json_path = Path(f"data/json/chapter-{chapter_num:03d}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def merge_analysis(chapter_num: int, analysis: dict) -> bool:
    """Merge subagent analysis into chapter JSON."""
    data = load_chapter_json(chapter_num)
    if data is None:
        print(f"[SKIP] Chapter {chapter_num} JSON not found")
        return False
    
    # Update annotations with subagent data
    if 'annotations' not in data:
        data['annotations'] = {}
    
    # Map subagent fields to our annotation structure
    field_mapping = {
        'characters': 'characters',
        'events': 'events',
        'locations': 'locations',
        'skills': 'skills',
        'deaths': 'deaths',
        'loops': 'loops',
        'cause_effect': 'cause_effect',
        'notes': 'notes'
    }
    
    for source_field, target_field in field_mapping.items():
        if source_field in analysis and analysis[source_field]:
            if isinstance(analysis[source_field], list):
                # Merge lists, avoiding duplicates
                existing = set(data['annotations'].get(target_field, []))
                new_items = [item for item in analysis[source_field] if item not in existing]
                if target_field not in data['annotations']:
                    data['annotations'][target_field] = []
                data['annotations'][target_field].extend(new_items)
            else:
                data['annotations'][target_field] = analysis[source_field]
    
    # Add metadata about the merge
    if 'analysis_metadata' not in data:
        data['analysis_metadata'] = {}
    
    data['analysis_metadata']['merged_at'] = datetime.now().isoformat()
    data['analysis_metadata']['source'] = 'subagent_batch_analysis'
    
    save_chapter_json(chapter_num, data)
    print(f"[MERGED] Chapter {chapter_num} - {len(analysis.get('characters', []))} chars, {len(analysis.get('events', []))} events")
    return True


def process_batch_file(batch_path: Path) -> None:
    """Process a batch analysis file."""
    print(f"\nProcessing {batch_path.name}...")
    
    try:
        with open(batch_path, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)
        
        # Handle both formats: {"batch": X, "chapters": [...]} and [...]
        if isinstance(batch_data, list):
            batch_data = {'batch': int(batch_path.stem.split('-')[1]), 'chapters': batch_data}
        
        if 'chapters' not in batch_data:
            print(f"[SKIP] No chapters found in {batch_path.name}")
            return
        
        print(f"  Found {len(batch_data['chapters'])} chapters in {batch_path.name}")
        
        success_count = 0
        skip_count = 0
        for chapter_analysis in batch_data['chapters']:
            if 'chapter' not in chapter_analysis:
                continue
            
            chapter_num = chapter_analysis['chapter']
            
            # Skip placeholder data
            if chapter_analysis.get('notes') == 'Placeholder - needs detailed analysis':
                skip_count += 1
                continue
            
            if merge_analysis(chapter_num, chapter_analysis):
                success_count += 1
        
        print(f"[DONE] Merged {success_count} chapters, skipped {skip_count} placeholders from {batch_path.name}")
        
    except Exception as e:
        print(f"[ERROR] Failed to process {batch_path.name}: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    print("=" * 60)
    print("MERGING SUBAGENT ANALYSIS INTO CHAPTER JSON FILES")
    print("=" * 60)
    
    batch_dir = Path("data/batch_results")
    if not batch_dir.exists():
        print(f"[ERROR] Batch results directory not found: {batch_dir}")
        return
    
    batch_files = sorted(batch_dir.glob("batch-*.json"))
    
    if not batch_files:
        print(f"[ERROR] No batch files found in {batch_dir}")
        return
    
    print(f"Found {len(batch_files)} batch files to process\n")
    
    total_merged = 0
    total_placeholder = 0
    for batch_file in batch_files:
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
            
            # Handle both formats: {"batch": X, "chapters": [...]} and [...]
            if isinstance(batch_data, list):
                batch_data = {'chapters': batch_data}
            
            if 'chapters' not in batch_data:
                continue
            
            for chapter_analysis in batch_data['chapters']:
                if 'chapter' not in chapter_analysis:
                    continue
                
                chapter_num = chapter_analysis['chapter']
                
                # Skip placeholder data
                if chapter_analysis.get('notes') == 'Placeholder - needs detailed analysis':
                    total_placeholder += 1
                    continue
                
                if merge_analysis(chapter_num, chapter_analysis):
                    total_merged += 1
            
        except Exception as e:
            print(f"[ERROR] Failed to process {batch_file.name}: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"MERGE COMPLETE")
    print(f"Total merged: {total_merged} chapters")
    print(f"Total placeholders: {total_placeholder} chapters")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
