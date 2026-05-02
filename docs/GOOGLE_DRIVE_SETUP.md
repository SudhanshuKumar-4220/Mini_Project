# 📁 Google Drive Folder Structure - Setup Guide

## Required Directory Structure

Your Google Drive must have this exact structure for the Colab pipeline to work:

```
MyDrive/
│
├── Mini_Project_Dataset/                    🔴 REQUIRED - Your photos go here
│   │
│   ├── healthy_leaves/                      (Disease folder)
│   │   ├── Vedant_Primary/                  (Contributor subfolder - iPhone)
│   │   │   ├── photo_001.HEIC
│   │   │   ├── photo_002.HEIC
│   │   │   └── ... more photos
│   │   ├── Vedant_Secondary/                (Contributor subfolder - iPhone)
│   │   │   ├── photo_001.HEIC
│   │   │   └── ... more photos
│   │   ├── Sagar/                           (Contributor subfolder - Android)
│   │   │   ├── photo_001.jpg
│   │   │   └── ... more photos
│   │   ├── Subodh/                          (Contributor subfolder - Android)
│   │   │   ├── photo_001.JPG
│   │   │   └── ... more photos
│   │   └── Sudhanshu/                       (Contributor subfolder - Android)
│   │       ├── photo_001.jpeg
│   │       └── ... more photos
│   │
│   ├── panama_wilt/                         (Disease folder)
│   │   ├── Vedant_Primary/
│   │   │   └── ... photos
│   │   ├── Vedant_Secondary/
│   │   │   └── ... photos
│   │   ├── Sagar/
│   │   │   └── ... photos
│   │   ├── Subodh/
│   │   │   └── ... photos
│   │   └── Sudhanshu/
│   │       └── ... photos
│   │
│   ├── potassium_deficiency/                (Disease folder)
│   │   ├── Vedant_Primary/
│   │   │   └── ... photos
│   │   ├── Vedant_Secondary/
│   │   │   └── ... photos
│   │   ├── Sagar/
│   │   │   └── ... photos
│   │   ├── Subodh/
│   │   │   └── ... photos
│   │   └── Sudhanshu/
│   │       └── ... photos
│   │
│   └── sigatoka/                            (Disease folder)
│       ├── Vedant_Primary/
│       │   └── ... photos
│       ├── Vedant_Secondary/
│       │   └── ... photos
│       ├── Sagar/
│       │   └── ... photos
│       ├── Subodh/
│       │   └── ... photos
│       └── Sudhanshu/
│           └── ... photos
│
└── MiniProject/                             🟢 REQUIRED - Output saved here
    └── Processed_Output/                    (Auto-created by script)
        ├── processed/                       Images converted to JPEG
        │   ├── healthy_leaves/
        │   ├── panama_wilt/
        │   ├── potassium_deficiency/
        │   └── sigatoka/
        ├── split/                           Train/Val/Test splits
        │   ├── train/
        │   │   ├── healthy_leaves/
        │   │   ├── panama_wilt/
        │   │   ├── potassium_deficiency/
        │   │   └── sigatoka/
        │   ├── val/
        │   │   ├── healthy_leaves/
        │   │   ├── panama_wilt/
        │   │   ├── potassium_deficiency/
        │   │   └── sigatoka/
        │   ├── test/
        │   │   ├── healthy_leaves/
        │   │   ├── panama_wilt/
        │   │   ├── potassium_deficiency/
        │   │   └── sigatoka/
        │   ├── cross_device_iphone_train/   Device-specific splits
        │   ├── cross_device_android_train/
        │   ├── cross_device_iphone_test/
        │   └── cross_device_android_test/
        └── metadata/                        CSV and JSON reports
            ├── image_metadata.csv
            ├── dataset_statistics.json
            ├── device_distribution.json
            ├── quality_report.txt
            └── duplicate_report.txt
```

## ✅ Setup Instructions

### Step 1: Create Folder Structure Manually

If you prefer to create folders manually:

```
1. Open Google Drive (drive.google.com)
2. Create "Mini_Project_Dataset" folder in MyDrive root
3. Inside, create 4 disease folders:
   - healthy_leaves
   - panama_wilt
   - potassium_deficiency
   - sigatoka
4. Inside each disease folder, create 5 contributor subfolders:
   - Vedant_Primary (iPhone)
   - Vedant_Secondary (iPhone)
   - Sagar (Android)
   - Subodh (Android)
   - Sudhanshu (Android)
5. Create "MiniProject" folder in MyDrive root
   (Processed_Output subfolder will be auto-created)
```

### Step 2: Upload Your Photos

```
1. Collect all your banana leaf photos
2. Organize by disease class
3. Organize by contributor
4. Upload to corresponding folders

Example:
  - Vedant_Primary's healthy leaf photos → 
    Mini_Project_Dataset/healthy_leaves/Vedant_Primary/
  
  - Sagar's panama wilt photos → 
    Mini_Project_Dataset/panama_wilt/Sagar/
```

### Step 3: Verify Structure

```
Before running Colab:
1. Open Mini_Project_Dataset in Google Drive
2. Verify you see 4 disease folders ✓
3. Open each disease folder
4. Verify you see 5 contributor subfolders ✓
5. Spot-check that photos are in correct folders ✓
```

---

## 🎯 Naming Conventions (IMPORTANT)

### Folder Names (Case-Sensitive)

