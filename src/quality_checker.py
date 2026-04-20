"""
Quality Checking Module - Detect problematic images.

This module implements quality assessment for images:
- Blur detection (Laplacian variance)
- Brightness analysis
- Contrast assessment
- Corrupt image detection
"""

import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class QualityChecker:
    """Assess image quality and identify problematic images."""
    
    def __init__(self, blur_threshold=100, min_brightness=40, max_brightness=240, min_contrast=15):
        """
        Initialize QualityChecker with quality thresholds.
        
        Args:
            blur_threshold (float): Laplacian variance threshold for blur
            min_brightness (int): Minimum average pixel brightness
            max_brightness (int): Maximum average pixel brightness
            min_contrast (int): Minimum standard deviation of pixel values
        """
        self.blur_threshold = blur_threshold
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_contrast = min_contrast
    
    def check_image_quality(self, image, image_path=None):
        """
        Comprehensive quality check on single image.
        
        WHY: This catches problematic images early:
        - Blurry images don't show disease patterns clearly
        - Too dark/bright images lose information
        - Low contrast images are uninformative
        - Ensure only quality images enter the model
        
        Args:
            image (np.ndarray): Image to check (as loaded by cv2 or PIL)
            image_path (str): Path for logging purposes
            
        Returns:
            dict: Quality metrics and assessment
            {
                "is_quality": bool,
                "blur_score": float,
                "is_blurry": bool,
                "brightness": float,
                "brightness_ok": bool,
                "contrast": float,
                "contrast_ok": bool,
                "flags": list  # List of issues found
            }
        """
        issues = []
        
        # Ensure grayscale for analysis
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 1. Check blur
        blur_score = self.detect_blur(gray)
        is_blurry = blur_score < self.blur_threshold
        if is_blurry:
            issues.append(f"BLURRY (score: {blur_score:.2f} < {self.blur_threshold})")
        
        # 2. Check brightness
        brightness = self.analyze_brightness(gray)
        brightness_ok = self.min_brightness <= brightness <= self.max_brightness
        if not brightness_ok:
            if brightness < self.min_brightness:
                issues.append(f"TOO_DARK (brightness: {brightness:.1f} < {self.min_brightness})")
            else:
                issues.append(f"TOO_BRIGHT (brightness: {brightness:.1f} > {self.max_brightness})")
        
        # 3. Check contrast
        contrast = self.analyze_contrast(gray)
        contrast_ok = contrast >= self.min_contrast
        if not contrast_ok:
            issues.append(f"LOW_CONTRAST (contrast: {contrast:.2f} < {self.min_contrast})")
        
        is_quality = len(issues) == 0
        
        quality_report = {
            "is_quality": is_quality,
            "blur_score": blur_score,
            "is_blurry": is_blurry,
            "brightness": brightness,
            "brightness_ok": brightness_ok,
            "contrast": contrast,
            "contrast_ok": contrast_ok,
            "flags": issues,
            "image_path": str(image_path) if image_path else None
        }
        
        return quality_report
    
    @staticmethod
    def detect_blur(gray_image):
        """
        Detect blur using Laplacian variance method.
        
        WHY: Blurry images don't provide clear disease pattern information.
        A blurry image of a diseased leaf looks the same as a blurry healthy leaf.
        Laplacian operator highlights edges; blur reduces variation.
        
        HOW: Laplacian computes second derivative of pixel intensity.
        - Sharp images: high variation in second derivative
        - Blurry images: low variation (smooth gradient)
        - Variance measures this variation
        
        Args:
            gray_image (np.ndarray): Grayscale image
            
        Returns:
            float: Laplacian variance (higher = sharper)
            
        TUNING TIPS:
        - Typical values: 50-500 depending on content
        - Sample images: compute score on sample leaves to find threshold
        - Too high threshold: removes too many images
        - Too low threshold: includes blurry images
        """
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        variance = laplacian.var()
        return variance
    
    @staticmethod
    def analyze_brightness(gray_image):
        """
        Analyze average brightness of image.
        
        WHY: Avoids images taken in poor lighting:
        - Dark images: disease patterns invisible
        - Overexposed images: fine details lost
        - Agricultural images should have natural good lighting
        
        Args:
            gray_image (np.ndarray): Grayscale image
            
        Returns:
            float: Average pixel value (0-255)
            
        INTERPRETATION:
        - 0-50: Very dark (underexposed)
        - 50-100: Dark but visible
        - 100-180: Good lighting (typical healthy crop)
        - 180-240: Bright (possibly overexposed)
        - 240-255: Blown out (definitely overexposed)
        """
        return float(cv2.mean(gray_image)[0])
    
    @staticmethod
    def analyze_contrast(gray_image):
        """
        Analyze contrast (standard deviation of pixels).
        
        WHY: Low contrast images are flat and uninformative.
        Disease symptoms need visible contrast to be recognizable.
        
        Args:
            gray_image (np.ndarray): Grayscale image
            
        Returns:
            float: Standard deviation of pixel values
            
        INTERPRETATION:
        - 0-10: Very low contrast (mostly uniform color)
        - 10-30: Low contrast (flat image)
        - 30-100: Good contrast (typical natural image)
        - 100+: Very high contrast (possibly artificial)
        """
        return float(gray_image.std())
    
    def is_image_corrupted(self, image):
        """
        Check if image data appears corrupted.
        
        WHY: Corrupted images can't be processed or contain invalid data.
        
        Args:
            image (np.ndarray): Image to check
            
        Returns:
            bool: True if image appears corrupted
        """
        if image is None or image.size == 0:
            return True
        
        # Check for NaN values
        if np.isnan(image).any():
            return True
        
        # Check for all zeros or all same value
        if not (image.max() > image.min()):
            return True
        
        # Check image shape validity
        if len(image.shape) < 2:
            return True
        
        return False
    
    def generate_quality_report(self, quality_results):
        """
        Generate summary report from quality check results.
        
        Args:
            quality_results (list): List of quality reports from check_image_quality
            
        Returns:
            dict: Summary statistics
        """
        if not quality_results:
            return {"total_images": 0}
        
        total = len(quality_results)
        quality_count = sum(1 for r in quality_results if r["is_quality"])
        blurry_count = sum(1 for r in quality_results if r["is_blurry"])
        brightness_issues = sum(1 for r in quality_results if not r["brightness_ok"])
        contrast_issues = sum(1 for r in quality_results if not r["contrast_ok"])
        
        report = {
            "total_images": total,
            "quality_images": quality_count,
            "quality_percentage": (quality_count / total * 100) if total > 0 else 0,
            "blurry_images": blurry_count,
            "brightness_issues": brightness_issues,
            "contrast_issues": contrast_issues,
            "rejection_rate": ((total - quality_count) / total * 100) if total > 0 else 0
        }
        
        return report


class ImageQualityValidator:
    """Higher-level image validation combining multiple checks."""
    
    def __init__(self, quality_checker):
        """
        Initialize validator.
        
        Args:
            quality_checker (QualityChecker): QualityChecker instance
        """
        self.quality_checker = quality_checker
    
    def validate_image_file(self, image_path):
        """
        Validate complete image file (loadability + quality).
        
        Args:
            image_path (str or Path): Path to image file
            
        Returns:
            tuple: (is_valid, image, quality_report)
        """
        try:
            image_path = Path(image_path)
            
            # Try to load image
            image = cv2.imread(str(image_path))
            
            if image is None:
                logger.warning(f"Failed to load image: {image_path}")
                return False, None, {"error": "Could not load image"}
            
            # Check if corrupted
            if self.quality_checker.is_image_corrupted(image):
                logger.warning(f"Image corrupted: {image_path}")
                return False, None, {"error": "Image data corrupted"}
            
            # Run quality checks
            quality_report = self.quality_checker.check_image_quality(image, image_path)
            
            is_valid = quality_report["is_quality"]
            
            return is_valid, image, quality_report
            
        except Exception as e:
            logger.error(f"Error validating {image_path}: {e}")
            return False, None, {"error": str(e)}
