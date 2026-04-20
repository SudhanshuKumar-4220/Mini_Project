"""
Bias Analysis and Detection Script.

Analyzes dataset for potential biases that could lead to:
- Model learning device characteristics instead of disease patterns
- Unfair class representation
- Contributor bias
- Cross-device performance degradation

Usage:
    python scripts/analyze_bias.py
"""

import sys
import logging
import pandas as pd
import numpy as np
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


def analyze_device_bias(metadata_df):
    """
    Analyze for device-specific bias.
    
    WHY: If model learns "iPhone = healthy, Android = diseased",
    it will fail in real-world deployment.
    """
    logger.info("\n" + "=" * 70)
    logger.info("DEVICE BIAS ANALYSIS")
    logger.info("=" * 70)
    
    if "device_type" not in metadata_df.columns:
        logger.info("Device information not available")
        return
    
    # Check if disease strongly correlates with device
    device_disease = pd.crosstab(
        metadata_df["device_type"],
        metadata_df["disease_class"],
        normalize="index"
    )
    
    logger.info("\nDisease distribution within each device:")
    logger.info(device_disease)
    
    # Check variance - if one device always has same disease, bias exists
    variance_by_device = device_disease.var(axis=1)
    logger.info(f"\nVariance in disease distribution by device:")
    for device, var in variance_by_device.items():
        logger.info(f"  {device}: {var:.4f} (lower = more bias)")
    
    # Look for extreme patterns
    logger.info(f"\nBias Risk Assessment:")
    for device in device_disease.index:
        max_disease_pct = device_disease.loc[device].max()
        min_disease_pct = device_disease.loc[device].min()
        
        if max_disease_pct > 0.6:
            logger.warning(f"  [!] {device}: {max_disease_pct*100:.1f}% of one disease type")
            logger.warning(f"      -> Model may learn device characteristics")


def analyze_contributor_bias(metadata_df):
    """
    Analyze for contributor/photographer bias.
    
    WHY: If one person took all photos of diseased leaves,
    model might learn photography style instead of disease.
    """
    logger.info("\n" + "=" * 70)
    logger.info("CONTRIBUTOR BIAS ANALYSIS")
    logger.info("=" * 70)
    
    if "contributor_name" not in metadata_df.columns:
        logger.info("Contributor information not available")
        return
    
    # Check contributor-disease correlation
    contrib_disease = pd.crosstab(
        metadata_df["contributor_name"],
        metadata_df["disease_class"],
        normalize="index"
    )
    
    logger.info("\nDisease distribution by contributor:")
    logger.info(contrib_disease)
    
    # Check how much each contributor concentrates on one disease
    logger.info(f"\nContributor Specialization Analysis:")
    for contrib in contrib_disease.index:
        max_pct = contrib_disease.loc[contrib].max()
        num_diseases = (contrib_disease.loc[contrib] > 0).sum()
        
        logger.info(f"  {contrib}:")
        logger.info(f"    Max concentration: {max_pct*100:.1f}%")
        logger.info(f"    Disease types: {num_diseases}/{len(contrib_disease.columns)}")
        
        if max_pct > 0.6 and num_diseases < len(contrib_disease.columns):
            logger.warning(f"    [!] Biased toward specific diseases/conditions")


def analyze_quality_bias(metadata_df):
    """
    Analyze if quality metrics differ by device/contributor.
    
    WHY: If one device produces blurrier images, model might
    learn to degrade quality instead of recognizing disease.
    """
    logger.info("\n" + "=" * 70)
    logger.info("QUALITY BIAS ANALYSIS")
    logger.info("=" * 70)
    
    if "blur_score" not in metadata_df.columns:
        logger.info("Blur score information not available")
        return
    
    # Quality by device
    if "device_type" in metadata_df.columns:
        logger.info("\nBlur Score by Device:")
        device_blur = metadata_df.groupby("device_type")["blur_score"].agg([
            "mean", "std", "min", "max"
        ])
        logger.info(device_blur)
        
        blur_range = device_blur["max"] - device_blur["min"]
        if blur_range.max() > 100:
            logger.warning("  [!] Large device difference in blur scores")
            logger.warning("      Device sensors or lighting conditions differ significantly")
    
    # Quality by contributor
    if "contributor_name" in metadata_df.columns:
        logger.info("\nBlur Score by Contributor:")
        contrib_blur = metadata_df.groupby("contributor_name")["blur_score"].agg([
            "mean", "std", "min", "max"
        ])
        logger.info(contrib_blur)
        
        mean_blur = contrib_blur["mean"]
        if mean_blur.max() - mean_blur.min() > 50:
            logger.warning("  [!] Contributors have significantly different blur profiles")
            logger.warning("      Some photographers may be less skilled or using different techniques")


