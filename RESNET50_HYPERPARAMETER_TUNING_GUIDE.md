# ResNet50 Advanced Training: Hyperparameter Tuning Guide

## 🎯 Quick Reference: What To Adjust If Results Aren't 92%+

### Problem 1: Validation Accuracy Stuck at 85-88%

**Symptom**: Model stops improving after Stage 2, plateaus

**Diagnosis**:
```
Current Val Acc: 85%
Train-Val Gap: < 3% (not overfitting, just underfitting)
Status: Model is too conservative or underfitting
```

**Solutions** (in order):

#### Solution A: Increase Learning Rates (EASIEST)
```python
# Current
Stage 3: LR = 5e-05
Stage 4: LR = 2e-05

# Try this
Stage 3: LR = 1e-04 (2x higher)
Stage 4: LR = 5e-05 (2.5x higher)
```

#### Solution B: Extend Training Epochs
```python
# Current
Stage 4: epochs=20

# Try this
Stage 4: epochs=30 (or 40)
```

#### Solution C: Reduce Regularization
```python
# Current
L2 regularizer: l2(1e-4)

# Try this (less aggressive)
L2 regularizer: l2(5e-5)

# Or remove entirely (not recommended)
Dense(512, activation='relu')  # No L2
```

#### Solution D: Reduce Dropout
```python
# Current
Dropout(0.4)
Dropout(0.3)

# Try this (less aggressive)
Dropout(0.3)
Dropout(0.2)
```

---

### Problem 2: Train Accuracy Much Higher Than Val (>10% Gap)

**Symptom**: 
```
Train Accuracy: 95%
Val Accuracy: 83%
Gap: 12% ❌ OVERFITTING
```

**Diagnosis**: Model memorizing training data, not generalizing

**Solutions** (in order):

#### Solution A: Increase Dropout
```python
# Current
Dropout(0.4), Dropout(0.3)

# Try this
Dropout(0.5), Dropout(0.4)

# Or aggressive
Dropout(0.6), Dropout(0.5)
```

#### Solution B: Increase L2 Regularization
```python
# Current
kernel_regularizer=l2(1e-4)

# Try this (stronger)
kernel_regularizer=l2(5e-4)

# Very aggressive
kernel_regularizer=l2(1e-3)
```

#### Solution C: Reduce Batch Size Further
```python
# Current
BATCH_SIZE = 16

# Try this
BATCH_SIZE = 8

# Or
BATCH_SIZE = 4 (very aggressive)
```

#### Solution D: Increase Augmentation
```python
# In train_transforms, increase probabilities
A.Rotate(limit=30, p=0.9)  # Increase p from 0.7
A.RandomBrightnessContrast(brightness_limit=0.3, p=0.9)  # Increase p
A.CoarseDropout(max_holes=12, p=0.3)  # More dropout
```

#### Solution E: Increase Early Stopping Patience
```python
# Current
EarlyStopping(patience=20, min_delta=0.0005)

# Try this (looser - but might overfit)
EarlyStopping(patience=15, min_delta=0.001)
# Requires 0.1% improvement instead of 0.05%
```

---

### Problem 3: Training Unstable (Loss Jumping Around)

**Symptom**:
```
Epoch 1: Loss = 2.1, Acc = 0.35
Epoch 2: Loss = 1.2, Acc = 0.65 (wild jump)
Epoch 3: Loss = 2.5, Acc = 0.40 (jumped back!)
```

**Diagnosis**: Learning rate too high or batch size too small

**Solutions**:

#### Solution A: Reduce Learning Rate
```python
# Current
STAGE3_LR = 5e-05

# Try this
STAGE3_LR = 2e-05

# Or very conservative
STAGE3_LR = 1e-05 (original!)
```

#### Solution B: Increase Batch Size
```python
# Current
BATCH_SIZE = 16

# Try this
BATCH_SIZE = 24

# Or
BATCH_SIZE = 32 (original)
```

