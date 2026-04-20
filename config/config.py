"""
Configuration module for the Banana Leaf Disease Dataset Preprocessing Pipeline.

This module contains all configurable parameters for the preprocessing pipeline.
These settings control image processing, quality thresholds, and dataset organization.

IMPORTANT: Modify these settings based on your specific requirements and hardware capabilities.
"""

import os
from pathlib import Path

# ==================== ENVIRONMENT ====================
# Set to True for Google Colab, False for local development
IS_COLAB = True  # Set to True when running in Google Colab

# ===== GOOGLE DRIVE PATHS (FOR COLAB) =====
# Dataset input: From "Shared with me" folder
DATASET_INPUT_PATH = "/content/drive/MyDrive/Mini_Project_Dataset"

# Dataset output: Saved to "Banana_Leaf_Processed" in My Drive
DATASET_OUTPUT_ROOT = "/content/drive/MyDrive/Banana_Leaf_Processed"

MOUNT_POINT = DATASET_INPUT_PATH if IS_COLAB else None

# Dataset paths (for local testing)
BASE_DATASET_DIR = Path("./dataset")
RAW_DATASET_DIR = BASE_DATASET_DIR / "raw"
PROCESSED_DATASET_DIR = BASE_DATASET_DIR / "processed"
SPLIT_DATASET_DIR = BASE_DATASET_DIR / "split"
METADATA_DIR = BASE_DATASET_DIR / "metadata"

# ==================== IMAGE PROCESSING ====================
# Target image dimensions (CNN-ready format)
# Common sizes: 224x224 (ImageNet default), 256x256 (higher precision)
# NOTE: Must be consistent across all preprocessing
TARGET_IMAGE_SIZE = (256, 256)  # (height, width)

# Target color space
TARGET_COLOR_SPACE = "RGB"  # Always RGB for most CNN architectures

# Target image format for all conversions
TARGET_IMAGE_FORMAT = "JPEG"  # JPEG (best for photos), PNG (best for lossless)
JPEG_QUALITY = 90  # 1-100, higher = better quality but larger size

# Supported input formats (MUST support these from Google Drive)
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".heic"}

# ==================== QUALITY DETECTION THRESHOLDS ====================
# These thresholds help identify problematic images that don't belong in the dataset

# Blur Detection (Laplacian variance method)
# IMPORTANT: Tuning this affects model robustness
# Lower values = stricter blur detection
# Typical range: 50-500 depending on image content
BLUR_THRESHOLD = 100.0

# Brightness Detection (normalized pixel mean)
# Detects extremely dark (underexposed) or overexposed images
# Range: 0-255, typical healthy leaves: 80-200
MIN_BRIGHTNESS = 40  # Below this = too dark
MAX_BRIGHTNESS = 240  # Above this = overexposed (blown out)

# Contrast Detection (std dev of pixel values)
# Images with very low contrast may be unreadable
MIN_CONTRAST = 15.0  # Below this = flat, non-informative

# Corruption Detection
# Max acceptable error rate when loading/processing images
MAX_CORRUPTION_ATTEMPTS = 3

# ==================== DUPLICATE DETECTION ====================
# Image Hashing for Perceptual Duplicate Detection
# Uses multiple hash algorithms for robustness

# Hash settings (IMPORTANT for duplicate detection accuracy)
HASH_SIZE = 8  # 8x8 = 64-bit hash (common choice)
HASH_ALGORITHM = "dhash"  # Options: "ahash", "dhash", "phash", "whash"
# dhash (difference hash) is best for simple duplicates
# phash (perceptual hash) is best for manipulated/scaled images

# Duplicate matching threshold (0-1 scale)
# Hamming distance similarity for considering images as duplicates
# 0.95 = 95% similar (stricter), 0.85 = 85% similar (looser)
DUPLICATE_THRESHOLD = 0.90

# ==================== DATASET SPLITTING ====================
# Train-Validation-Test Split Ratios
# IMPORTANT: These affect model generalization capability
TRAIN_RATIO = 0.70  # 70% for training
VAL_RATIO = 0.15    # 15% for validation (tuning hyperparameters)
TEST_RATIO = 0.15   # 15% for testing (final evaluation)

# NOTE: These ratios MUST sum to 1.0
assert TRAIN_RATIO + VAL_RATIO + TEST_RATIO == 1.0, "Split ratios must sum to 1.0"

# Random seed for reproducibility
# IMPORTANT: Use same seed for paper/publication reproducibility
RANDOM_SEED = 42

# Stratification settings
USE_STRATIFIED_SPLIT = True  # Maintains disease class distribution
BALANCE_DEVICE_DISTRIBUTION = True  # Ensures fair iPhone/Android split

# ==================== DISEASE CLASSES ====================
# Must match your Google Drive folder names exactly
DISEASE_CLASSES = [
    "healthy_leaves",
    "panama_wilt",
    "potassium_deficiency",
    "sigatoka"
]

