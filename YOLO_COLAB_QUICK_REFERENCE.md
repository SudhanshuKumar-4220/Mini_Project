# 🚀 YOLO Disease Detection - Google Colab Quick Reference

## ⚡ 60-Second Quick Start

1. **Open Colab**: https://colab.research.google.com
2. **Upload Notebook**: `yolo_disease_detection_colab.ipynb`
3. **Enable GPU**: Runtime → Change runtime type → GPU
4. **Run Cells**: Top to bottom, wait for each to complete
5. **Download Results**: From Google Drive when done

**Total Time: 2-3 hours with GPU enabled**

---

## 📋 CELL-BY-CELL CHECKLIST

- [ ] **CELL 1** (2-3 min): Mount Drive & Install
  - Run and wait for "✅ All imports successful!"
  
- [ ] **CELL 2** (1-2 min): Load Dataset
  - Displays sample images from your dataset
  
- [ ] **CELL 3** (30-45 min): **Augmentation Pipeline** ⏳
  - CRITICAL: Creates 6000-8000 images
  - Watch for progress updates
  - DO NOT INTERRUPT
  
- [ ] **CELL 4** (5 min): Prepare YOLO Format
  - Organizes data for training
  
- [ ] **CELL 5** (45-90 min): **Train YOLO Model** ⏳
  - CRITICAL: Main training happens here
  - Watch for epoch progress (1/50, 2/50, etc.)
  - DO NOT CLOSE BROWSER
  
- [ ] **CELL 6** (5-10 min): Run Inference
  - Shows disease predictions on test images
  
- [ ] **CELL 7** (3-5 min): Evaluate Results
  - Accuracy, confusion matrix, metrics
  
- [ ] **CELL 8** (1 min): Summary & Download
  - Lists all saved files

---

## 🎯 CRITICAL SETTINGS TO MODIFY (IF NEEDED)

### In CELL 2 - Dataset Path
```python
DATASET_PATH = "/content/drive/MyDrive/Banana_Leaf_Processed"
```
**Change to your actual folder path if different**

### In CELL 3 - Augmentation Config
```python
TARGET_IMAGES_PER_CLASS = 1500  # Change for more/fewer images
IMAGES_PER_ORIGINAL = 5          # Augmentations per image
```

### In CELL 5 - Training Config
```python
EPOCHS = 50              # Increase to 100 for better accuracy
BATCH_SIZE = 16          # Reduce to 8 if out of memory
MODEL_SIZE = "n"         # "n" (fast), "s" (balanced), "m" (better)
```

---

## 📊 EXPECTED RESULTS

| Metric | Expected Value |
|--------|-----------------|
| Total Augmented Images | 6000-8000 |
| Training Images | ~4800-6400 |
| Validation Images | ~600-800 |
| Test Images | ~600-800 |
| Expected Accuracy | 85-95% |
| Training Time | 45-90 min (with GPU) |
| Model Size | ~50-150 MB |

---

## ⚠️ EMERGENCY TROUBLESHOOTING

### "No images found" in CELL 2
```
Action: 
1. Check your Google Drive folder path
2. Modify DATASET_PATH variable
3. Re-run CELL 2
```

### Out of Memory (OOM) Error in CELL 5
```
Action:
1. Stop the cell (square button)
2. Edit BATCH_SIZE from 16 → 8
3. Restart runtime (Runtime → Restart runtime)
4. Re-run CELL 5
```

### Training is very slow
```
Check: Runtime → Change runtime type
Make sure "GPU" is selected, not "CPU"
```

### "CUDA" or GPU errors
```
Action:
1. Restart runtime (Runtime → Restart runtime)
2. Re-run CELL 1
3. Re-run CELL 5
```

### Connection lost to Colab
```
Action:
1. Click "Reconnect" button (top right)
2. Training continues in background
3. Check progress in Google Drive
```

---

## 💾 OUTPUT FILE LOCATIONS