#### Solution C: Increase Beta1 (Momentum)
```python
# Current
optimizer=Adam(learning_rate=LR, beta_1=0.9, beta_2=0.999)

# Try this (more stable, slower)
optimizer=Adam(learning_rate=LR, beta_1=0.95, beta_2=0.999)

# Or
optimizer=Adam(learning_rate=LR, beta_1=0.99, beta_2=0.999)
```

---

### Problem 4: Model Not Training (Accuracy Stays ~25%)

**Symptom**:
```
All epochs: Train Acc ≈ 0.25, Val Acc ≈ 0.25
(Random guessing for 4 classes = 25%)
Status: Model not learning at all!
```

**Diagnosis**: Learning rate too low, optimizer issue, or data problem

**Solutions**:

#### Solution A: Increase Base Learning Rate SIGNIFICANTLY
```python
# Current
LEARNING_RATE = 0.001

# Try this
LEARNING_RATE = 0.01 (10x higher!)

# Test if learning starts...
```

#### Solution B: Check Data Loading
```python
# Verify data is loading correctly
print(f"Sample batch shape: {train_sequence[0][0].shape}")
print(f"Sample labels: {train_sequence[0][1][:5]}")
print(f"Label range: {min(train_sequence[0][1])} to {max(train_sequence[0][1])}")
# Labels should be 0, 1, 2, 3 (not 0-1 normalized!)
```

#### Solution C: Check Model Compilation
```python
# Make sure model is actually compiled
print(model.optimizer)  # Should not be None
print(model.compiled_loss)  # Should exist
```

---

## 🔧 Hyperparameter Tuning Matrix

### For Maximum Accuracy (92%+):
```
Best Settings if you have TIME:
├── Batch Size: 8 (very small, but slow)
├── L2 Lambda: 5e-5 (moderate)
├── Dropout: 0.4, 0.3 (current)
├── Epochs: Stage4 = 40 (not 20)
└── LR: 0.001, 0.0002, 0.00005, 0.00001

Expected: 92-94% accuracy
Time: 45+ minutes
```

### For Fast Training (92% in ~20 min):
```
Current Settings:
├── Batch Size: 16
├── L2 Lambda: 1e-4
├── Dropout: 0.4, 0.3
├── Epochs: 20 per stage
└── LR: As specified

Expected: 91-93% accuracy
Time: 20-25 minutes
```

### For Best Generalization (No overfitting):
```
Most Conservative:
├── Batch Size: 8
├── L2 Lambda: 5e-4 (high!)
├── Dropout: 0.5, 0.4 (high!)
├── Epochs: 30 per stage
├── Augmentation: More aggressive
└── LR: Lower (0.0001, 2e-05, 5e-06, 1e-06)

Expected: 88-90% accuracy (safer)
Gap: < 3% (excellent generalization)
Time: 40+ minutes
```

---

## 📊 Monitoring Guide

### What Each Metric Means

#### Accuracy
```
0.0 - 0.2: Model is guessing (4 classes = 0.25 baseline)
0.2 - 0.5: Model learning but poorly
0.5 - 0.7: Learning happening
0.7 - 0.8: Good progress
0.8 - 0.9: Excellent progress
0.9 - 1.0: Near-perfect (might be overfitting!)
```

#### Loss
```
Lower is better (0 = perfect)
Typical progression: 2.5 → 1.5 → 0.8 → 0.5
If loss stops decreasing: Learning plateau detected
If loss suddenly increases: Overfitting or LR issue
```

#### Train-Val Gap
```
Gap = |Train Acc - Val Acc|
< 0.02 (2%): Excellent balance ✅
0.02-0.05: Good balance ✅
0.05-0.10: Slight overfitting ⚠️
0.10-0.15: Moderate overfitting ❌
> 0.15: Severe overfitting ❌❌
```

---

## 🎯 Stage-Specific Tuning

