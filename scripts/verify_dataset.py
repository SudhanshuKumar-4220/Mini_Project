"""
Dataset Verification Script.

This script verifies dataset quality and identifies potential issues.

Usage:
    python scripts/verify_dataset.py

Checks:
- Image integrity
- Class distribution balance
- Device distribution balance
- Quality metrics
- Cross-device validation readiness
"""

import sys
import logging
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import config
from src.metadata_generator import MetadataAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_metadata_exists():
    """Check if metadata CSV exists."""
    if not config.METADATA_CSV.exists():
        logger.error(f"Metadata CSV not found: {config.METADATA_CSV}")
        logger.error("Please run run_pipeline.py first")
        return False
    return True


def load_metadata():
    """Load metadata from CSV."""
    try:
        df = pd.read_csv(config.METADATA_CSV)
        logger.info(f"Loaded {len(df)} image records")
        return df
    except Exception as e:
        logger.error(f"Failed to load metadata: {e}")
        return None


def verify_dataset_quality(metadata_df):
    """Verify overall dataset quality."""
    logger.info("\n" + "=" * 70)
    logger.info("DATASET QUALITY VERIFICATION")
    logger.info("=" * 70)
    
    # Quality statistics
    total = len(metadata_df)
    quality_count = metadata_df["is_quality"].sum()
    quality_rate = (quality_count / total * 100) if total > 0 else 0
    
    logger.info(f"\nQuality Check Results:")
    logger.info(f"  Total images: {total}")
    logger.info(f"  Quality images: {quality_count} ({quality_rate:.1f}%)")
    logger.info(f"  Rejected images: {total - quality_count}")
    
    # Quality metrics
    if "blur_score" in metadata_df.columns:
        logger.info(f"\nBlur Score Statistics:")
        logger.info(f"  Mean: {metadata_df['blur_score'].mean():.2f}")
        logger.info(f"  Min: {metadata_df['blur_score'].min():.2f}")
        logger.info(f"  Max: {metadata_df['blur_score'].max():.2f}")
        logger.info(f"  Threshold: {config.BLUR_THRESHOLD}")
    
    if "brightness_score" in metadata_df.columns:
        logger.info(f"\nBrightness Score Statistics:")
        logger.info(f"  Mean: {metadata_df['brightness_score'].mean():.2f}")
        logger.info(f"  Min: {metadata_df['brightness_score'].min():.2f}")
        logger.info(f"  Max: {metadata_df['brightness_score'].max():.2f}")
        logger.info(f"  Range: [{config.MIN_BRIGHTNESS}, {config.MAX_BRIGHTNESS}]")
    
    return quality_rate > 80  # Warning if <80% quality


def verify_class_balance(metadata_df):
    """Verify disease class distribution."""
    logger.info("\n" + "=" * 70)
    logger.info("CLASS DISTRIBUTION VERIFICATION")
    logger.info("=" * 70)
    
    class_counts = metadata_df["disease_class"].value_counts()
    total = len(metadata_df)
    
    logger.info(f"\nDisease Class Distribution:")
    for disease, count in class_counts.items():
        pct = (count / total * 100)
        logger.info(f"  {disease}: {count} ({pct:.1f}%)")
    
    # Check for imbalance
    if len(class_counts) > 1:
        max_count = class_counts.max()
        min_count = class_counts.min()
        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
        
        logger.warning(f"\nClass Imbalance Ratio: {imbalance_ratio:.2f}x")
        
        if imbalance_ratio > 3:
            logger.warning("  [!] HIGH IMBALANCE - Model may overfit to majority class")
            return False
    
    return True


