"""
Duplicate Detection Module - Find duplicate and near-duplicate images.

This module implements image hashing for duplicate detection:
- Multiple hash algorithms (dhash, phash, ahash, whash)
- Hamming distance comparison
- Duplicate clustering
"""

import imagehash
import logging
from pathlib import Path
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Detect duplicate and near-duplicate images using perceptual hashing."""
    
    HASH_ALGORITHMS = {
        "ahash": imagehash.average_hash,     # Average hash - basic differences
        "dhash": imagehash.dhash,            # Difference hash - better for scaled images
        "phash": imagehash.phash,            # Perceptual hash - robust to minor changes
        "whash": imagehash.whash             # Wavelet hash - good for complex patterns
    }
    
    def __init__(self, hash_size=8, algorithm="dhash", threshold=0.90):
        """
        Initialize DuplicateDetector.
        
        WHY TUNING MATTERS:
        - Hash algorithm affects duplicate detection quality
        - Hash size affects precision-sensitivity tradeoff
        - Threshold determines sensitivity to similarity
        
        Args:
            hash_size (int): Hash grid size (8x8 = 64-bit hash)
            algorithm (str): Hash algorithm name from HASH_ALGORITHMS
            threshold (float): Similarity threshold (0.0-1.0)
                0.95 = 95% similar (strict, catches exact/near-exact)
                0.85 = 85% similar (loose, includes rotations/crops)
        """
        if algorithm not in self.HASH_ALGORITHMS:
            raise ValueError(f"Unknown algorithm. Choose from: {list(self.HASH_ALGORITHMS.keys())}")
        
        self.hash_size = hash_size
        self.algorithm = algorithm
        self.hash_function = self.HASH_ALGORITHMS[algorithm]
        self.threshold = threshold
        self.image_hashes = {}  # Maps image_path -> hash
    
    def compute_hash(self, image_path):
        """
        Compute perceptual hash for image.
        
        WHY PERCEPTUAL HASHING:
        Different from cryptographic hashing (MD5, SHA1):
        - Cryptographic hash: small change -> completely different hash
        - Perceptual hash: similar images -> similar hashes
        
        This enables finding near-duplicates from different devices.
        Example: Same disease photo, different compression settings
                 -> different bits, but similar hash
        
        Args:
            image_path (str or Path): Path to image
            
        Returns:
            imagehash.ImageHash or None if failed
        """
        try:
            image_path = Path(image_path)
            
            # imagehash.phash, dhash, etc. return ImageHash objects
            image_hash = self.hash_function(
                imagehash.Image.open(str(image_path)),
                hash_size=self.hash_size
            )
            
            return image_hash
            
        except Exception as e:
            logger.warning(f"could not compute hash for {image_path}: {e}")
            return None
    
    def compute_hamming_distance(self, hash1, hash2):
        """
        Compute Hamming distance between two hashes.
        
        WHY: Hamming distance counts differing bits.
        Similar images -> few different bits -> low distance
        Different images -> many different bits -> high distance
        
        Args:
            hash1 (imagehash.ImageHash): First hash
            hash2 (imagehash.ImageHash): Second hash
            
        Returns:
            int: Hamming distance (number of differing bits)
        """
        if hash1 is None or hash2 is None:
            return float('inf')
        
        return hash1 - hash2  # ImageHash.__sub__ returns Hamming distance
    
    def compute_similarity(self, hash1, hash2):
        """
        Compute similarity score between two hashes (0.0-1.0).
        
        Args:
            hash1 (imagehash.ImageHash): First hash
            hash2 (imagehash.ImageHash): Second hash
            
        Returns:
            float: Similarity score (0.0 = completely different, 1.0 = identical)
        """
        distance = self.compute_hamming_distance(hash1, hash2)
        
        if hash1 is None or hash2 is None:
            return 0.0
        
        # Convert distance to similarity
        # Maximum possible distance is hash.size ** 2 / 2 * 8 (64 bits for 8x8)
        # For 8x8 hash: max distance = 64 bits
        max_distance = 64 if self.hash_size == 8 else self.hash_size * self.hash_size
        similarity = 1.0 - (distance / max_distance)
        
        return max(0.0, min(1.0, similarity))
    
    def are_duplicates(self, hash1, hash2):
        """
        Determine if two hashes represent duplicate images.
        
        Args:
            hash1 (imagehash.ImageHash): First hash
            hash2 (imagehash.ImageHash): Second hash
            
        Returns:
            bool: True if images are duplicates (above threshold)
        """
        similarity = self.compute_similarity(hash1, hash2)
        return similarity >= self.threshold
    
    def find_duplicates_in_batch(self, image_paths):
        """
        Find all duplicate pairs/groups in batch of images.
        
        WHY: Prevents data leakage when same image appears in train and test.
        Also removes redundant images to increase effective dataset size.
        
        Args:
            image_paths (list): List of image file paths
            
        Returns:
            dict: Results {
                "hashes": {image_path: hash},
                "duplicate_groups": [[image1, image2], [image3, image4, image5]],
                "duplicate_count": int
            }
        """
        # Compute hashes
        hashes = {}
        for image_path in image_paths:
            image_hash = self.compute_hash(image_path)
            hashes[str(image_path)] = image_hash
        
        # Find duplicate groups
        duplicate_groups = []
        processed = set()
        
        image_paths_str = [str(p) for p in image_paths]
        
        for i, path1 in enumerate(image_paths_str):
            if path1 in processed:
                continue
            
            group = [path1]
            
            for path2 in image_paths_str[i+1:]:
                if path2 in processed:
                    continue
                
                if self.are_duplicates(hashes[path1], hashes[path2]):
                    group.append(path2)
                    processed.add(path2)
            
            if len(group) > 1:
                duplicate_groups.append(group)
                processed.add(path1)
        
        duplicate_count = sum(len(group) - 1 for group in duplicate_groups)
        
        return {
            "hashes": hashes,
            "duplicate_groups": duplicate_groups,
            "duplicate_count": duplicate_count,
            "unique_count": len(image_paths) - duplicate_count
        }
    
    def build_hash_database(self, image_paths, batch_size=100):
        """
        Build database of image hashes for entire dataset.
        
        Args:
            image_paths (list): All image paths
            batch_size (int): Process in batches to show progress
            
        Returns:
            dict: Mapping of image_path -> hash
        """
        hash_db = {}
        total = len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            if i % batch_size == 0:
                logger.info(f"Hashing: {i}/{total}")
            
            image_hash = self.compute_hash(image_path)
            hash_db[str(image_path)] = image_hash
        
        logger.info(f"Hash database complete: {total} images")
        return hash_db
    
    def find_all_duplicates(self, hash_database):
        """
        Find all duplicates in database using optimized algorithm.
        
        WHY: More efficient than pairwise comparison for large datasets.
        Uses grouping to avoid comparing all pairs.
        
        Args:
            hash_database (dict): Output from build_hash_database()
            
        Returns:
            dict: Duplicate information
        """
        # Group images by hash prefix for faster comparison
        hash_groups = defaultdict(list)
        
        for image_path, image_hash in hash_database.items():
            if image_hash is None:
                hash_groups["unhashable"].append(image_path)
                continue
            
            # Use first 16 bits as prefix for grouping
            # This reduces comparisons needed
            prefix = str(image_hash)[:4]
            hash_groups[prefix].append((image_path, image_hash))
        
        # Find duplicates within each group
        duplicate_groups = []
        all_duplicates = set()
        
        for group_items in hash_groups.values():
            if isinstance(group_items[0], str):  # Unhashable group
                # Each unhashable image is its own group
                for item in group_items:
                    all_duplicates.add(item)
                continue
            
            # Find duplicates within this group
            for i, (path1, hash1) in enumerate(group_items):
                if path1 in all_duplicates:
                    continue
                
                group = [path1]
                
                for path2, hash2 in group_items[i+1:]:
                    if path2 not in all_duplicates and self.are_duplicates(hash1, hash2):
                        group.append(path2)
                        all_duplicates.add(path2)
                
                if len(group) > 1:
                    duplicate_groups.append(group)
                    all_duplicates.add(path1)
        
        return {
            "duplicate_groups": duplicate_groups,
            "total_duplicates": len(all_duplicates),
            "total_unique": len(hash_database) - len(all_duplicates)
        }


class DuplicateRemover:
    """Handle removal/marking of duplicate images."""
    
    @staticmethod
    def select_duplicates_to_remove(duplicate_group, strategy="keep_first"):
        """
        Select which images in duplicate group to remove.
        
        WHY: When duplicates found, keep ONE, remove others.
        Different strategies for different scenarios.
        
        Args:
            duplicate_group (list): List of duplicate image paths
            strategy (str): Removal strategy
                "keep_first": Keep first image
                "keep_best": Keep largest file (highest quality)
                "keep_shortest_path": Keep shortest filename
        
        Returns:
            dict: {"keep": [path], "remove": [paths]}
        """
        if not duplicate_group or len(duplicate_group) < 2:
            return {"keep": duplicate_group, "remove": []}
        
        if strategy == "keep_first":
            return {
                "keep": [duplicate_group[0]],
                "remove": duplicate_group[1:]
            }
        
        elif strategy == "keep_best":
            # Keep largest file (usually best quality)
            largest_idx = max(
                range(len(duplicate_group)),
                key=lambda i: Path(duplicate_group[i]).stat().st_size
            )
            keep = duplicate_group[largest_idx]
            remove = duplicate_group[:largest_idx] + duplicate_group[largest_idx+1:]
            return {"keep": [keep], "remove": remove}
        
        elif strategy == "keep_shortest_path":
            shortest_idx = min(
                range(len(duplicate_group)),
                key=lambda i: len(str(duplicate_group[i]))
            )
            keep = duplicate_group[shortest_idx]
            remove = duplicate_group[:shortest_idx] + duplicate_group[shortest_idx+1:]
            return {"keep": [keep], "remove": remove}
        
        else:
            logger.warning(f"Unknown strategy: {strategy}, using keep_first")
            return DuplicateRemover.select_duplicates_to_remove(
                duplicate_group, "keep_first"
            )
    
    @staticmethod
    def generate_removal_report(duplicate_groups, total_original):
        """
        Generate report on duplicate removal impact.
        
        Args:
            duplicate_groups (list): List of duplicate groups
            total_original (int): Total original image count
            
        Returns:
            dict: Statistical report
        """
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        remaining_images = total_original - total_duplicates
        
        return {
            "total_original": total_original,
            "duplicate_count": total_duplicates,
            "remaining_after_removal": remaining_images,
            "removal_rate": (total_duplicates / total_original * 100) if total_original > 0 else 0,
            "duplicate_groups": len(duplicate_groups)
        }
