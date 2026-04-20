#!/usr/bin/env python3
"""
Dataset Structure Validator
Analyzes local dataset before uploading to Google Drive
"""

import os
import json
from pathlib import Path
from collections import defaultdict

def count_images(folder_path):
    """Count images by extension."""
    extensions = defaultdict(int)
    total = 0
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in {'.heic', '.jpg', '.jpeg', '.png'}:
                extensions[ext] += 1
                total += 1
    
    return dict(extensions), total

def validate_structure(dataset_root):
    """Validate dataset folder structure."""
    print("\n" + "="*70)
    print("🔍 DATASET STRUCTURE VALIDATOR")
    print("="*70)
    
    dataset_path = Path(dataset_root)
    
    if not dataset_path.exists():
        print(f"\n❌ ERROR: Dataset folder not found: {dataset_root}")
        return False
    
    print(f"\n📁 Analyzing: {dataset_path}")
    
    # Expected structure
    required_diseases = {'healthy_leaves', 'panama_wilt', 'potassium_deficiency', 'sigatoka'}
    required_contributors = {'Vedant_Primary', 'Vedant_Secondary', 'Sagar', 'Subodh', 'Sudhanshu'}
    
    # Check disease folders
    print("\n📊 DISEASE FOLDERS:")
    disease_stats = {}
    
    for disease in sorted(required_diseases):
        disease_path = dataset_path / disease
        
        if disease_path.exists():
            print(f"  ✓ {disease}")
            
            # Check contributor subfolders
            contributor_stats = {}
            total_disease_images = 0
            
            for contrib in sorted(required_contributors):
                contrib_path = disease_path / contrib
                
                if contrib_path.exists():
                    extensions, count = count_images(contrib_path)
                    total_disease_images += count
                    
                    if count > 0:
                        ext_str = ", ".join([f"{ext}: {c}" for ext, c in sorted(extensions.items())])
                        print(f"    - {contrib}: {count} images ({ext_str})")
                        contributor_stats[contrib] = {
                            'count': count,
                            'extensions': extensions
                        }
                    else:
                        print(f"    - {contrib}: ⚠️  No images")
                else:
                    print(f"    - {contrib}: ❌ Missing folder")
            
            disease_stats[disease] = {
                'total': total_disease_images,
                'contributors': contributor_stats
            }
        else:
            print(f"  ❌ {disease} - MISSING")
    
    # Summary Statistics
    print("\n📈 SUMMARY STATISTICS:")
    
    total_images = sum(stats['total'] for stats in disease_stats.values())
    total_contributors = 0
    total_folders = 0
    extension_totals = defaultdict(int)
    
    for disease, stats in disease_stats.items():
        total_folders += len(stats['contributors'])
        total_contributors = len(stats['contributors'])
        for contrib, contrib_stats in stats['contributors'].items():
            for ext, count in contrib_stats['extensions'].items():
                extension_totals[ext] += count
    
    print(f"\n  Total images: {total_images}")
    print(f"  Total contributor folders: {total_folders}")
    print(f"\n  By file type:")
    for ext, count in sorted(extension_totals.items()):
        print(f"    - {ext.upper()}: {count} images ({count/total_images*100:.1f}%)")
    
    # Device distribution
    print(f"\n  Device distribution:")
    iphone_count = 0
    android_count = 0
    
    for disease, stats in disease_stats.items():
        for contrib, contrib_stats in stats['contributors'].items():
            if 'Vedant' in contrib:
                iphone_count += contrib_stats['count']
            else:
                android_count += contrib_stats['count']
    
    print(f"    - iPhone (Vedant_*): {iphone_count} images ({iphone_count/total_images*100:.1f}%)")
    print(f"    - Android (Sagar/Subodh/Sudhanshu): {android_count} images ({android_count/total_images*100:.1f}%)")
    
    # Disease distribution
    print(f"\n  By disease class:")
    for disease in sorted(disease_stats.keys()):
        count = disease_stats[disease]['total']
        if total_images > 0:
            print(f"    - {disease}: {count} images ({count/total_images*100:.1f}%)")
    
    # Quality checks
    print("\n✅ VALIDATION CHECKS:")
    
    all_good = True
    
    # Check 1: All disease folders exist
    missing_diseases = []
    for disease in required_diseases:
        if (dataset_path / disease).exists():
            print(f"  ✓ Disease folder '{disease}' exists")
        else:
            print(f"  ❌ Disease folder '{disease}' MISSING")
            missing_diseases.append(disease)
            all_good = False
    
    # Check 2: All contributor folders exist
    missing_contributors = []
    for disease, stats in disease_stats.items():
        for contrib in required_contributors:
            if contrib not in stats['contributors']:
                print(f"  ⚠️  Missing contributor '{contrib}' in '{disease}'")
                missing_contributors.append((disease, contrib))
                all_good = False
    
    # Check 3: All disease classes have images
    for disease, stats in disease_stats.items():
        if stats['total'] == 0:
            print(f"  ❌ Disease class '{disease}' has NO IMAGES")
            all_good = False
        elif stats['total'] < 10:
            print(f"  ⚠️  Disease class '{disease}' has very few images ({stats['total']})")
    
    # Check 4: File format support
    unsupported = defaultdict(int)
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in {'.heic', '.jpg', '.jpeg', '.png'}:
                unsupported[ext] += 1
    
    if unsupported:
        print(f"\n  ⚠️  Unsupported file formats found:")
        for ext, count in unsupported.items():
            print(f"    - {ext}: {count} files (won't be processed)")
    else:
        print(f"  ✓ All files use supported formats (HEIC/JPG/JPEG/PNG)")
    
    # Check 5: Total image count
    if total_images == 0:
        print(f"  ❌ NO IMAGES FOUND in dataset")
        all_good = False
    elif total_images < 50:
        print(f"  ⚠️  Very small dataset ({total_images} images)")
    else:
        print(f"  ✓ Dataset has {total_images} images (good size for training)")
    
    # Overall result
    print("\n" + "="*70)
    if all_good:
        print("✅ READY FOR UPLOAD - Structure looks good!")
    else:
        print("⚠️  STRUCTURE ISSUES - Review above for helpful hints")
    print("="*70)
    
    # Generate report
    report = {
        'total_images': total_images,
        'disease_classes': disease_stats,
        'device_distribution': {
            'iPhone': iphone_count,
            'Android': android_count
        },
        'file_types': dict(extension_totals),
        'validation_passed': all_good
    }
    
    return report

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1:
        dataset_root = sys.argv[1]
    else:
        # Try common locations
        possible_paths = [
            'dataset/raw',
            'dataset',
            './raw',
            os.path.expanduser('~/Desktop/MiniProject/dataset/raw'),
            os.getcwd()
        ]
        
        print("\n📁 COMMON DATASET LOCATIONS:")
        for i, path in enumerate(possible_paths, 1):
            exists = "✓" if Path(path).exists() else "✗"
            print(f"  {i}. {exists} {path}")
        
        dataset_root = input("\n📂 Enter path to dataset folder: ").strip()
        
        if not dataset_root:
            print("\n❌ No path provided. Exiting.")
            return
    
    # Validate the structure
    report = validate_structure(dataset_root)
    
    # Save report
    if report:
        report_file = Path(dataset_root).parent / 'dataset_validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to: {report_file}")

if __name__ == '__main__':
    main()