def verify_device_distribution(metadata_df):
    """Verify device type distribution."""
    logger.info("\n" + "=" * 70)
    logger.info("DEVICE DISTRIBUTION VERIFICATION")
    logger.info("=" * 70)
    
    if "device_type" not in metadata_df.columns:
        logger.warning("Device type information not available")
        return True
    
    device_counts = metadata_df["device_type"].value_counts()
    total = len(metadata_df)
    
    logger.info(f"\nDevice Distribution:")
    for device, count in device_counts.items():
        pct = (count / total * 100)
        logger.info(f"  {device}: {count} ({pct:.1f}%)")
    
    # Check for device-class bias
    logger.info(f"\nDisease by Device Cross-tabulation:")
    cross_tab = pd.crosstab(metadata_df["device_type"], metadata_df["disease_class"])
    logger.info(cross_tab)
    
    if len(device_counts) > 1:
        max_dev = device_counts.max()
        min_dev = device_counts.min()
        device_imbalance = max_dev / min_dev if min_dev > 0 else float('inf')
        
        if device_imbalance > 3:
            logger.warning(f"  [!] High device imbalance: {device_imbalance:.2f}x")
            return False
    
    return True


def verify_splits(metadata_df):
    """Verify train/val/test splits."""
    logger.info("\n" + "=" * 70)
    logger.info("DATASET SPLIT VERIFICATION")
    logger.info("=" * 70)
    
    splits_csv = config.METADATA_DIR / "splits.csv"
    
    if splits_csv.exists():
        try:
            splits_df = pd.read_csv(splits_csv)
            
            split_counts = splits_df["split_assignment"].value_counts()
            total = len(splits_df)
            
            logger.info(f"\nSplit Distribution:")
            for split, count in split_counts.items():
                pct = (count / total * 100)
                logger.info(f"  {split}: {count} ({pct:.1f}%)")
            
            # Verify target ratios
            target_train = config.TRAIN_RATIO * 100
            target_val = config.VAL_RATIO * 100
            target_test = config.TEST_RATIO * 100
            
            logger.info(f"\nTarget Ratios:")
            logger.info(f"  Train: {target_train:.1f}%")
            logger.info(f"  Val: {target_val:.1f}%")
            logger.info(f"  Test: {target_test:.1f}%")
            
            return True
        except Exception as e:
            logger.error(f"Error reading splits: {e}")
            return False
    else:
        logger.warning(f"Splits file not found: {splits_csv}")
        return False


def detect_potential_issues(metadata_df):
    """Detect potential dataset issues."""
    logger.info("\n" + "=" * 70)
    logger.info("POTENTIAL ISSUES DETECTION")
    logger.info("=" * 70)
    
    issues = MetadataAnalyzer.detect_potential_issues(metadata_df)
    
    if not issues:
        logger.info("\n[✓] No major issues detected!")
    else:
        logger.warning(f"\n[!] {len(issues)} potential issues detected:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"  {i}. {issue}")
    
    return len(issues) == 0


def main():
    """Run dataset verification."""
    logger.info("=" * 80)
    logger.info("BANANA LEAF DATASET VERIFICATION")
    logger.info("=" * 80)
    
    # Check metadata exists
    if not verify_metadata_exists():
        return False
    
    # Load metadata
    metadata_df = load_metadata()
    if metadata_df is None:
        return False
    
    # Run all verifications
    quality_ok = verify_dataset_quality(metadata_df)
    class_ok = verify_class_balance(metadata_df)
    device_ok = verify_device_distribution(metadata_df)
    splits_ok = verify_splits(metadata_df)
    no_issues = detect_potential_issues(metadata_df)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 80)
    
    results = {
        "Quality": quality_ok,
        "Class Balance": class_ok,
        "Device Distribution": device_ok,
        "Splits": splits_ok,
        "No Major Issues": no_issues
    }
    
    for check, passed in results.items():
        status = "[✓]" if passed else "[!]"
        logger.info(f"  {status} {check}")
    
    all_ok = all(results.values())
    
    logger.info("\n" + "=" * 80)
    if all_ok:
        logger.info("DATASET READY FOR MODEL TRAINING!")
    else:
        logger.warning("DATASET HAS ISSUES - REVIEW ABOVE WARNINGS")
    logger.info("=" * 80)
    
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