**Disease Folders - Must be EXACT:**
```
✅ CORRECT:
  - healthy_leaves
  - panama_wilt
  - potassium_deficiency
  - sigatoka

❌ WRONG:
  - Healthy_Leaves (capital H)
  - healthy leaf (space, singular)
  - Panama_wilt (P/w mismatch)
  - deficiency (missing potassium_)
```

**Contributor Folders - Must be EXACT:**
```
✅ CORRECT:
  - Vedant_Primary
  - Vedant_Secondary
  - Sagar
  - Subodh
  - Sudhanshu

❌ WRONG:
  - vedant_primary (lowercase v)
  - V_Primary (single letter)
  - VedantPrimary (no underscore)
  - Vedant Primary (space instead of underscore)
```

### Photo File Names (Any format OK)

Photos can have any name, as long as extension is correct:

```
✅ SUPPORTED:
  - photo_001.HEIC
  - banana_leaf_1.JPG
  - P1000123.jpg
  - scan_20231101_001.jpeg
  - disease_sample.png
  - IMG_2024_01_15.heic

❌ NOT SUPPORTED:
  - photo.pdf
  - image.bmp
  - scan.tiff
  - photo.gif (GIF supported but not recommended)
```

---

## 📊 Example Dataset Structure

Here's a realistic example:

```
MyDrive/Mini_Project_Dataset/

healthy_leaves/
├── Vedant_Primary/              (iPhone - 45 photos)
│   ├── IMG_0001.HEIC
│   ├── IMG_0002.HEIC
│   └── ... (43 more)
├── Vedant_Secondary/            (iPhone - 38 photos)
│   ├── photo_1.HEIC
│   └── ... (37 more)
├── Sagar/                        (Android - 52 photos)
│   ├── Photo_2024_01.jpg
│   └── ... (51 more)
├── Subodh/                       (Android - 41 photos)
│   └── ... (41 photos)
└── Sudhanshu/                    (Android - 39 photos)
    └── ... (39 photos)

panama_wilt/
├── Vedant_Primary/              (42 photos)
├── Vedant_Secondary/            (35 photos)
├── Sagar/                        (48 photos)
├── Subodh/                       (44 photos)
└── Sudhanshu/                    (36 photos)

potassium_deficiency/
├── Vedant_Primary/              (50 photos)
├── Vedant_Secondary/            (46 photos)
├── Sagar/                        (55 photos)
├── Subodh/                       (51 photos)
└── Sudhanshu/                    (47 photos)

sigatoka/
├── Vedant_Primary/              (48 photos)
├── Vedant_Secondary/            (44 photos)
├── Sagar/                        (52 photos)
├── Subodh/                       (49 photos)
└── Sudhanshu/                    (45 photos)

Total: ~970 photos across 4 diseases, 5 contributors
```

---

## 🔧 Device Mapping Reference

The pipeline automatically recognizes devices based on contributor:

```
iPhone (Photos saved as HEIC):
├── Vedant_Primary
└── Vedant_Secondary

Android (Photos saved as JPG/JPEG):
├── Sagar
├── Subodh
└── Sudhanshu
```

This mapping is in `colab_pipeline.ipynb` Config section:
```python
DEVICE_MAPPING = {
    "Vedant_Primary": "iPhone",
    "Vedant_Secondary": "iPhone",
    "Sagar": "Android",
    "Subodh": "Android",
    "Sudhanshu": "Android"
}
```

---

## 📝 Troubleshooting Setup Issues

### Problem: "Dataset not found" in Colab

**Cause:** Folder not in correct location

**Solution:**
```
1. Check that folder is named EXACTLY: Mini_Project_Dataset
2. Check that it's in Google Drive ROOT (MyDrive)
3. NOT in a subfolder like Documents/Mini_Project_Dataset
4. NOT with different capitalization
```

### Problem: "Contributor folder missing"

**Cause:** Contributor subfolder not created or misnamed

**Solution:**
```
1. Verify all 5 subfolders exist:
   ✓ Vedant_Primary
   ✓ Vedant_Secondary  
   ✓ Sagar
   ✓ Subodh
   ✓ Sudhanshu
2. Check exact spelling and capitalization
3. Folders must use underscore (_) not space
```

### Problem: "Permission Denied" in Colab

**Cause:** Google Drive permissions issue

**Solution:**
```
1. Ensure you're signed into the same Google account
2. Verify Mini_Project_Dataset is readable
   (Right-click → Share → Check permissions)
3. Try re-running the mount cell in Colab
```

### Problem: "No images found"

**Cause:** Photos not in correct subfolders

**Solution:**
```
1. Photos must be in contributor subfolders
   ✓ Correct: Mini_Project_Dataset/healthy_leaves/Vedant_Primary/photo.HEIC
   ✗ Wrong: Mini_Project_Dataset/photo.HEIC
2. Check folder structure matches the template above
3. Verify file extensions are HEIC/JPG/JPEG/PNG
```

---

## ✨ Once You're Ready

1. ✅ Folder structure created
2. ✅ All disease folders exist
3. ✅ All contributor subfolders exist
4. ✅ Photos uploaded and organized
5. ✅ MiniProject folder created
6. 🚀 **Ready to run Colab pipeline!**

---

**Pro Tips:**
- 💾 Organize photos locally first, then bulk upload to Google Drive
- 🔍 Use Google Drive's search to verify specific photos are where you expect
- 📋 Keep a spreadsheet of contributor photo counts for verification
- ⏱️ If uploading many photos, allow extra time for Google Drive sync

**Questions?** See README.md or COLAB_QUICK_START.md
