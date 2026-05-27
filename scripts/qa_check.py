#!/usr/bin/env python3
"""
QA Check for SSS-Class Suicide Hunter data
Verifies JSON integrity and analysis completeness
"""

import json
import glob
from pathlib import Path
from collections import defaultdict


def check_json_files():
    """Check all JSON files for validity and consistency"""
    print("=" * 60)
    print("JSON FILE QA CHECK")
    print("=" * 60)
    
    json_files = sorted(Path("data/json").glob("chapter-*.json"))
    issues = []
    
    print(f"\nTotal JSON files: {len(json_files)}")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check required fields
            required_fields = ['chapter', 'title', 'content', 'metadata', 'annotations']
            for field in required_fields:
                if field not in data:
                    issues.append(f"{json_file.name}: Missing field '{field}'")
            
            # Check annotation fields
            if 'annotations' in data:
                annotation_fields = ['characters', 'events', 'locations', 'skills', 'deaths', 'loops', 'cause_effect']
                for field in annotation_fields:
                    if field not in data['annotations']:
                        issues.append(f"{json_file.name}: Missing annotation '{field}'")
                
                # Check if chapter has actual analysis data or is placeholder
                has_data = any(
                    len(data['annotations'].get(field, [])) > 0 
                    for field in annotation_fields
                )
                if not has_data:
                    issues.append(f"{json_file.name}: No analysis data (placeholder)")
                    
        except json.JSONDecodeError as e:
            issues.append(f"{json_file.name}: Invalid JSON - {e}")
        except Exception as e:
            issues.append(f"{json_file.name}: Error - {e}")
    
    print(f"Issues found: {len(issues)}")
    if issues:
        print("\nIssues:")
        for issue in issues[:20]:  # Show first 20
            print(f"  - {issue}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    else:
        print("No issues found!")
    
    return len(issues) == 0


def check_data_completeness():
    """Check data completeness statistics"""
    print("\n" + "=" * 60)
    print("DATA COMPLETENESS CHECK")
    print("=" * 60)
    
    json_files = sorted(Path("data/json").glob("chapter-*.json"))
    
    stats = {
        'total_chapters': len(json_files),
        'with_characters': 0,
        'with_events': 0,
        'with_deaths': 0,
        'with_loops': 0,
        'with_skills': 0,
        'total_characters': set(),
        'total_deaths': 0,
        'total_loops': 0,
    }
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('annotations'):
            ann = data['annotations']
            
            if ann.get('characters'):
                stats['with_characters'] += 1
                stats['total_characters'].update(ann['characters'])
            
            if ann.get('events'):
                stats['with_events'] += 1
            
            if ann.get('deaths'):
                stats['with_deaths'] += 1
                stats['total_deaths'] += len(ann['deaths'])
            
            if ann.get('loops'):
                stats['with_loops'] += 1
                stats['total_loops'] += len(ann['loops'])
            
            if ann.get('skills'):
                stats['with_skills'] += 1
    
    print(f"\nChapters with analysis:")
    print(f"  Characters: {stats['with_characters']}/{stats['total_chapters']} ({stats['with_characters']/stats['total_chapters']*100:.1f}%)")
    print(f"  Events: {stats['with_events']}/{stats['total_chapters']} ({stats['with_events']/stats['total_chapters']*100:.1f}%)")
    print(f"  Deaths: {stats['with_deaths']}/{stats['total_chapters']} ({stats['with_deaths']/stats['total_chapters']*100:.1f}%)")
    print(f"  Loops: {stats['with_loops']}/{stats['total_chapters']} ({stats['with_loops']/stats['total_chapters']*100:.1f}%)")
    print(f"  Skills: {stats['with_skills']}/{stats['total_chapters']} ({stats['with_skills']/stats['total_chapters']*100:.1f}%)")
    
    print(f"\nTotals:")
    print(f"  Unique characters: {len(stats['total_characters'])}")
    print(f"  Total deaths recorded: {stats['total_deaths']}")
    print(f"  Total loops recorded: {stats['total_loops']}")
    
    # Show sample characters
    if stats['total_characters']:
        print(f"\nSample characters: {', '.join(list(stats['total_characters'])[:10])}")


def check_consistency():
    """Check for data consistency issues"""
    print("\n" + "=" * 60)
    print("CONSISTENCY CHECK")
    print("=" * 60)
    
    issues = []
    json_files = sorted(Path("data/json").glob("chapter-*.json"))
    
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check chapter number matches filename
        chapter_num = int(json_file.stem.split('-')[1])
        if data.get('chapter') != chapter_num:
            issues.append(f"{json_file.name}: Chapter number mismatch ({data.get('chapter')} vs {chapter_num})")
        
        # Check for empty titles
        if not data.get('title'):
            issues.append(f"{json_file.name}: Empty title")
        
        # Check for empty content
        if not data.get('content'):
            issues.append(f"{json_file.name}: Empty content")
    
    print(f"\nConsistency issues: {len(issues)}")
    if issues:
        for issue in issues[:10]:
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("No consistency issues found!")
    
    return len(issues) == 0


def main():
    print("SSS-CLASS SUICIDE HUNTER - DATA QA CHECK")
    print("=" * 60)
    
    # Run checks
    json_ok = check_json_files()
    check_data_completeness()
    consistency_ok = check_consistency()
    
    print("\n" + "=" * 60)
    print("QA SUMMARY")
    print("=" * 60)
    print(f"JSON files valid: {'YES' if json_ok else 'NO'}")
    print(f"Consistency check: {'PASSED' if consistency_ok else 'FAILED'}")
    print(f"Overall: {'READY FOR DEPLOYMENT' if json_ok and consistency_ok else 'NEEDS ATTENTION'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
