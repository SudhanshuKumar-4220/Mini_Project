# 🚀 ResNet50 Disease Detection - Quick Reference Guide

## ⚡ 60-Second Quick Start

**Key Difference from YOLO:**
- ✅ ResNet50 (not YOLO)
- ✅ Real-time augmentation (NO storage!)
- ✅ 1-2 hours (not 2-3 hours)
- ✅ Saves 4-5GB space

### Steps:
1. **Open Colab**: https://colab.research.google.com
2. **Upload Notebook**: `yolo_disease_detection_colab.ipynb` (same file, updated content)
3. **Enable GPU**: Runtime → Change runtime type → GPU
4. **Run Cells**: Top to bottom, wait for each
5. **Download**: From Google Drive when done

**Total Time: 1-2 hours with GPU enabled**

---

## 🆚 ResNet50 vs YOLO (What Changed?)

| Feature | YOLO | ResNet50 |
|---------|------|---------|
| **Model** | YOLOv8n (detection) | ResNet50 (classification) |
| **Training Time** | 45-90 min | 45-60 min |
| **Augmentation** | Stores 6000-8000 images | Real-time (no storage!) |
| **Storage Needed** | 4-5 GB | <1 GB |
| **Total Time** | 2-3 hours | 1-2 hours ⚡ |
| **Accuracy** | 85-95% | 90-95% |
| **Transfer Learning** | Limited | Full ImageNet (50M params) |
| **Speed** | Medium | Fast + Efficient |

**Result: 33% faster + uses 80% less storage!**

---

## 📋 CELL-BY-CELL CHECKLIST

- [ ] **CELL 1** (2-3 min): Mount Drive & Install (TensorFlow, ResNet50)
- [ ] **CELL 2** (1-2 min): Load Dataset
- [ ] **CELL 3** (2-3 min): Create Augmentation Pipeline (on-the-fly)
- [ ] **CELL 4** (2-3 min): Prepare Data (train/val/test split)
- [ ] **CELL 5** (45-60 min): **Train ResNet50** ⏳ (on-the-fly augmentation)
- [ ] **CELL 6** (5-10 min): Run Inference (predictions)
- [ ] **CELL 7** (3-5 min): Evaluate Results
- [ ] **CELL 8** (1 min): Summary & Download

---

## 🎯 CRITICAL SETTINGS TO MODIFY (IF NEEDED)

### In CELL 2 - Dataset Path
```python
DATASET_PATH = "/content/drive/MyDrive/Banana_Leaf_Processed"
```

### In CELL 5 - Training Config
```python
EPOCHS = 30              # Increase to 50+ for better accuracy
BATCH_SIZE = 32          # Reduce to 16 if out of memory
LEARNING_RATE = 0.001    # Learning rate
TARGET_SIZE = (224, 224) # ResNet50 standard input size
```

---

## 📊 EXPECTED RESULTS

| Metric | Expected Value |
|--------|-----------------|
| **Total Training Time** | 1-2 hours |
| **Storage Used** | <1 GB |
| **Expected Accuracy** | 90-95% |
| **Training Images** | ~70% of total |
| **Validation Images** | ~15% of total |
| **Test Images** | ~15% of total |
| **Model Size** | ~100-150 MB |

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
2. Edit BATCH_SIZE from 32 → 16
3. Restart runtime (Runtime → Restart runtime)
4. Re-run from CELL 1
```

### Training is very slow
```
Check: Runtime → Change runtime type
Make sure "GPU" is selected, not "CPU"
```

### "TensorFlow/CUDA" errors
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

All results saved to Google Drive in: **Root My Drive folder**

Key files:
- `ResNet50_Disease_Model.h5` - Trained ResNet50 model (download this!)
- `confusion_matrix.png` - Performance visualization
- `evaluation_report.txt` - Detailed metrics
- `inference_results.png` - Sample predictions
- `training_history.json` - Training metrics

---

## 🎮 USE TRAINED MODEL AFTER TRAINING

### Option 1: In Colab
```python
from tensorflow import keras
import cv2
import numpy as np

# Load model
model = keras.models.load_model('ResNet50_Disease_Model.h5')

# Predict on new image
img = cv2.imread('leaf.jpg')
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_resized = cv2.resize(img_rgb, (224, 224))
img_norm = img_resized.astype('float32') / 255.0
img_norm = (img_norm - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])

pred = model.predict(np.expand_dims(img_norm, axis=0))
disease = class_names[np.argmax(pred[0])]
confidence = float(np.max(pred[0]))

print(f"Disease: {disease}, Confidence: {confidence:.2%}")
```

### Option 2: Locally (After downloading)
```python
from tensorflow import keras
import cv2
import numpy as np

model = keras.models.load_model('ResNet50_Disease_Model.h5')
# Use same code as above
```

---

## 🔧 OPTIMIZATION TIPS

### For Better Accuracy (Longer training)
```python
# In CELL 5, change:
EPOCHS = 50               # Instead of 30
BATCH_SIZE = 16           # Instead of 32
LEARNING_RATE = 0.0005    # Lower learning rate
```
Result: 92-96% accuracy, 60-75 minutes training

### For Faster Completion (Lower accuracy)
```python
# In CELL 5, change:
EPOCHS = 15               # Instead of 30
BATCH_SIZE = 64           # Instead of 32
```
Result: 85-90% accuracy, 20-30 minutes training

---

## 📱 WHY REAL-TIME AUGMENTATION?

### Traditional Approach (Old YOLO way):
```
1. Generate 6000-8000 images → 30-45 minutes
2. Store on Google Drive → Uses 4-5 GB
3. Train model → 45-90 minutes
4. Total: 2-3 hours + 4-5 GB storage
```

### New Approach (ResNet50):
```
1. Define augmentation transforms → 2 minutes
2. Apply on-the-fly during training → 0 GB storage
3. Train model → 45-60 minutes
4. Total: 1-2 hours + <1 GB storage ✨
```

**Benefits:**
- ✅ 5x faster (no storage time)
- ✅ 80% less storage (4-5 GB saved!)
- ✅ Better training (new augmentations each epoch)
- ✅ More scalable (works with any dataset size)

---

## ✅ FINAL CHECKLIST

Before running in Colab:
- [ ] Google Drive folder is accessible
- [ ] Have 5+ GB free space (not 10+ anymore!)
- [ ] Know your dataset folder path
- [ ] GPU is enabled in Runtime settings

During execution:
- [ ] GPU is enabled (check Runtime settings)
- [ ] Browser tab stays open (especially CELL 5)
- [ ] Good internet connection
- [ ] Computer doesn't sleep

After completion:
- [ ] Download ResNet50_Disease_Model.h5
- [ ] Save confusion matrix image
- [ ] Note the final accuracy percentage
- [ ] Test model on new images

---

## 📊 QUICK STATS

- **Model**: ResNet50 (Pretrained on ImageNet)
- **Framework**: TensorFlow/Keras
- **Augmentation**: 5 strategies applied on-the-fly
- **Training**: 30 epochs (default)
- **Expected Accuracy**: 90-95%
- **Total Runtime**: 1-2 hours (GPU)
- **Storage Needed**: <1 GB (NO augmented storage!)
- **Output**: Trained .h5 model ready for inference

---

**This approach is significantly faster and more efficient than the YOLO version! 🚀**

Last Updated: 2024
