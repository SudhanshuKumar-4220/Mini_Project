"""
Main Preprocessing Pipeline - Orchestrates complete preprocessing workflow.

This module coordinates:
- Image discovery and loading
- Format conversion
- Quality checking
- Duplicate detection
- Metadata generation
- Dataset splitting
"""

import logging
from pathlib import Path
from typing import Dict
import pandas as pd

from config import config
from src.utils import FileManager, ImageProcessor, setup_logging
from src.quality_checker import QualityChecker, ImageQualityValidator
from src.duplicate_detection import DuplicateDetector, DuplicateRemover
from src.metadata_generator import MetadataGenerator, MetadataAnalyzer
from src.dataset_splitter import DatasetSplitter

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """Main preprocessing orchestration class."""
    
    def __init__(self):
        """Initialize preprocessing pipeline."""
        self.config = config
        self.file_manager = FileManager()
        self.image_processor = ImageProcessor(
            target_size=config.TARGET_IMAGE_SIZE,
            jpeg_quality=config.JPEG_QUALITY
        )
        self.quality_checker = QualityChecker(
            blur_threshold=config.BLUR_THRESHOLD,
            min_brightness=config.MIN_BRIGHTNESS,
            max_brightness=config.MAX_BRIGHTNESS,
            min_contrast=config.MIN_CONTRAST
        )
        self.quality_validator = ImageQualityValidator(self.quality_checker)
        self.duplicate_detector = DuplicateDetector(
            hash_size=config.HASH_SIZE,
            algorithm=config.HASH_ALGORITHM,
            threshold=config.DUPLICATE_THRESHOLD
        )
        self.metadata_generator = MetadataGenerator()
        self.metadata_analyzer = MetadataAnalyzer()
        self.dataset_splitter = DatasetSplitter(
            random_seed=config.RANDOM_SEED
        )
        
        # Setup logging
        setup_logging(config.LOG_FILE if config.VERBOSE else None)
    
    def run_full_pipeline(self, source_drive_path: str):
        """
        Execute complete preprocessing pipeline.
        
        Steps:
        1. Discover images
        2. Check and report statistics
        3. Process images (format conversion, resizing)
        4. Quality check and filtering
        5. Duplicate detection and removal
        6. Metadata generation
        7. Dataset splitting
        8. Cross-device validation preparation
        
        Args:
            source_drive_path (str): Path to Mini_Project_Dataset on Google Drive
            
        Returns:
            bool: Success status
        """
        logger.info("=" * 70)
        logger.info("STARTING BANANA LEAF DISEASE PREPROCESSING PIPELINE")
        logger.info("=" * 70)
        
        try:
            # Step 1: Discover images
            logger.info("\n[STEP 1] Discovering images from Google Drive...")
            images_structure = self.discover_images(source_drive_path)
            summary = FileManager.get_image_summary(images_structure)
            logger.info(f"Found {summary['total_images']} images")
            logger.info(f"Disease breakdown: {summary['diseases']}")
            
            # Step 2: Create output directories
            logger.info("\n[STEP 2] Creating output directory structure...")
            self.setup_output_directories()
            
            # Step 3: Process images
            logger.info("\n[STEP 3] Processing images (format conversion, resizing)...")
            all_images_flat = FileManager.get_all_images_flat_list(images_structure)
            
            processed_count = 0
            failed_count = 0
            
            for i, (image_path, disease_class, contributor) in enumerate(all_images_flat):
                if i % 50 == 0:
                    logger.info(f"Progress: {i}/{len(all_images_flat)}")
                
                success = self.process_single_image(
                    image_path, disease_class, contributor
                )
                
                if success:
                    processed_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"Processed: {processed_count}, Failed: {failed_count}")
            
            # Step 4: Quality filtering
            logger.info("\n[STEP 4] Quality checking and filtering...")
            metadata_df = self.metadata_generator.get_metadata_dataframe()
            quality_stats = self.quality_checker.generate_quality_report(
                metadata_df[["is_quality", "blur_score", "brightness_score", "contrast_score"]].to_dict('records')
            )
            logger.info(f"Quality images: {quality_stats['quality_images']}/{len(metadata_df)}")
            
            # Filter to quality only
            quality_metadata = metadata_df[metadata_df["is_quality"] == True].reset_index(drop=True)
            logger.info(f"Retaining {len(quality_metadata)} quality images")
            
            # Step 5: Duplicate detection
            logger.info("\n[STEP 5] Detecting duplicate images...")
            duplicates = self.detect_duplicates(quality_metadata)
            logger.info(f"Found {len(duplicates['duplicate_groups'])} duplicate groups")
            
            # Step 6: Dataset splitting
            logger.info("\n[STEP 6] Splitting dataset...")
            splits = self.split_dataset(quality_metadata)
            
            # Step 7: Cross-device validation
            logger.info("\n[STEP 7] Creating cross-device validation splits...")
            cross_device_splits = self.dataset_splitter.create_cross_device_splits(
                quality_metadata
            )
            
            # Save all results
            logger.info("\n[STEP 8] Saving results...")
            self.save_results(quality_metadata, duplicates, splits)
            
            # Generate reports
            logger.info("\n[STEP 9] Generating analysis reports...")
            self.generate_reports(quality_metadata)
            
            logger.info("\n" + "=" * 70)
            logger.info("PREPROCESSING PIPELINE COMPLETE!")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return False
    
    def discover_images(self, source_path: str) -> Dict:
        """
        Discover all images in source directory.
        
        Args:
            source_path (str): Path to dataset root
            
        Returns:
            dict: Discovered images structure
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            logger.error(f"Source path does not exist: {source_path}")
            return {}
        
        images = FileManager.discover_images(source_path, self.config.DISEASE_CLASSES)
        return images
    
    def setup_output_directories(self):
        """Create output folder structure."""
        # Create base directories
        for directory in [
            self.config.RAW_DATASET_DIR,
            self.config.PROCESSED_DATASET_DIR,
            self.config.SPLIT_DATASET_DIR,
            self.config.METADATA_DIR
        ]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create per-disease folders
        FileManager.create_disease_class_folders(
            self.config.PROCESSED_DATASET_DIR,
            self.config.DISEASE_CLASSES
        )
        
        logger.info("Output directories created")
    
    def process_single_image(self, image_path, disease_class, contributor):
        """
        Process single image through standardization pipeline.
        
        Args:
            image_path (Path): Image file path
            disease_class (str): Disease classification
            contributor (str): Contributor name
            
        Returns:
            bool: Success status
        """
        try:
            image_path = Path(image_path)
            device_type = self.config.DEVICE_MAPPING.get(contributor, "Unknown")
            original_format = image_path.suffix.lstrip('.')
            
            # Get file size
            original_size_mb = FileManager.get_file_size_mb(image_path)
            
            # Load and validate image
            is_valid, image_array, quality_report = self.quality_validator.validate_image_file(
                image_path
            )
            
            # Standardize image
            standardized_image, success = self.image_processor.standardize_image(
                image_path,
                correct_orientation=True,
                normalize=False
            )
            
            if not success:
                # Create failed metadata record
                self.metadata_generator.create_metadata_record(
                    image_name=image_path.name,
                    disease_class=disease_class,
                    contributor_name=contributor,
                    device_type=device_type,
                    original_path=str(image_path),
                    original_format=original_format,
                    original_size_mb=original_size_mb,
                    processing_status="failed",
                    quality_issues="Could not standardize image"
                )
                return False
            
            # Save processed image
            output_filename = image_path.stem + ".jpg"
            output_path = (
                self.config.PROCESSED_DATASET_DIR / disease_class / output_filename
            )
            
            save_success = self.image_processor.save_image(
                standardized_image,
                output_path,
                format="JPEG",
                quality=self.config.JPEG_QUALITY
            )
            
            if not save_success:
                self.metadata_generator.create_metadata_record(
                    image_name=image_path.name,
                    disease_class=disease_class,
                    contributor_name=contributor,
                    device_type=device_type,
                    original_path=str(image_path),
                    original_format=original_format,
                    original_size_mb=original_size_mb,
                    processing_status="failed",
                    quality_issues="Could not save processed image"
                )
                return False
            
            # Calculate processed file size
            processed_size_mb = FileManager.get_file_size_mb(output_path)
            
            # Create metadata record
            status = "processed" if is_valid else "processed_quality_issue"
            
            self.metadata_generator.create_metadata_record(
                image_name=image_path.name,
                disease_class=disease_class,
                contributor_name=contributor,
                device_type=device_type,
                original_path=str(image_path),
                original_format=original_format,
                original_size_mb=original_size_mb,
                processed_path=str(output_path),
                processed_format="JPEG",
                processed_size_mb=processed_size_mb,
                quality_report=quality_report,
                processing_status=status
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")
            return False
    
    def detect_duplicates(self, metadata_df):
        """
        Detect duplicate images in dataset.
        
        Args:
            metadata_df (pd.DataFrame): Metadata of processed images
            
        Returns:
            dict: Duplicate detection results
        """
        # Get all processed image paths
        image_paths = metadata_df["processed_path"].dropna().tolist()
        
        if not image_paths:
            logger.warning("No processed images found")
            return {"duplicate_groups": [], "duplicate_count": 0}
        
        # Find duplicates
        results = self.duplicate_detector.find_duplicates_in_batch(image_paths)
        
        # Mark duplicates in metadata
        duplicate_ids = []
        for group_idx, group in enumerate(results["duplicate_groups"]):
            duplicate_ids.extend(group)
        
        metadata_df["is_duplicate"] = metadata_df["processed_path"].isin(duplicate_ids)
        
        return results
    
    def split_dataset(self, metadata_df):
        """
        Split dataset into train/val/test.
        
        Args:
            metadata_df (pd.DataFrame): Metadata of images
            
        Returns:
            dict: Split assignments
        """
        if self.config.BALANCE_DEVICE_DISTRIBUTION:
            splits = self.dataset_splitter.device_aware_split(
                metadata_df,
                train_ratio=self.config.TRAIN_RATIO,
                val_ratio=self.config.VAL_RATIO,
                test_ratio=self.config.TEST_RATIO,
                balance_devices=True
            )
        else:
            splits = self.dataset_splitter.stratified_split(
                metadata_df,
                train_ratio=self.config.TRAIN_RATIO,
                val_ratio=self.config.VAL_RATIO,
                test_ratio=self.config.TEST_RATIO
            )
        
        return splits
    
    def save_results(self, metadata_df, duplicates, splits):
        """
        Save all results to disk.
        
        Args:
            metadata_df (pd.DataFrame): Metadata dataframe
            duplicates (dict): Duplicate detection results
            splits (dict): Split assignments
        """
        # Save metadata CSV
        self.metadata_generator.save_metadata_csv(self.config.METADATA_CSV)
        
        # Save splits
        split_df = self.dataset_splitter.assign_splits(metadata_df, splits)
        split_df.to_csv(
            self.config.METADATA_DIR / "splits.csv",
            index=False
        )
        
        logger.info(f"Results saved to {self.config.METADATA_DIR}")
    
    def generate_reports(self, metadata_df):
        """
        Generate analysis and bias reports.
        
        Args:
            metadata_df (pd.DataFrame): Metadata dataframe
        """
        # Generate statistics
        stats = self.metadata_generator.get_statistics()
        logger.info(f"Dataset statistics: {stats}")
        
        # Analyze potential issues
        issues = MetadataAnalyzer.detect_potential_issues(metadata_df)
        if issues:
            logger.warning("Potential dataset issues detected:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        
        # Cross-device distribution
        device_dist = MetadataAnalyzer.analyze_device_distribution(metadata_df)
        logger.info(f"Device distribution: {device_dist}")


if __name__ == "__main__":
    # Example usage
    pipeline = PreprocessingPipeline()
    success = pipeline.run_full_pipeline("/path/to/Mini_Project_Dataset")
