"""
Metadata Generation Module - Track image information and processing.

This module generates and maintains metadata about:
- Individual image properties
- Processing status and results
- Disease classification
- Device/contributor information
- Quality scores
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MetadataGenerator:
    """Generate and manage image metadata tracking."""
    
    # Standard metadata columns
    REQUIRED_COLUMNS = [
        "image_id",           # Unique identifier
        "image_name",         # Original filename
        "disease_class",      # Disease classification
        "contributor_name",   # Who collected the image
        "device_type",        # iPhone / Android
        "original_path",      # Original file location
        "original_format",    # Original file format
        "original_size_mb",   # Original file size
        "processed_path",     # New file location
        "processed_format",   # Format after processing
        "processed_size_mb",  # Size after processing
        "is_quality",         # Passed quality checks
        "blur_score",         # Laplacian variance
        "brightness_score",   # Average pixel brightness
        "contrast_score",     # Pixel value standard deviation
        "is_duplicate",       # Is duplicate of another image
        "duplicate_group_id", # ID of duplicate group if applicable
        "processing_status",  # "processed" / "failed" / "rejected"
        "quality_issues",     # Description of quality problems
        "split_assignment",   # "train" / "val" / "test" / "unassigned"
        "timestamp",          # When metadata was created
    ]
    
    def __init__(self):
        """Initialize MetadataGenerator."""
        self.metadata_list = []
        self.image_counter = 0
    
    def create_metadata_record(
        self,
        image_name: str,
        disease_class: str,
        contributor_name: str,
        device_type: str,
        original_path: str,
        original_format: str = None,
        original_size_mb: float = None,
        processed_path: str = None,
        processed_format: str = None,
        processed_size_mb: float = None,
        quality_report: Dict = None,
        is_duplicate: bool = False,
        duplicate_group_id: str = None,
        processing_status: str = "processing",
        quality_issues: str = ""
    ) -> Dict[str, Any]:
        """
        Create metadata record for single image.
        
        WHY: Maintains complete history of each image.
        Enables debugging, analysis, and audit trail.
        
        Args:
            image_name (str): Original filename
            disease_class (str): Disease classification
            contributor_name (str): Data contributor
            device_type (str): Device type (iPhone/Android)
            original_path (str): Original file path
            original_format (str): Original file format
            original_size_mb (float): Original file size
            processed_path (str): Processed file path (can be added later)
            processed_format (str): Output format
            processed_size_mb (float): Output file size
            quality_report (dict): Quality check results
            is_duplicate (bool): Whether image is duplicate
            duplicate_group_id (str): ID of duplicate group
            processing_status (str): Current processing status
            quality_issues (str): Description of issues
            
        Returns:
            dict: Complete metadata record
        """
        self.image_counter += 1
        image_id = f"IMG_{self.image_counter:06d}"
        
        # Extract quality metrics from report
        blur_score = None
        brightness_score = None
        contrast_score = None
        is_quality = True
        quality_issues_list = []
        
        if quality_report:
            blur_score = quality_report.get("blur_score")
            brightness_score = quality_report.get("brightness")
            contrast_score = quality_report.get("contrast")
            is_quality = quality_report.get("is_quality", False)
            quality_issues_list = quality_report.get("flags", [])
        
        if quality_issues:
            quality_issues_list.append(quality_issues)
        
        record = {
            "image_id": image_id,
            "image_name": image_name,
            "disease_class": disease_class,
            "contributor_name": contributor_name,
            "device_type": device_type,
            "original_path": str(original_path),
            "original_format": original_format or Path(original_path).suffix.lstrip('.'),
            "original_size_mb": original_size_mb or 0.0,
            "processed_path": str(processed_path) if processed_path else None,
            "processed_format": processed_format,
            "processed_size_mb": processed_size_mb or 0.0,
            "is_quality": is_quality,
            "blur_score": blur_score,
            "brightness_score": brightness_score,
            "contrast_score": contrast_score,
            "is_duplicate": is_duplicate,
            "duplicate_group_id": duplicate_group_id,
            "processing_status": processing_status,
            "quality_issues": "; ".join(quality_issues_list) if quality_issues_list else "",
            "split_assignment": "unassigned",
            "timestamp": datetime.now().isoformat()
        }
        
        self.metadata_list.append(record)
        return record
    
    def update_record(self, image_id: str, updates: Dict) -> bool:
        """
        Update existing metadata record.
        
        Args:
            image_id (str): Image ID to update
            updates (dict): Fields to update
            
        Returns:
            bool: Success status
        """
        for record in self.metadata_list:
            if record["image_id"] == image_id:
                record.update(updates)
                return True
        
        logger.warning(f"Record not found: {image_id}")
        return False
    
    def get_metadata_dataframe(self) -> pd.DataFrame:
        """
        Get all metadata as pandas DataFrame.
        
        Returns:
            pd.DataFrame: Metadata table
        """
        if not self.metadata_list:
            return pd.DataFrame(columns=self.REQUIRED_COLUMNS)
        
        df = pd.DataFrame(self.metadata_list)
        
        # Ensure all required columns exist
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = None
        
        return df[self.REQUIRED_COLUMNS]
    
    def save_metadata_csv(self, output_path: str) -> bool:
        """
        Save metadata to CSV file.
        
        Args:
            output_path (str or Path): Output CSV file path
            
        Returns:
            bool: Success status
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df = self.get_metadata_dataframe()
            df.to_csv(output_path, index=False)
            
            logger.info(f"Saved metadata to: {output_path}")
            logger.info(f"Total records: {len(df)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return False
    
    def load_metadata_csv(self, input_path: str) -> bool:
        """
        Load metadata from CSV file.
        
        Args:
            input_path (str or Path): Input CSV file path
            
        Returns:
            bool: Success status
        """
        try:
            input_path = Path(input_path)
            
            df = pd.read_csv(input_path)
            self.metadata_list = df.to_dict('records')
            
            logger.info(f"Loaded {len(self.metadata_list)} records from {input_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Generate statistics about dataset.
        
        Returns:
            dict: Dataset statistics
        """
        if not self.metadata_list:
            return {"total_images": 0}
        
        df = self.get_metadata_dataframe()
        
        stats = {
            "total_images": len(df),
            "quality_images": df["is_quality"].sum(),
            "quality_rate": (df["is_quality"].sum() / len(df) * 100) if len(df) > 0 else 0,
            "duplicate_count": df["is_duplicate"].sum(),
            "by_disease": df.groupby("disease_class").size().to_dict(),
            "by_device": df.groupby("device_type").size().to_dict(),
            "by_contributor": df.groupby("contributor_name").size().to_dict(),
            "processing_status": df.groupby("processing_status").size().to_dict(),
        }
        
        return stats
    
    def get_split_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about train/val/test split.
        
        Returns:
            dict: Split statistics
        """
        df = self.get_metadata_dataframe()
        
        stats = {
            "total": len(df),
            "train": len(df[df["split_assignment"] == "train"]),
            "val": len(df[df["split_assignment"] == "val"]),
            "test": len(df[df["split_assignment"] == "test"]),
            "unassigned": len(df[df["split_assignment"] == "unassigned"])
        }
        
        # Add percentages
        total = stats["total"]
        if total > 0:
            stats["train_pct"] = (stats["train"] / total * 100)
            stats["val_pct"] = (stats["val"] / total * 100)
            stats["test_pct"] = (stats["test"] / total * 100)
        
        return stats


class MetadataAnalyzer:
    """Analyze metadata for insights and potential issues."""
    
    @staticmethod
    def analyze_device_distribution(metadata_df: pd.DataFrame) -> Dict:
        """
        Analyze distribution across devices.
        
        WHY: Helps detect bias (all healthy leaves from iPhone, etc.)
        
        Args:
            metadata_df (pd.DataFrame): Metadata dataframe
            
        Returns:
            dict: Device distribution analysis
        """
        device_disease = pd.crosstab(
            metadata_df["device_type"],
            metadata_df["disease_class"],
            margins=True
        )
        
        return {
            "distribution": device_disease.to_dict(),
            "by_device": metadata_df.groupby("device_type").size().to_dict()
        }
    
    @staticmethod
    def analyze_contributor_distribution(metadata_df: pd.DataFrame) -> Dict:
        """
        Analyze distribution across contributors.
        
        WHY: Detect if one person is overrepresented (potential bias)
        
        Args:
            metadata_df (pd.DataFrame): Metadata dataframe
            
        Returns:
            dict: Contributor distribution analysis
        """
        contributor_disease = pd.crosstab(
            metadata_df["contributor_name"],
            metadata_df["disease_class"],
            margins=True
        )
        
        return {
            "distribution": contributor_disease.to_dict(),
            "by_contributor": metadata_df.groupby("contributor_name").size().to_dict()
        }
    
    @staticmethod
    def analyze_quality_issues(metadata_df: pd.DataFrame) -> Dict:
        """
        Analyze quality issues across dataset.
        
        Args:
            metadata_df (pd.DataFrame): Metadata dataframe
            
        Returns:
            dict: Quality analysis
        """
        quality_by_disease = metadata_df.groupby("disease_class")["is_quality"].agg(["sum", "count"])
        quality_by_device = metadata_df.groupby("device_type")["is_quality"].agg(["sum", "count"])
        
        return {
            "quality_by_disease": quality_by_disease.to_dict(),
            "quality_by_device": quality_by_device.to_dict(),
            "average_blur_score": float(metadata_df["blur_score"].mean()) if "blur_score" in metadata_df.columns else None,
            "average_brightness": float(metadata_df["brightness_score"].mean()) if "brightness_score" in metadata_df.columns else None
        }
    
    @staticmethod
    def detect_potential_issues(metadata_df: pd.DataFrame) -> List[str]:
        """
        Detect potential issues in dataset.
        
        WHY: Proactive quality check before model training
        
        Args:
            metadata_df (pd.DataFrame): Metadata dataframe
            
        Returns:
            list: List of detected issues
        """
        issues = []
        
        # Check class imbalance
        class_counts = metadata_df["disease_class"].value_counts()
        if len(class_counts) > 1:
            max_count = class_counts.max()
            min_count = class_counts.min()
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
            
            if imbalance_ratio > 3:  # More than 3x difference
                issues.append(f"High class imbalance: {imbalance_ratio:.1f}x")
        
        # Check device distribution
        device_counts = metadata_df["device_type"].value_counts()
        if len(device_counts) > 1:
            max_dev = device_counts.max()
            min_dev = device_counts.min()
            if max_dev / min_dev > 2:
                issues.append("Unbalanced device distribution across splits")
        
        # Check quality rejection rate
        quality_rate = metadata_df["is_quality"].sum() / len(metadata_df) if len(metadata_df) > 0 else 0
        if quality_rate < 0.8:
            issues.append(f"Low quality acceptance rate: {quality_rate*100:.1f}%")
        
        # Check for single contributor
        if len(metadata_df["contributor_name"].unique()) == 1:
            issues.append("All images from single contributor - high bias risk")
        
        # Check file format consistency
        if "original_format" in metadata_df.columns:
            format_counts = metadata_df["original_format"].value_counts()
            if len(format_counts) == 1:
                issues.append("All images same original format - less robust model")
        
        return issues
