"""
File Utility Functions - Folder scanning, path management, I/O operations.

This module handles:
- Recursive folder scanning
- File discovery and filtering
- Path management
- Batch operations
"""

import os
import logging
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class FileManager:
    """Handles file and folder operations."""
    
    VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}
    
    @classmethod
    def discover_images(cls, base_path, disease_classes=None):
        """
        Discover all images in folder structure.
        
        WHY: Automates finding images across entire Google Drive structure.
        Prevents manual file listing and path errors.
        
        Args:
            base_path (str or Path): Root folder containing disease class folders
            disease_classes (list): List of disease class folder names to scan
            
        Returns:
            dict: Structure {disease_class: {contributor: [image_paths]}}
            
        Example:
            {
                "healthy_leaves": {
                    "Sagar": [Path(...), Path(...)],
                    "Subodh": [Path(...)]
                },
                "panama_wilt": {...}
            }
        """
        base_path = Path(base_path)
        images_structure = defaultdict(lambda: defaultdict(list))
        
        if not base_path.exists():
            logger.error(f"Base path does not exist: {base_path}")
            return {}
        
        # Iterate through disease classes
        for disease_folder in base_path.iterdir():
            if not disease_folder.is_dir():
                continue
            
            disease_name = disease_folder.name
            
            # Skip if not in specified classes
            if disease_classes and disease_name not in disease_classes:
                continue
            
            # Iterate through contributor folders
            for contributor_folder in disease_folder.iterdir():
                if not contributor_folder.is_dir():
                    continue
                
                contributor_name = contributor_folder.name
                
                # Find all images in contributor folder
                for image_file in contributor_folder.rglob("*"):
                    if image_file.is_file():
                        ext = image_file.suffix.lower()
                        if ext in cls.VALID_IMAGE_EXTENSIONS:
                            images_structure[disease_name][contributor_name].append(image_file)
        
        return dict(images_structure)
    
    @classmethod
    def create_disease_class_folders(cls, base_output_path, disease_classes):
        """
        Create folder structure for processed images.
        
        Args:
            base_output_path (str or Path): Base output directory
            disease_classes (list): List of disease class names
            
        Returns:
            dict: Mapping of disease class to folder paths
        """
        base_output_path = Path(base_output_path)
        folders = {}
        
        for disease_class in disease_classes:
            class_folder = base_output_path / disease_class
            class_folder.mkdir(parents=True, exist_ok=True)
            folders[disease_class] = class_folder
            logger.info(f"Created folder: {class_folder}")
        
        return folders
    
    @classmethod
    def get_image_summary(cls, images_structure):
        """
        Generate summary statistics of discovered images.
        
        Args:
            images_structure (dict): Output from discover_images()
            
        Returns:
            dict: Summary statistics
            
        Example:
            {
                "total_images": 1500,
                "diseases": {
                    "healthy_leaves": {
                        "total": 400,
                        "contributors": {
                            "Sagar": 80,
                            ...
                        }
                    },
                    ...
                }
            }
        """
        summary = {
            "total_images": 0,
            "diseases": {}
        }
        
        for disease, contributors in images_structure.items():
            disease_total = 0
            contributor_counts = {}
            
            for contributor, images in contributors.items():
                count = len(images)
                disease_total += count
                contributor_counts[contributor] = count
            
            summary["diseases"][disease] = {
                "total": disease_total,
                "contributors": contributor_counts
            }
            summary["total_images"] += disease_total
        
        return summary
    
    @classmethod
    def link_images_for_split(cls, split_csv, split_data):
        """
        Create symbolic links or copy instructions for splitting.
        
        WHY: Organizing images into train/val/test folders
        without duplicating files saves disk space (symbolic links)
        or creates organized structure (copying).
        
        Args:
            split_csv (Path): CSV with split assignments
            split_data (dict): Data about splits
            
        Returns:
            bool: Success status
        """
        # This is typically handled in dataset_splitter.py
        # This function provides utility support
        pass
    
    @classmethod
    def get_file_size_mb(cls, file_path):
        """
        Get file size in megabytes.
        
        Args:
            file_path (str or Path): Path to file
            
        Returns:
            float: Size in MB
        """
        file_path = Path(file_path)
        return file_path.stat().st_size / (1024 * 1024)
    
    @classmethod
    def get_directory_size_mb(cls, directory_path):
        """
        Get total size of directory in megabytes.
        
        Args:
            directory_path (str or Path): Path to directory
            
        Returns:
            float: Total size in MB
        """
        directory_path = Path(directory_path)
        total_size = 0
        
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size / (1024 * 1024)
    
    @classmethod
    def ensure_directory(cls, directory_path):
        """
        Ensure directory exists, create if needed.
        
        Args:
            directory_path (str or Path): Path to directory
            
        Returns:
            Path: Directory path
        """
        directory_path = Path(directory_path)
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
    
    @classmethod
    def get_all_images_flat_list(cls, images_structure):
        """
        Flatten image structure to single list with metadata.
        
        Args:
            images_structure (dict): Output from discover_images()
            
        Returns:
            list: List of tuples (image_path, disease_class, contributor)
        """
        flat_list = []
        
        for disease, contributors in images_structure.items():
            for contributor, images in contributors.items():
                for image_path in images:
                    flat_list.append((image_path, disease, contributor))
        
        return flat_list
    
    @classmethod
    def group_by_contributor(cls, images_structure):
        """
        Reorganize image structure to group by contributor.
        
        Args:
            images_structure (dict): Output from discover_images()
            
        Returns:
            dict: Structure {contributor: {disease_class: [images]}}
        """
        by_contributor = defaultdict(lambda: defaultdict(list))
        
        for disease, contributors in images_structure.items():
            for contributor, images in contributors.items():
                by_contributor[contributor][disease].extend(images)
        
        return dict(by_contributor)
    
    @classmethod
    def calculate_storage_requirements(cls, images_structure, avg_file_size_mb=2.5):
        """
        Estimate storage requirements for original and processed images.
        
        WHY: Important for planning disk space in Google Drive/local machine.
        Processed images are typically smaller due to standardization.
        
        Args:
            images_structure (dict): Output from discover_images()
            avg_file_size_mb (float): Average file size estimate
            
        Returns:
            dict: Storage estimation
        """
        summary = cls.get_image_summary(images_structure)
        total_images = summary["total_images"]
        
        # Estimates
        original_size = total_images * avg_file_size_mb
        # Processed images are typically 30-50% of original due to JPEG compression
        processed_size = original_size * 0.35
        
        return {
            "total_images": total_images,
            "estimated_original_mb": original_size,
            "estimated_processed_mb": processed_size,
            "estimated_total_mb": original_size + processed_size,
            "estimated_space_saved": original_size * 0.65  # After removing duplicates
        }


def setup_logging(log_file=None):
    """
    Setup logging configuration.
    
    Args:
        log_file (str or Path): File to log to, or None for console only
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if log_file:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)
