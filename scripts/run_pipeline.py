"""
Main Pipeline Execution Script.

This script runs the complete preprocessing pipeline for the Banana Leaf Disease dataset.

Usage:
    python scripts/run_pipeline.py

For Google Colab, modify the MOUNT_POINT in config.py and run this script.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import config
from src.preprocessing import PreprocessingPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Execute preprocessing pipeline."""
    
    logger.info("=" * 80)
    logger.info("BANANA LEAF DISEASE PREPROCESSING PIPELINE")
    logger.info("=" * 80)
    
    # Determine dataset path based on environment
    if config.IS_COLAB:
        dataset_path = config.MOUNT_POINT
        logger.info(f"Running in Google Colab mode")
    else:
        # For local development, use a test path or prompt user
        dataset_path = input("Enter path to Mini_Project_Dataset: ").strip()
    
    dataset_path = Path(dataset_path)
    
    if not dataset_path.exists():
        logger.error(f"Dataset path does not exist: {dataset_path}")
        return False
    
    logger.info(f"Dataset path: {dataset_path}")
    
    # Verify configuration
    logger.info("\nConfiguration:")
    logger.info(f"  Target image size: {config.TARGET_IMAGE_SIZE}")
    logger.info(f"  Target format: {config.TARGET_IMAGE_FORMAT}")
    logger.info(f"  Blur threshold: {config.BLUR_THRESHOLD}")
    logger.info(f"  Duplicate threshold: {config.DUPLICATE_THRESHOLD}")
    logger.info(f"  Split ratios: {config.TRAIN_RATIO}/{config.VAL_RATIO}/{config.TEST_RATIO}")
    logger.info(f"  Random seed: {config.RANDOM_SEED}")
    
    # Run pipeline
    logger.info("\nStarting preprocessing pipeline...\n")
    
    pipeline = PreprocessingPipeline()
    success = pipeline.run_full_pipeline(str(dataset_path))
    
    if success:
        logger.info("\n" + "=" * 80)
        logger.info("PREPROCESSING COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"\nResults saved to: {config.METADATA_DIR}")
        logger.info(f"  - Metadata CSV: {config.METADATA_CSV}")
        logger.info(f"  - Processed images: {config.PROCESSED_DATASET_DIR}")
        logger.info(f"  - Split data: {config.SPLIT_DATASET_DIR}")
    else:
        logger.error("\n" + "=" * 80)
        logger.error("PREPROCESSING FAILED!")
        logger.error("=" * 80)
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