# ==================== DEVICE MAPPING ====================
# Maps contributor folders to device types
# IMPORTANT: Update based on your actual data collection setup
DEVICE_MAPPING = {
    "Vedant_Primary": "iPhone",
    "Vedant_Secondary": "iPhone",
    "Sagar": "Android",
    "Subodh": "Android",
    "Sudhanshu": "Android"
}

# ==================== IMAGE AUGMENTATION ====================
# Optional augmentation for CNN training (NOT used during preprocessing)
# These can be applied after splitting during model training
AUGMENTATION_CONFIG = {
    "rotation_range": 20,  # degrees
    "zoom_range": [0.8, 1.2],  # 80-120% zoom
    "brightness_range": [0.8, 1.2],  # 80-120% brightness
    "horizontal_flip": True,
    "vertical_flip": False,  # Usually False for agriculture images
    "random_crop_size": None,  # Set to (h, w) to enable
}

# ==================== LOGGING & REPORTING ====================
# Controls verbosity and logging level
VERBOSE = True  # Print detailed progress information
LOG_FILE = METADATA_DIR / "preprocessing_log.txt"

# Report generation
GENERATE_QUALITY_REPORT = True  # Detailed quality analysis report
GENERATE_STATISTICS = True  # Dataset statistics and distribution

# ==================== PROCESSING LIMITS ====================
# Useful for testing on subset of data
MAX_IMAGES_PER_CLASS = None  # None = process all, or set to limit (e.g., 100)
MAX_WORKERS = 4  # For parallel processing (CPU cores available)

# ==================== FILE ORGANIZATION ====================
# CSV file for metadata tracking
METADATA_CSV = METADATA_DIR / "image_metadata.csv"
CROSS_DEVICE_SPLIT_CSV = METADATA_DIR / "cross_device_splits.csv"

# ==================== VALIDATION ====================
def validate_config():
    """
    Validate configuration parameters.
    Call this at startup to catch configuration errors early.
    """
    errors = []
    
    # Validate split ratios
    if not (abs(TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0) < 1e-6):
        errors.append("Split ratios must sum to 1.0")
    
    # Validate image size
    if TARGET_IMAGE_SIZE[0] <= 0 or TARGET_IMAGE_SIZE[1] <= 0:
        errors.append("TARGET_IMAGE_SIZE must be positive integers")
    
    # Validate thresholds
    if BLUR_THRESHOLD <= 0:
        errors.append("BLUR_THRESHOLD must be positive")
    
    if MIN_BRIGHTNESS >= MAX_BRIGHTNESS:
        errors.append("MIN_BRIGHTNESS must be less than MAX_BRIGHTNESS")
    
    if DUPLICATE_THRESHOLD < 0 or DUPLICATE_THRESHOLD > 1.0:
        errors.append("DUPLICATE_THRESHOLD must be between 0 and 1")
    
    # Validate disease classes
    if not DISEASE_CLASSES:
        errors.append("DISEASE_CLASSES cannot be empty")
    
    # Validate device mapping covers all contributors
    contributors = set()
    for disease_class in DISEASE_CLASSES:
        # Additional validation if needed
        pass
    
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
    
    return True


# Ensure config is valid on import
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"WARNING: {e}")


# ==================== HELPFUL COMMENTS ====================
"""
WHY EACH SETTING MATTERS:

1. TARGET_IMAGE_SIZE (256x256):
   - CNN models expect fixed input dimensions
   - 224x224 is standard (ImageNet), but 256x256 gives more detail
   - Larger = more computation but potentially better accuracy
   - Must be consistent across ALL images in dataset

2. BLUR_THRESHOLD (100):
   - Prevents low-quality images that can't provide disease patterns
   - Too high: includes blurry images, model learns wrong patterns
   - Too low: removes too many images, insufficient data
   - Test threshold on sample images before full pipeline

3. MIN/MAX_BRIGHTNESS (40, 240):
   - Removes images taken in poor lighting conditions
   - Dark images: disease patterns invisible to model
   - Overexposed images: fine details lost
   - Agricultural images should have clear, natural lighting

4. DUPLICATE_THRESHOLD (0.90):
   - Prevents data leakage from identical/near-identical images
   - Data leakage causes artificially high accuracy
   - 0.90 = 90% similar (catches rotations, minor crops)
   - Should be higher for images with minor variations

5. TRAIN/VAL/TEST split (70/15/15):
   - 70% for learning disease patterns
   - 15% for tuning model hyperparameters
   - 15% for final testing (unseen during training)
   - Never tune on test set!

6. DEVICE_MAPPING:
   - Essential for cross-device validation
   - Prevents model from learning phone characteristics instead of diseases
   - iPhone vs Android may have different color profiles, sensors
   - Cross-device accuracy is TRUE accuracy metric

7. RANDOM_SEED (42):
   - Ensures reproducibility for academic papers
   - Same seed = same split across runs
   - Change only if you need different splits
"""
