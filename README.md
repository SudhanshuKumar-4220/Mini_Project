# Banana Leaf Disease Classification - Dataset Preprocessing Pipeline

A professional, production-ready Python preprocessing pipeline for the Banana Leaf Disease Classification project. This pipeline handles format conversion, quality assurance, duplicate detection, and intelligent dataset splitting with cross-device validation support.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Detailed Documentation](#detailed-documentation)
- [Why Each Step Matters](#why-each-step-matters)
- [Best Practices & Common Mistakes](#best-practices--common-mistakes)
- [Cross-Device Validation](#cross-device-validation)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Image Processing
- **Multi-format Support**: HEIC, JPG, JPEG, PNG with automatic conversion
- **EXIF Orientation Correction**: Handles mobile phone image rotations
- **Standardization**: Fixed size (256x256), RGB color space, proper normalization
- **Format Unification**: All images converted to optimized JPEG

### Quality Assurance
- **Blur Detection**: Laplacian variance method
- **Brightness Analysis**: Detects underexposed/overexposed images
- **Contrast Checking**: Removes flat, uninformative images
- **Corruption Detection**: Identifies unreadable/corrupt files

### Duplicate Management
- **Perceptual Hashing**: Multiple algorithms (dhash, phash, ahash, whash)
- **Hamming Distance Comparison**: Identifies near-duplicates
- **Data Leakage Prevention**: Ensures same image doesn't appear in multiple splits
- **Grouping**: Intelligent handling of duplicate clusters

### Metadata Tracking
- **Comprehensive Recording**: Disease class, device type, contributor, quality scores
- **Quality Metrics**: Blur, brightness, contrast for each image
- **Split Assignment**: Train/Val/Test with no leakage
- **Audit Trail**: Full processing history

### Intelligent Splitting
- **Stratified Splitting**: Maintains disease class distribution
- **Device-Aware Splitting**: Balances iPhone vs Android across splits
- **Cross-Device Validation**: Train on one device, test on another
- **Reproducible**: Fixed random seed for academic paper reproducibility

---

## 📁 Project Structure

```
MiniProject/
├── config/
│   ├── __init__.py
│   └── config.py                 # Centralized configuration
├── src/
│   ├── __init__.py
│   ├── preprocessing.py          # Main pipeline orchestration
│   ├── quality_checker.py        # Image quality detection
│   ├── duplicate_detection.py    # Duplicate/near-duplicate detection
│   ├── metadata_generator.py     # Metadata tracking and analysis
│   ├── dataset_splitter.py       # Intelligent dataset splitting
│   └── utils/
│       ├── __init__.py
│       ├── image_utils.py        # Image processing utilities
│       └── file_utils.py         # File and folder operations
├── scripts/
│   ├── run_pipeline.py           # Main execution script
│   ├── verify_dataset.py         # Quality verification
│   └── analyze_bias.py           # Bias detection and analysis
├── dataset/
│   ├── raw/                      # Original downloaded data
│   ├── processed/                # Preprocessed images
│   │   ├── healthy_leaves/
│   │   ├── panama_wilt/
│   │   ├── potassium_deficiency/
│   │   └── sigatoka/
│   ├── split/                    # Train/Val/Test organization
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── metadata/                 # CSV files and reports
├── notebooks/
│   └── colab_pipeline.ipynb      # Google Colab notebook
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── .gitignore
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- GPU optional (CPU processing works fine)

### Step 1: Clone or Download Project
```bash
cd MiniProject
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Settings
Edit `config/config.py` for your specific setup:
```python
# For local development
IS_COLAB = False
BASE_DATASET_DIR = Path("./dataset")

# For Google Colab
IS_COLAB = True
MOUNT_POINT = "/content/drive/MyDrive/Mini_Project_Dataset"

# Image processing
TARGET_IMAGE_SIZE = (256, 256)  # or (224, 224)
JPEG_QUALITY = 90

# Quality thresholds
BLUR_THRESHOLD = 100
MIN_BRIGHTNESS = 40
MAX_BRIGHTNESS = 240

# Dataset split
TRAIN_RATIO = 0.70    # 70%
VAL_RATIO = 0.15     # 15%
TEST_RATIO = 0.15    # 15%
```

---

## ⚡ Quick Start

### Local Preprocessing
```bash
python scripts/run_pipeline.py
```

### Google Colab Setup
1. Upload project to Google Drive
2. In Colab notebook:
```python
from google.colab import drive
drive.mount('/content/drive')

# Update config
import sys
sys.path.insert(0, '/content/drive/MyDrive/MiniProject')

from config import config
config.IS_COLAB = True
config.MOUNT_POINT = '/content/drive/MyDrive/Mini_Project_Dataset'

# Run pipeline
exec(open('/content/drive/MyDrive/MiniProject/scripts/run_pipeline.py').read())
```

### After Preprocessing
```bash
# Verify dataset quality
python scripts/verify_dataset.py

# Analyze for bias
python scripts/analyze_bias.py
```

---

## 📚 Detailed Documentation

### 1. Configuration (`config/config.py`)

**Why each setting matters:**

#### IMAGE PROCESSING
- `TARGET_IMAGE_SIZE = (256, 256)`: 
  - Standard size for CNNs (256 or 224)
  - Larger ≠ always better (more computation, may overfit to specific details)
  - MUST be consistent across all images

- `JPEG_QUALITY = 90`:
  - 90 = good balance of quality and file size
  - 95+ = minimal compression but larger files
  - < 85 = visible artifacts, quality loss

#### QUALITY THRESHOLDS
- `BLUR_THRESHOLD = 100`:
  - Detects blurry images (can't show disease patterns)
  - **Too high**: Accepts blurry images → model learns wrong patterns
  - **Too low**: Rejects too many images → insufficient data
  - Test on sample images before full run

- `MIN_BRIGHTNESS = 40, MAX_BRIGHTNESS = 240`:
  - Removes images taken in poor lighting
  - Dark images: disease patterns invisible
  - Overexposed: fine details lost
  - Agricultural images should have natural lighting

- `MIN_CONTRAST = 15`:
  - Removes flat, uninformative images
  - Very low contrast = almost no visual information

#### DATASET SPLITTING
- `TRAIN_RATIO = 0.70, VAL_RATIO = 0.15, TEST_RATIO = 0.15`:
  - Never tune hyperparameters on test set
  - Validation set: for hyperparameter tuning
  - Test set: final evaluation (treated as unseen data)

- `RANDOM_SEED = 42`:
  - Ensures reproducibility for academic papers
  - Same seed = same split across runs
  - IMPORTANT for publication/submission

### 2. Image Processing

#### Format Conversion
- **HEIC → JPEG**: iPhone images use HEIC (better compression)
- **PNG → JPEG**: PNG lossless but larger; JPEG good for photographs
- **Multiple formats**: Handled transparently

#### EXIF Orientation
```
WHY: Mobile phones store rotation in EXIF metadata.
PROBLEM: Loading pixel data directly shows wrong orientation.
SOLUTION: ImageOps.exif_transpose() reads EXIF and rotates image.
```

#### Resizing with Padding
```
WHY: Stretching distorts image, affecting disease pattern recognition.
SOLUTION: Resize with padding to preserve original proportions.
TRADEOFF: Some pixels are padding (white), but original aspect preserved.
```

### 3. Quality Checking

#### Blur Detection (Laplacian Variance)
```python
# Laplacian operator highlights edges
# Sharp edges → high variance
# Blurry images → low variance → low blur_score

# Typical values:
# < 50: Very blurry (reject)
# 50-100: Blurry (questionable)
# 100-200: Acceptable
# > 200: Very sharp
```

#### Brightness Analysis
```python
# Detects lighting problems
# Underexposed: < 40 (disease patterns invisible)
# Good lighting: 80-200
# Overexposed: > 240 (details lost, blown-out)

# WHY MATTERS:
# Model learns: "bright leaf = healthy, dark leaf = diseased"
# But actually: "taken in sunlight" vs "taken in shade"
```

#### Contrast Analysis
```python
# Contrast = standard deviation of pixel values
# Flat image: low std dev (uninformative)
# Normal image: moderate std dev
# High contrast: very high std dev (possibly edited)
```

### 4. Duplicate Detection

#### Perceptual Hashing
```
Different from: Cryptographic hashing (MD5, SHA1)
- Cryptographic: tiny change → completely different hash
- Perceptual: similar images → similar hash

WHY: Find near-duplicates (same disease photo, different compression)
BENEFIT: Remove data redundancy, prevent train/test leakage
```

#### Hash Algorithms
- **dhash (difference hash)**: Best for simple duplicates, rotations
- **phash (perceptual hash)**: Better for manipulated/scaled images
- **ahash (average hash)**: Fastest but less accurate
- **whash (wavelet hash)**: Good for complex patterns

#### Similarity Threshold
```
DUPLICATE_THRESHOLD = 0.90:
- 0.90 = 90% similar (strict, catches near-exact)
- 0.85 = 85% similar (looser, includes variations)

TRADEOFF:
- Too high (0.95+): Misses edited/scaled duplicates
- Too low (0.80-): May mark different disease photos as duplicates
```

### 5. Metadata Generation

Generated CSV columns:
```
image_id             # Unique identifier (IMG_000001)
image_name           # Original filename
disease_class        # Disease type
contributor_name     # Data collector
device_type          # iPhone/Android
original_path        # Original file location
original_format      # Original file type
original_size_mb     # File size before processing
processed_path       # Processed file location
processed_format     # Format after processing
processed_size_mb    # File size after processing
is_quality           # Passed quality checks
blur_score           # Laplacian variance
brightness_score     # Average pixel brightness
contrast_score       # Pixel value std dev
is_duplicate         # Marked as duplicate
duplicate_group_id   # Duplicate group identifier
split_assignment     # Train/Val/Test assignment
```

### 6. Dataset Splitting

#### Stratified Splitting
```
WHY: Maintains disease class distribution in each split

Without stratification:
- Random selection may put all healthy leaves in train
- Test set gets all diseased leaves
- Unfair evaluation

With stratification:
- Each split: 25% healthy, 25% panama_wilt, etc.
- Fair representation
- Reliable generalization metrics
```

#### Device-Aware Splitting
```
WHY: Balances iPhone/Android across splits

GOAL: Model shouldn't learn "iPhone = healthy, Android = diseased"

Example (ideal):
- Train: 50 iPhone images, 50 Android images
- Val: 10 iPhone images, 10 Android images
- Test: 10 iPhone images, 10 Android images

VERIFICATION:
- If accuracy on iPhone 90% but Android 75%
- → Model learned iPhone characteristics
- → Will fail on real Android phones
```

#### Cross-Device Validation
```
CRITICAL TEST for agricultural models:

Scenario 1 (Within-device, baseline):
- Train on iPhone: 90% accuracy
- Test on iPhone: 88% accuracy (good generalization)

Scenario 2 (Cross-device, true test):
- Train on iPhone: 90% accuracy
- Test on Android: 75% accuracy (10% drop!)

INTERPRETATION:
- 15% accuracy drop = Model learned phone characteristics
- Model will fail deployment on different phone
- Need more data collection or better approach

WHAT TO DO:
- Train both ways: both device → other device
- If consistent cross-device drop > 10%: red flag
- Collect more balanced data
```

---

## 🎯 Why Each Preprocessing Step Is Necessary

### 1. Format Conversion
**Problem**: Different phones save different formats (HEIC, JPG, PNG)
**Solution**: Convert all to JPEG for uniformity
**Result**: CNN can process without format-specific code

### 2. EXIF Orientation Correction
**Problem**: iPhone stores rotation in EXIF, not pixels
**Solution**: Read EXIF and apply rotation
**Result**: Images display correctly aligned

### 3. Resizing to Fixed Size
**Problem**: CNNs require fixed input dimensions
**Solution**: Resize all to 256×256 with padding
**Result**: Can batch images for training, memory efficient

### 4. RGB Color Space Conversion
**Problem**: Different formats use BGR, RGBA, grayscale
**Solution**: Convert everything to RGB
**Result**: Model sees consistent 3-channel images

### 5. Blur Detection
**Problem**: Blurry images don't show disease patterns clearly
**Solution**: Reject images with blur_score < 100
**Result**: Model trains on clear, informative images

### 6. Brightness Checking
**Problem**: Dark/overexposed images lose information
**Solution**: Reject extreme brightness
**Result**: Good lighting conditions for disease visibility

### 7. Duplicate Detection
**Problem**: Same image in train AND test = data leakage
**Solution**: Identify and remove duplicates
**Result**: Honest model evaluation, no artificial accuracy boost

### 8. Stratified Splitting
**Problem**: Random split may have class imbalance
**Solution**: Maintain proportions in each split
**Result**: Fair model evaluation on representative data

### 9. Cross-Device Splitting
**Problem**: Model may learn device characteristics
**Solution**: Test on different device than training
**Result**: Real-world applicability verified

---

## 🚨 Best Practices & Common Mistakes

### ✓ BEST PRACTICES

#### 1. Always Verify Cross-Device Accuracy
```python
# DO THIS:
train_iphone = dataset[device == "iPhone"]
test_android = dataset[device == "Android"]

# Results:
within_device_acc = 92%
cross_device_acc = 82%  # 10% drop - acceptable

# If cross_device_acc 75% or less:
# → Model learned device characteristics
# → Won't work in real world with different phones
```

#### 2. Use Proper Split Assignment
```python
# DO THIS:
# Never touch test set during training
# Only use training set for training
# Only use validation set for hyperparameter tuning
# Only use test set for final evaluation

# DON'T DO THIS:
# Check test accuracy during training
# Use test set for anything except final evaluation
```

#### 3. Document Preprocessing Decisions
```python
# Record in README or paper:
- Which images were rejected and why
- Threshold settings and justification
- Quality statistics (% rejected due to blur, etc.)
- Cross-device accuracy results
```

#### 4. Check for Data Leakage
```python
# Verify:
assert len(train_set & test_set) == 0  # No overlap
assert len(duplicate_groups) > 1 implies "no cross-split duplicates"

# Your preprocessing automatically prevents this!
```

### ✗ COMMON MISTAKES

#### Mistake 1: Ignoring Device Characteristics
```python
# DON'T DO THIS:
# Train only on iPhone, test only on iPhone
# Project as "trained on Agricultural dataset"

# CORRECT:
# Train on iPhone, test on Android (and vice versa)
# Report cross-device accuracy
# Demonstrate model generalizes across devices
```

#### Mistake 2: Too Strict Quality Thresholds
```python
# DON'T DO THIS:
BLUR_THRESHOLD = 500  # Too strict
# Result: 50% of images rejected, too few remaining

# CORRECT:
BLUR_THRESHOLD = 100  # Reasonable
# Result: ~15-20% rejection rate
```

#### Mistake 3: Class Imbalance Not Addressed
```python
# DON'T DO THIS:
# Collect: 100 healthy, 100 panama_wilt, 50 sigatoka, 20 potassium
# Model learns to always predict "healthy" (80% accuracy)

# CORRECT:
# Ensure balanced collection: ~100 of each disease
# Or use class weights in model training
```

#### Mistake 4: Single Photographer Bias
```python
# DON'T DO THIS:
# Vedant collected all "healthy" images
# Sagar collected all "diseased" images

# CORRECT:
# Each photographer: every disease type
# Model learns disease patterns, not photographer technique
```

#### Mistake 5: Not Verifying Dataset Before Training
```python
# DON'T DO THIS:
# Preprocess data, immediately start training model

# CORRECT:
# python scripts/verify_dataset.py  # Check quality
# python scripts/analyze_bias.py    # Check for bias
# Only then: start training model
```

---

## 📊 Cross-Device Validation Guide

### Why It Matters

Agricultural ML models often fail in real-world deployment because:
1. Models trained on iPhone images learn iPhone sensor characteristics
2. When deployed on Android phone, accuracy drops significantly
3. Farmers report "model doesn't work on my phone"

### How to Verify

#### Step 1: Prepare Cross-Device Splits
```bash
# Pipeline automatically creates:
# - iphone_train_android_test
# - android_train_iphone_test
# - within_device (baseline)
```

#### Step 2: Train Models
```python
# Train Model 1: iPhone data
model1 = train_model(iphone_train_data)
within_device_acc = evaluate(model1, iphone_test_data)  # ~90%
cross_device_acc = evaluate(model1, android_test_data)   # ? %

# Train Model 2: Android data  
model2 = train_model(android_train_data)
within_device_acc = evaluate(model2, android_test_data)  # ~90%
cross_device_acc = evaluate(model2, iphone_test_data)    # ? %
```

#### Step 3: Interpret Results
```
IDEAL RESULTS:
- Model 1 on iPhone: 90% (within-device baseline)
- Model 1 on Android: 88% (2% drop - device characteristics negligible)

WARNING SIGNS:
- Model 1 on iPhone: 90%
- Model 1 on Android: 75% (15% drop - significant device bias!)
- → Model learned iPhone camera characteristics
- → Will fail deployment on different devices

ACTION:
- Collect more balanced device data
- Use techniques to make model device-agnostic
- Consider domain adaptation methods
```

---

## 🔍 Bias Detection Guide

### Run Bias Analysis
```bash
python scripts/analyze_bias.py
```

### What to Look For

#### Device Bias
```
GOOD: iPhone 45%, Android 55%
      Each disease represented in both devices
      
BAD:  iPhone 90%, Android 10%
      All healthy leaves from iPhone, diseased from Android
```

#### Contributor Bias
```
GOOD: Each contributor photographed all disease types
      images roughly balanced

BAD:  Vedant: all healthy leaves
      Sagar: all diseased leaves
      → Model learns "Vedant_photostyle = healthy"
```

#### Quality Consistency
```
GOOD: All devices have similar blur scores
      Blur_iphone mean: 150, Blur_android mean: 148
      
BAD:  Blur_iphone mean: 200, Blur_android mean: 50
      → One device produces images model can't read
```

---

## 🛠️ Troubleshooting

### Issue: "Module not found" errors
```python
# Solution 1: Ensure you're in project root
cd /path/to/MiniProject
python scripts/run_pipeline.py

# Solution 2: Check Python path
import sys
print(sys.path)
# Should include project root

# Solution 3: Reinstall packages
pip install -r requirements.txt --force-reinstall
```

### Issue: HEIC images not converting
```python
# Problem: pillow-heif not installed
# Solution:
pip install pillow-heif
# On Windows, might need: pip install pillow-heif --upgrade

# Verify:
from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()
```

### Issue: "Too many images rejected"
```python
# If >30% rejection rate, check:

# 1. BLUR_THRESHOLD too strict?
BLUR_THRESHOLD = 100  # Try 80-120

# 2. BRIGHTNESS too strict?
MIN_BRIGHTNESS = 40   # Try 30-50
MAX_BRIGHTNESS = 240  # Try 220-255

# 3. Check a sample of rejected images:
# Are they actually bad quality?

# Rerun with adjusted thresholds
```

### Issue: "Not enough images after duplicate removal"
```python
# Problem: Many duplicates detected
# Reasons:
# 1. Multiple photos of same leaf
# 2. Image compression variations
# 3. Slight crop/rotation variations

# Check:
DUPLICATE_THRESHOLD = 0.90  # Try 0.95 (stricter)

# This keeps more variation as separate images
```

### Issue: Google Colab storage exceeded
```python
# Problem: Processed images too large
# Solutions:

# 1. Reduce JPEG_QUALITY
JPEG_QUALITY = 85  # from 90

# 2. Use smaller image size (depends on network)
TARGET_IMAGE_SIZE = (224, 224)  # from 256x256

# 3. Store only processed (remove original raw copies)
# Saves 50% space
```

---

## 📝 Next Steps: Model Training

After preprocessing:

### 1. Load Data
```python
import pandas as pd
from pathlib import Path

# Load metadata
metadata = pd.read_csv("dataset/metadata/image_metadata.csv")

# Load images
train_data = load_from_split("dataset/split/train")
val_data = load_from_split("dataset/split/val")
test_data = load_from_split("dataset/split/test")
```

### 2. Apply Augmentation (Optional)
```python
# During preprocessing: images standardized (no augmentation)
# During training: apply augmentation

from tensorflow.keras.preprocessing.image import ImageDataGenerator

datagen = ImageDataGenerator(
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2]
)
```

### 3. Build and Train Model
```python
from tensorflow.keras.applications import ResNet50

model = ResNet50(weights='imagenet', include_top=False)
# Add custom head for 4 disease classes
# Fine-tune on your dataset
```

### 4. Cross-Device Evaluation
```python
# Train on iPhone, evaluate on Android
model_iphone = train(iphone_train_data)
acc_iphone = evaluate(model_iphone, iphone_test_data)
acc_cross = evaluate(model_iphone, android_test_data)

# Document results in paper/report
```

---

## 📚 References

- **Blur Detection**: Laplacian Variance - https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
- **Perceptual Hashing**: ImageHash - https://github.com/JohannesBuchner/imagehash
- **Cross-Device Domain Adaptation**: Transfer learning techniques
- **Agricultural ML Best Practices**: FAO and academic papers

---

## 📄 Citation

If using this pipeline in research:
```bibtex
@software{banana_leaf_preprocessing_2024,
  title={Banana Leaf Disease Dataset Preprocessing Pipeline},
  author={Your Name},
  year={2024},
  url={https://github.com/yourname/banana-leaf-disease}
}
```

---

## 📞 Support

For issues or questions:
1. Check `Troubleshooting` section above
2. Review configuration settings in `config/config.py`
3. Run verification: `python scripts/verify_dataset.py`
4. Run bias analysis: `python scripts/analyze_bias.py`

---

**Good luck with your research! 🍌🌿**
