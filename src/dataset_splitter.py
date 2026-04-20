"""
Dataset Splitter Module - Intelligent train/validation/test splitting.

This module implements:
- Stratified splitting (maintains class distribution)
- Device-aware splitting
- Cross-device validation splits
- No data leakage guarantees
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from sklearn.model_selection import train_test_split, StratifiedShuffleSplit
import shutil

logger = logging.getLogger(__name__)


class DatasetSplitter:
    """Intelligent dataset splitting with multiple strategies."""
    
    def __init__(self, random_seed=42):
        """
        Initialize splitter.
        
        Args:
            random_seed (int): Seed for reproducibility
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def stratified_split(
        self,
        metadata_df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> Dict[str, pd.DataFrame]:
        """
        Split dataset with stratification by disease class.
        
        WHY: Ensures each split has representative samples of each disease.
        Without stratification:
        - Train might get 90% of "healthy" (overfit to that class)
        - Test might get 90% of "sigatoka" (unfair evaluation)
        
        With stratification:
        - Each split maintains ~25% of each disease class
        - Fair representation across splits
        - More reliable generalization metrics
        
        Args:
            metadata_df (pd.DataFrame): Image metadata
            train_ratio (float): Training set ratio
            val_ratio (float): Validation set ratio
            test_ratio (float): Test set ratio
            
        Returns:
            dict: {"train": df, "val": df, "test": df}
        """
        # Validate split ratios
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 1e-6:
            raise ValueError(f"Split ratios must sum to 1.0, got {total_ratio}")
        
        # First split: separate test set
        # Use stratification to keep class proportions
        splitter = StratifiedShuffleSplit(
            n_splits=1,
            test_size=test_ratio,
            random_state=self.random_seed
        )
        
        train_val_idx, test_idx = next(
            splitter.split(metadata_df, metadata_df["disease_class"])
        )
        
        train_val_df = metadata_df.iloc[train_val_idx].reset_index(drop=True)
        test_df = metadata_df.iloc[test_idx].reset_index(drop=True)
        
        # Second split: separate validation from training
        val_ratio_adjusted = val_ratio / (train_ratio + val_ratio)
        
        splitter_val = StratifiedShuffleSplit(
            n_splits=1,
            test_size=val_ratio_adjusted,
            random_state=self.random_seed
        )
        
        train_idx, val_idx = next(
            splitter_val.split(train_val_df, train_val_df["disease_class"])
        )
        
        train_df = train_val_df.iloc[train_idx].reset_index(drop=True)
        val_df = train_val_df.iloc[val_idx].reset_index(drop=True)
        
        # Verify stratification worked
        self._verify_stratification(metadata_df, train_df, val_df, test_df)
        
        return {
            "train": train_df,
            "val": val_df,
            "test": test_df
        }
    
    def device_aware_split(
        self,
        metadata_df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        balance_devices: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Split dataset maintaining device type balance across splits.
        
        WHY: Important for model generalization across devices.
        - Model should not overfit to one device's sensor/camera characteristics
        - iPhone and Android have different color profiles, sensors
        - Balanced devices = model learns disease patterns, not device patterns
        
        Args:
            metadata_df (pd.DataFrame): Image metadata
            train_ratio (float): Training set ratio
            val_ratio (float): Validation set ratio
            test_ratio (float): Test set ratio
            balance_devices (bool): Maintain device balance across splits
            
        Returns:
            dict: {"train": df, "val": df, "test": df}
        """
        if not balance_devices:
            return self.stratified_split(metadata_df, train_ratio, val_ratio, test_ratio)
        
        # Create stratification key combining disease and device
        metadata_df = metadata_df.copy()
        metadata_df["strat_key"] = (
            metadata_df["disease_class"].astype(str) + "_" + 
            metadata_df["device_type"].astype(str)
        )
        
        # Split with stratification on combined key
        splitter = StratifiedShuffleSplit(
            n_splits=1,
            test_size=test_ratio,
            random_state=self.random_seed
        )
        
        train_val_idx, test_idx = next(
            splitter.split(metadata_df, metadata_df["strat_key"])
        )
        
        train_val_df = metadata_df.iloc[train_val_idx].reset_index(drop=True)
        test_df = metadata_df.iloc[test_idx].reset_index(drop=True)
        
        # Split train/val
        val_ratio_adjusted = val_ratio / (train_ratio + val_ratio)
        splitter_val = StratifiedShuffleSplit(
            n_splits=1,
            test_size=val_ratio_adjusted,
            random_state=self.random_seed
        )
        
        train_idx, val_idx = next(
            splitter_val.split(train_val_df, train_val_df["strat_key"])
        )
        
        train_df = train_val_df.iloc[train_idx].reset_index(drop=True)
        val_df = train_val_df.iloc[val_idx].reset_index(drop=True)
        
        # Log device distribution
        self._log_device_distribution(train_df, val_df, test_df)
        
        return {
            "train": train_df,
            "val": val_df,
            "test": test_df
        }
    
    def create_cross_device_splits(
        self,
        metadata_df: pd.DataFrame,
        test_ratio: float = 0.15
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Create cross-device validation splits.
        
        WHY: Most important for verifying model isn't learning device characteristics.
        
        CROSS-DEVICE EVALUATION:
        - Train on iPhone, test on Android -> measures generalization to new device
        - Train on Android, test on iPhone -> measures generalization to new device
        - If accuracy much higher within-device than cross-device:
          -> Model learned device characteristics, not disease patterns
          -> BAD - Model will fail in real world with different phones
        
        Args:
            metadata_df (pd.DataFrame): Image metadata
            test_ratio (float): Test set ratio
            
        Returns:
            dict: {
                "within_device": {"train": df, "test": df},
                "iphone_train_android_test": {"train": df, "test": df},
                "android_train_iphone_test": {"train": df, "test": df}
            }
        """
        devices = metadata_df["device_type"].unique()
        
        splits_dict = {}
        
        # 1. Within-device split (baseline - normal split)
        logger.info("Creating within-device split (normal)...")
        within_device_split = self.stratified_split(
            metadata_df,
            train_ratio=1-test_ratio,
            val_ratio=0,
            test_ratio=test_ratio
        )
        splits_dict["within_device"] = {
            "train": within_device_split["train"],
            "test": within_device_split["test"]
        }
        
        # 2. Cross-device splits (if multiple devices exist)
        if len(devices) >= 2:
            device_list = sorted(list(devices))
            
            for i, device1 in enumerate(device_list):
                for device2 in device_list[i+1:]:
                    # Train on device1, test on device2
                    device1_data = metadata_df[metadata_df["device_type"] == device1]
                    device2_data = metadata_df[metadata_df["device_type"] == device2]
                    
                    if len(device1_data) > 0 and len(device2_data) > 0:
                        split_name = f"{device1}_train_{device2}_test"
                        splits_dict[split_name] = {
                            "train": device1_data.reset_index(drop=True),
                            "test": device2_data.reset_index(drop=True)
                        }
                        logger.info(f"  {split_name}: {len(device1_data)} train, {len(device2_data)} test")
                    
                    # Train on device2, test on device1
                    if len(device2_data) > 0 and len(device1_data) > 0:
                        split_name = f"{device2}_train_{device1}_test"
                        splits_dict[split_name] = {
                            "train": device2_data.reset_index(drop=True),
                            "test": device1_data.reset_index(drop=True)
                        }
        
        return splits_dict
    
    def assign_splits(
        self,
        metadata_df: pd.DataFrame,
        split_assignment: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Assign split labels to metadata records.
        
        Args:
            metadata_df (pd.DataFrame): Original metadata
            split_assignment (dict): Split dataframes with indices
            
        Returns:
            pd.DataFrame: Updated metadata with split assignments
        """
        metadata_df = metadata_df.copy()
        metadata_df["split_assignment"] = "unassigned"
        
        for split_name, split_df in split_assignment.items():
            # Get indices of split_df and assign split names
            indices = split_df.index.tolist()
            # Use original dataframe indices
            for idx in indices:
                metadata_df.loc[idx, "split_assignment"] = split_name
        
        return metadata_df
    
    def verify_no_leakage(
        self,
        metadata_df: pd.DataFrame,
        split_assignment: Dict[str, pd.DataFrame]
    ) -> bool:
        """
        Verify no data leakage between splits.
        
        WHY: Essential for reliable model evaluation.
        Data leakage = same image (or near-duplicate) in train AND test
        Result: Artificially high accuracy that doesn't generalize
        
        Args:
            metadata_df (pd.DataFrame): Metadata with duplicate_group_id
            split_assignment (dict): Split assignments
            
        Returns:
            bool: True if no leakage detected
        """
        splits = list(split_assignment.values())
        has_leakage = False
        
        # Check for exact image duplicates across splits
        for split1_name, split1_df in split_assignment.items():
            for split2_name, split2_df in split_assignment.items():
                if split1_name >= split2_name:  # Skip self-comparison
                    continue
                
                # Check if any images appear in both splits
                set1 = set(split1_df.index)
                set2 = set(split2_df.index)
                
                overlap = set1 & set2
                if len(overlap) > 0:
                    logger.error(
                        f"Data leakage detected between {split1_name} and {split2_name}: "
                        f"{len(overlap)} overlapping images"
                    )
                    has_leakage = True
        
        # Check for duplicate groups spanning multiple splits
        if "duplicate_group_id" in metadata_df.columns:
            for dup_group_id in metadata_df["duplicate_group_id"].unique():
                if pd.isna(dup_group_id):
                    continue
                
                group_indices = metadata_df[
                    metadata_df["duplicate_group_id"] == dup_group_id
                ].index.tolist()
                
                # Check if group spans multiple splits
                group_splits = metadata_df.loc[group_indices, "split_assignment"].unique()
                if len(group_splits) > 1:
                    logger.warning(
                        f"Duplicate group {dup_group_id} spans multiple splits: {group_splits}"
                    )
        
        return not has_leakage
    
    def organize_by_split(
        self,
        metadata_df: pd.DataFrame,
        output_base_dir: Path,
        copy_files: bool = True,
        link_files: bool = False
    ) -> bool:
        """
        Organize images into train/val/test folder structure.
        
        Args:
            metadata_df (pd.DataFrame): Metadata with processed_path and split_assignment
            output_base_dir (Path): Output base directory
            copy_files (bool): Copy files to new locations
            link_files (bool): Create symbolic links (if False and copy_files False, only update metadata)
            
        Returns:
            bool: Success status
        """
        output_base_dir = Path(output_base_dir)
        
        try:
            for split_name in ["train", "val", "test"]:
                split_data = metadata_df[metadata_df["split_assignment"] == split_name]
                
                for _, row in split_data.iterrows():
                    processed_path = Path(row["processed_path"])
                    disease_class = row["disease_class"]
                    
                    # Create output path
                    output_dir = output_base_dir / split_name / disease_class
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    output_file = output_dir / processed_path.name
                    
                    if copy_files and processed_path.exists():
                        shutil.copy2(processed_path, output_file)
                        logger.debug(f"Copied {processed_path} -> {output_file}")
                    
                    if link_files and processed_path.exists():
                        try:
                            output_file = output_dir / processed_path.name
                            if not output_file.exists():
                                Path(output_file).symlink_to(processed_path)
                                logger.debug(f"Linked {processed_path} -> {output_file}")
                        except Exception as e:
                            logger.warning(f"Could not create symlink: {e}")
            
            logger.info(f"Organized dataset into {output_base_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to organize dataset: {e}")
            return False
    
    @staticmethod
    def _verify_stratification(full_df, train_df, val_df, test_df):
        """Verify stratification worked correctly."""
        full_dist = full_df["disease_class"].value_counts(normalize=True)
        train_dist = train_df["disease_class"].value_counts(normalize=True)
        val_dist = val_df["disease_class"].value_counts(normalize=True)
        test_dist = test_df["disease_class"].value_counts(normalize=True)
        
        logger.info("Disease distribution verification:")
        logger.info(f"  Full dataset: {dict(full_dist)}")
        logger.info(f"  Train set: {dict(train_dist)}")
        logger.info(f"  Val set: {dict(val_dist)}")
        logger.info(f"  Test set: {dict(test_dist)}")
    
    @staticmethod
    def _log_device_distribution(train_df, val_df, test_df):
        """Log device distribution across splits."""
        logger.info("Device distribution verification:")
        if "device_type" in train_df.columns:
            logger.info(f"  Train: {dict(train_df['device_type'].value_counts())}")
            logger.info(f"  Val: {dict(val_df['device_type'].value_counts())}")
            logger.info(f"  Test: {dict(test_df['device_type'].value_counts())}")