def analyze_class_representation(metadata_df):
    """
    Analyze if classes are evenly represented across subgroups.
    """
    logger.info("\n" + "=" * 70)
    logger.info("CLASS REPRESENTATION ANALYSIS")
    logger.info("=" * 70)
    
    # Overall class counts
    class_counts = metadata_df["disease_class"].value_counts(normalize=True)
    
    logger.info("\nOverall class distribution:")
    for disease, pct in class_counts.items():
        logger.info(f"  {disease}: {pct*100:.1f}%")
    
    # Expected for balanced dataset
    expected_pct = 100.0 / len(class_counts)
    logger.info(f"\nIdeal balanced: {expected_pct:.1f}% per class")
    
    # Check device-specific class distribution
    if "device_type" in metadata_df.columns:
        logger.info("\nClass representation by device:")
        for device in metadata_df["device_type"].unique():
            device_data = metadata_df[metadata_df["device_type"] == device]
            device_classes = device_data["disease_class"].value_counts(normalize=True)
            
            logger.info(f"\n  {device} ({len(device_data)} images):")
            for disease, pct in device_classes.items():
                expected_count = len(device_data) * class_counts[disease]
                actual_count = (device_data["disease_class"] == disease).sum()
                variance = abs(actual_count - expected_count) / expected_count if expected_count > 0 else 0
                
                deviation = "✓" if variance < 0.2 else "[!]"
                logger.info(f"    {deviation} {disease}: {pct*100:.1f}% ({actual_count} images)")
                
                if variance > 0.3:
                    logger.warning(
                        f"      Significant deviation from expected {class_counts[disease]*100:.1f}%"
                    )


def check_cross_device_readiness(metadata_df):
    """
    Check if dataset is ready for cross-device validation.
    """
    logger.info("\n" + "=" * 70)
    logger.info("CROSS-DEVICE VALIDATION READINESS")
    logger.info("=" * 70)
    
    devices = metadata_df["device_type"].unique()
    logger.info(f"\nNumber of devices: {len(devices)}")
    
    if len(devices) < 2:
        logger.warning("[!] Only one device type - cannot perform cross-device validation")
        return False
    
    logger.info(f"Devices: {', '.join(devices)}")
    
    # Check if each class has samples from each device
    logger.info("\nClass-Device Coverage:")
    for disease in metadata_df["disease_class"].unique():
        disease_data = metadata_df[metadata_df["disease_class"] == disease]
        covered_devices = disease_data["device_type"].unique()
        coverage = len(covered_devices) / len(devices) * 100
        
        logger.info(f"  {disease}: {len(covered_devices)}/{len(devices)} devices ({coverage:.0f}%)")
        
        if len(covered_devices) < len(devices):
            missing = set(devices) - set(covered_devices)
            logger.warning(f"    Missing: {', '.join(missing)}")
    
    return len(devices) >= 2


def generate_bias_report(metadata_df):
    """Generate comprehensive bias report."""
    logger.info("\n" + "=" * 100)
    logger.info("COMPREHENSIVE BIAS REPORT")
    logger.info("=" * 100)
    
    # Run all analyses
    analyze_device_bias(metadata_df)
    analyze_contributor_bias(metadata_df)
    analyze_quality_bias(metadata_df)
    analyze_class_representation(metadata_df)
    cross_device_ready = check_cross_device_readiness(metadata_df)
    
    # Summary recommendations
    logger.info("\n" + "=" * 100)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 100)
    
    logger.info("""
To minimize bias and ensure robust model:

1. CROSS-DEVICE TESTING (CRITICAL):
   - Always train on one device type and test on another
   - If cross-device accuracy < within-device accuracy, bias detected
   - Example: Train on Android 80% accuracy, test on iPhone 72% accuracy
   - This 8% drop indicates model learned phone characteristics

2. CLASS BALANCE:
   - Ensure each disease type is well-represented from all devices
   - Avoid one device having all "healthy" samples

3. CONTRIBUTOR BALANCE:
   - Different photographers have different techniques
   - Ensure each disease type photographed by multiple contributors
   - Prevents model from learning photography style instead of disease

4. QUALITY CONSISTENCY:
   - Different devices/photographers may have different image quality
   - Model should learn disease patterns, not quality artifacts

5. DATA COLLECTION STRATEGY:
   - Collect more data from underrepresented device/contributor combinations
   - Use similar camera settings across all contributors
   - Take multiple photos of same leaf from different angles
    """)


def main():
    """Run bias analysis."""
    logger.info("=" * 100)
    logger.info("BANANA LEAF DISEASE DATASET - BIAS ANALYSIS")
    logger.info("=" * 100)
    
    # Load metadata
    metadata_csv = config.METADATA_CSV
    
    if not metadata_csv.exists():
        logger.error(f"Metadata CSV not found: {metadata_csv}")
        logger.error("Please run run_pipeline.py first")
        return False
    
    try:
        metadata_df = pd.read_csv(metadata_csv)
        logger.info(f"Loaded {len(metadata_df)} image records")
    except Exception as e:
        logger.error(f"Failed to load metadata: {e}")
        return False
    
    # Generate comprehensive report
    generate_bias_report(metadata_df)
    
    logger.info("\n" + "=" * 100)
    logger.info("BIAS ANALYSIS COMPLETE")
    logger.info("=" * 100)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