### Stage 1 Adjustments
**If stuck at ~60%**:
```python
# Increase base LR
LEARNING_RATE = 0.002 (from 0.001)

# Extend epochs
epochs=25 (from 20)

# Or reduce dropout
x = Dropout(0.3)(x)  # from 0.4
```

### Stage 2 Adjustments
**If accuracy not improving from Stage 1**:
```python
# Increase learning rate reduction
STAGE2_LR = 0.0005 (from 0.0002)

# Or extend epochs
epochs=35 (from 25)

# Or unfreeze more layers
for layer in base_model.layers[-125:]:  # 125 instead of 100
    layer.trainable = True
```

### Stage 3 Adjustments
**If accuracy plateaus**:
```python
# KEY: Increase LR significantly
STAGE3_LR = 1e-04 (from 5e-05)  # 2x!

# Extend patience
patience=30 (from 20)

# Or reduce dropout
Dropout(0.3), Dropout(0.2) (from 0.4, 0.3)
```

### Stage 4 Adjustments
**If still not reaching 92%**:
```python
# Increase epochs significantly
epochs=40 (from 20)

# Increase LR
STAGE4_LR = 5e-05 (from 2e-05)

# Or reduce regularization
kernel_regularizer=l2(5e-5) (from 1e-4)
```

---

## ⚠️ Common Mistakes To Avoid

### ❌ Mistake 1: Changing Too Many Things at Once
```
Don't do: Change LR, batch size, dropout, and epochs all at once
Do this: Change ONE thing at a time, train, then evaluate
```

### ❌ Mistake 2: Stopping Early If First Stage Low
```
Don't worry if Stage 1 = 60-65%
This is NORMAL when base is frozen!
Each stage should improve significantly.
```

### ❌ Mistake 3: Using Same LR for All Stages
```
Don't do: 0.0001 for all stages (too low overall)
Do this: Progressive decay 0.001 → 0.00002
```

### ❌ Mistake 4: Monitoring Wrong Metrics
```
Don't use: val_loss (indirect)
Do use: val_accuracy (direct)
```

### ❌ Mistake 5: Early Stopping Too Aggressive
```
Don't use: patience=3 (stops immediately)
Do use: patience=20-25 (allows convergence)
```

---

## 📈 Decision Tree for Tuning

```
Is Val Accuracy >= 92%?
├─ YES → ✅ DONE! You've achieved the goal!
└─ NO → Is train-val gap < 5%?
    ├─ YES (underfitting) → Increase LR and epochs
    │   └─ Still < 92%? → Reduce regularization (dropout, L2)
    │
    └─ NO (overfitting, gap > 5%) → Increase regularization
        ├─ Try: Increase dropout first (fastest)
        ├─ Then: Increase L2 regularization
        └─ Finally: Reduce batch size if needed
```

---

## ✅ Checklist Before Running Training

- [ ] Batch size set to 16 (or adjusted as needed)
- [ ] Learning rates defined correctly
- [ ] L2 regularization added to dense layers
- [ ] BatchNormalization added
- [ ] Dropout configured (0.4, 0.3)
- [ ] Early stopping patience set to 20-25
- [ ] ReduceLROnPlateau patience set to 4-5
- [ ] Monitoring val_accuracy (not val_loss)
- [ ] BiasVarianceMonitor callback added
- [ ] Augmentation pipeline enhanced
- [ ] Data loading tested (correct shapes)
- [ ] GPU available (check with tf.config.list_physical_devices('GPU'))

---

## 🚀 Final Tips

1. **Start with current settings** - They're already optimized for 92%+
2. **If not working, increase LR first** - Most common bottleneck
3. **Monitor train-val gap closely** - Key to avoiding bias/variance
4. **Be patient during Stage 3-4** - These take time to converge
5. **Trust the BiasVarianceMonitor** - It tells you if something's wrong
6. **Save best model checkpoint** - Already done in code

**Good luck! You've got this! 🎯**