All results saved to Google Drive in: **YOLO_Results/**

Key files:
- `best_model.pt` - Trained YOLO model (use for predictions)
- `confusion_matrix.png` - Performance visualization
- `evaluation_report.txt` - Detailed metrics
- `inference_results.png` - Sample predictions
- `banana_disease_detector/` - Full training logs

---

## 🎮 USE TRAINED MODEL AFTER TRAINING

### Option 1: In Colab
```python
from ultralytics import YOLO

# Load model
model = YOLO('path/to/best_model.pt')

# Predict on new image
results = model.predict('path/to/leaf.jpg')

# Get prediction
disease = results[0].names[int(results[0].probs.top1)]
confidence = float(results[0].probs.top1conf)
print(f"Disease: {disease}, Confidence: {confidence:.2%}")
```

### Option 2: Locally (After downloading best_model.pt)
```python
from ultralytics import YOLO

model = YOLO('best_model.pt')
results = model.predict('leaf_image.jpg')
```

---

## 🔧 OPTIMIZATION TIPS

### For Better Accuracy (Slower)
```python
# In CELL 5, change:
EPOCHS = 100          # Instead of 50
MODEL_SIZE = "s"      # Instead of "n"
BATCH_SIZE = 32       # Instead of 16 (if memory allows)
```

### For Faster Training (Lower Accuracy)
```python
# In CELL 5, change:
EPOCHS = 30           # Instead of 50
MODEL_SIZE = "n"      # Keep as nano
BATCH_SIZE = 8        # Smaller batches
```

### For More Augmented Images
```python
# In CELL 3, change:
TARGET_IMAGES_PER_CLASS = 2000  # Instead of 1500
IMAGES_PER_ORIGINAL = 8         # Instead of 5
```

---

## 📱 KEYBOARD SHORTCUTS IN COLAB

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Run current cell |
| `Shift + Enter` | Run and move to next |
| `Ctrl + M + B` | Insert cell below |
| `Ctrl + M + A` | Insert cell above |
| `Ctrl + M + D` | Delete cell |
| `Ctrl + /` | Comment/uncomment line |

---

## 🆘 CONTACT & SUPPORT

### If Something Goes Wrong:
1. **Re-read error message** - Usually tells you the problem
2. **Check this troubleshooting guide**
3. **Restart runtime and re-run from CELL 1**
4. **Check Google Colab status page** for service issues

### Common Error Messages:

| Error | Meaning | Solution |
|-------|---------|----------|
| `FileNotFoundError` | File path is wrong | Update DATASET_PATH |
| `CUDA out of memory` | Not enough GPU RAM | Reduce BATCH_SIZE |
| `ConnectionError` | Lost internet | Click Reconnect |
| `ModuleNotFoundError` | Library not installed | Re-run CELL 1 |
| `FileExistsError` | Output folder exists | Clear Google Drive folder |

---

## ✅ FINAL CHECKLIST

Before running in Colab:
- [ ] Google Drive folder is accessible
- [ ] Have 10GB+ free space in Google Drive
- [ ] Know your dataset folder path
- [ ] Read through all cells (understand what they do)

During execution:
- [ ] GPU is enabled (check Runtime settings)
- [ ] Browser tab stays open (especially during CELL 3 & 5)
- [ ] No other heavy processes running
- [ ] Good internet connection

After completion:
- [ ] Download best_model.pt from Google Drive
- [ ] Save confusion matrix visualization
- [ ] Note the final accuracy percentage
- [ ] Test model on new images

---

## 📚 ADDITIONAL RESOURCES

### YOLO Documentation
- Official: https://docs.ultralytics.com/
- YOLOv8 Guide: https://docs.ultralytics.com/tasks/classify/

### Google Colab Tips
- Tips & Tricks: https://colab.research.google.com/notebooks/welcome.ipynb
- GPU Memory: https://colab.research.google.com/notebooks/faq.ipynb

### Data Augmentation
- Albumentations: https://albumentations.ai/docs/
- Examples: https://albumentations.ai/docs/examples/

---

## 🎓 LEARNING OUTCOMES

After running this notebook, you will have:
1. ✅ A dataset of 6000-8000 augmented banana leaf images
2. ✅ A trained YOLOv8 disease detection model
3. ✅ Model performance metrics and confusion matrix
4. ✅ A reusable model for disease prediction
5. ✅ Understanding of data augmentation techniques
6. ✅ Experience with YOLO training pipeline

---

**Last Updated: 2024**
**For issues or updates, refer to the main notebook documentation**
