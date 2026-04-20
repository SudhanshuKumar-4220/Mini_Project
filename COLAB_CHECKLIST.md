# 🚀 Colab Execution Checklist

Before running `colab_pipeline.ipynb`, verify everything is set up correctly:

## ✅ Google Drive Setup

- [ ] **Folder Structure Created:**
  ```
  MyDrive/
  ├── Mini_Project_Dataset/          ← Your photos must be here
  │   ├── healthy_leaves/
  │   │   ├── Vedant_Primary/
  │   │   ├── Vedant_Secondary/
  │   │   ├── Sagar/
  │   │   ├── Subodh/
  │   │   └── Sudhanshu/
  │   ├── panama_wilt/
  │   ├── potassium_deficiency/
  │   └── sigatoka/
  └── MiniProject/                   ← Output will be saved here
      └── Processed_Output/          ← Auto-created by notebook
  ```

- [ ] **Dataset Photos Uploaded:**
  - [ ] All disease folders present (healthy_leaves, panama_wilt, potassium_deficiency, sigatoka)
  - [ ] Contributor subfolders created
  - [ ] Photos in correct contributor folders
  - [ ] File formats are HEIC, JPG, JPEG, or PNG

- [ ] **MiniProject Folder Created:**
  - [ ] `MyDrive/MiniProject/` folder exists (Processed_Output subfolder will be auto-created)

## 📋 Dataset Verification

- [ ] **Total Image Count Known:**
  - [ ] Approximately how many images total? __________
  - [ ] Which disease has most photos? __________
  - [ ] Which disease has least photos? __________

- [ ] **Device Distribution:**
  - [ ] Vedant_Primary (iPhone) - ____ photos
  - [ ] Vedant_Secondary (iPhone) - ____ photos
  - [ ] Sagar (Android) - ____ photos
  - [ ] Subodh (Android) - ____ photos
  - [ ] Sudhanshu (Android) - ____ photos

- [ ] **File Formats Check:**
  - [ ] HEIC files present? (iPhone photos)
  - [ ] JPG/JPEG files present? (Android photos)
  - [ ] PNG files present? (screenshots/other)

## 🎯 Colab Preparation

- [ ] **Have this open:**
  - [ ] Google Colab (colab.research.google.com)
  - [ ] Your Google Drive (drive.google.com)
  - [ ] README.md (for reference)
  - [ ] COLAB_QUICK_START.md (for troubleshooting)

- [ ] **Colab Runtime Selected:**
  - [ ] GPU enabled (if available - speeds up processing)
  - [ ] High RAM runtime recommended (if processing >500 images)

## ⚙️ Configuration Review

- [ ] **Quality Thresholds Appropriate:**
  - [ ] Blur threshold: 100 (adjust if too strict/loose)
  - [ ] Brightness: 40-240 (good for natural lighting)
  - [ ] Contrast: 15 (adjust if images too flat)
  - [ ] Note: Can adjust in Config cell if needed

- [ ] **Duplicate Threshold Set:**
  - [ ] Threshold: 0.90 (90% similarity = duplicate)
  - [ ] 0.80-0.85 = Stricter (catches more near-duplicates)
  - [ ] 0.90-0.95 = Lenient (only exact duplicates)

- [ ] **Split Ratios Acceptable:**
  - [ ] Train: 70% (main dataset)
  - [ ] Val: 15% (tuning hyperparameters)
  - [ ] Test: 15% (final evaluation)

## 📊 Expected Results

- [ ] **Processing Time Estimate:**
  - [ ] <100 images: 2-3 minutes
  - [ ] 100-500 images: 5-15 minutes
  - [ ] 500-1000 images: 15-30 minutes
  - [ ] 1000+ images: 30-60+ minutes

- [ ] **Disk Space Available:**
  - [ ] Google Drive has 2GB+ free (safe margin for outputs)
  - [ ] If low on space, consider archiving old files first

## 🔐 Permissions & Access

- [ ] **Google Account Ready:**
  - [ ] Signed into Google account with @gmail access
  - [ ] Can access Google Drive
  - [ ] Can create folders in Drive

- [ ] **Colab Access Confirmed:**
  - [ ] Can open Colab notebook
  - [ ] Can connect to runtime
  - [ ] Can execute cells

## 🎬 Pre-Execution Steps

1. [ ] **Verify Dataset One Last Time:**
   ```
   Open Google Drive → Mini_Project_Dataset
   - Do you see 4 disease folders?
   - Do you see photos in each folder?
   - Approximately how many total? 
   ```

2. [ ] **Take Screenshot:**
   - [ ] Take screenshot of Google Drive folder structure before running
   - [ ] This helps if you need to troubleshoot later

3. [ ] **Open Colab Notebook:**
   - [ ] Navigate to `notebooks/colab_pipeline.ipynb`
   - [ ] Click "Open with Google Colab"
   - [ ] Wait for notebook to load completely

4. [ ] **Create Shortcut (Optional):**
   - [ ] Add Colab notebook to Google Drive favorites
   - [ ] Makes it easier to find later

## 💡 Pro Tips

- **Checkpoint Your Progress:**
  - Before running Section 6 (Main Processing), save a checkpoint
  - If processing fails halfway, you won't lose earlier steps

- **Memory Monitoring:**
  - Keep `Runtime → Run All Setup Cells` as your first step
  - This installs dependencies before processing

- **Multiple Runs:**
  - You can run the notebook multiple times
  - Later runs will overwrite previous outputs
  - If you want to keep results, download before re-running

## 🚨 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| `Dataset not found` | Verify Mini_Project_Dataset in MyDrive root |
| `Permission denied` | Re-run Google Drive mounting cell |
| `Out of memory` | Use High RAM runtime or process fewer images |
| `File format not supported` | Ensure files are HEIC/JPG/JPEG/PNG only |
| `Slow processing` | Enable GPU in runtime settings |

## ✨ Success Indicators

After running, you'll see:

1. ✅ **Logs showing:**
   - "✓ Dataset found"
   - Processing percentages (25%, 50%, 75%, 100%)
   - "✓ Dataset split completed"

2. ✅ **Output Files Created:**
   - `processed_dir/` with converted images
   - `split_dir/` with train/val/test subfolders
   - `metadata_dir/` with CSV and JSON files

3. ✅ **Summary Displayed:**
   - Total images processed
   - Quality filtering results
   - Duplicate count
   - Split distribution

## 🎓 Next Steps After Successful Run

1. **Analyze Results:**
   - Download `image_metadata.csv`
   - Review which images failed quality checks
   - Verify split distribution

2. **Adjust If Needed:**
   - If too many images filtered by quality, adjust thresholds
   - If duplicate count seems high, adjust duplicate threshold
   - Re-run with adjusted settings

3. **Prepare for Model Training:**
   - Your `split/train/`, `split/val/`, `split/test/` folders are ready
   - Use these for CNN model training
   - Reference: "Next Steps for Model Training" section in README.md

4. **Verify Cross-Device Validation:**
   - Check `cross_device_splits/` for device-specific splits
   - Use these to verify model isn't learning device characteristics

---

**Ready to start? Good luck! 🍌🍃** 

Questions? Refer to:
- 📖 README.md - Full documentation
- ⚡ COLAB_QUICK_START.md - Quick reference
- 🔧 Troubleshooting section above
