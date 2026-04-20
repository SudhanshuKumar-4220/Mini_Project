"""
Image Utility Functions - Image processing, format conversion, EXIF handling.

This module handles:
- Format conversions (HEIC, JPG, PNG)
- EXIF orientation correction
- Image resizing and standardization
- Color space management
"""

import cv2
import numpy as np
from PIL import Image, ImageOps
from pathlib import Path
import logging

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image processing operations."""
    
    def __init__(self, target_size=(256, 256), target_format="RGB", jpeg_quality=90):
        """
        Initialize ImageProcessor.
        
        Args:
            target_size (tuple): Target image dimensions (height, width)
            target_format (str): Target color space ("RGB" or "BGR")
            jpeg_quality (int): JPEG quality (1-100)
        """
        self.target_size = target_size
        self.target_format = target_format
        self.jpeg_quality = jpeg_quality
    
    def load_image(self, image_path, return_pil=False):
        """
        Load image from file, handling various formats.
        
        WHY: Images come in different formats (HEIC, JPEG, PNG).
        This function provides unified loading interface.
        
        Args:
            image_path (str or Path): Path to image file
            return_pil (bool): If True, return PIL Image; if False, return OpenCV format
            
        Returns:
            np.ndarray or PIL.Image: Loaded image
            
        Raises:
            Exception: If image cannot be loaded
        """
        image_path = Path(image_path)
        
        try:
            # Try PIL first (better for HEIC support)
            pil_img = Image.open(image_path)
            
            if return_pil:
                return pil_img
            
            # Convert PIL to OpenCV format (BGR)
            pil_img = pil_img.convert("RGB")
            cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            return cv_img
            
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            raise
    
    def correct_exif_orientation(self, image_path):
        """
        Correct image orientation based on EXIF metadata.
        
        WHY: Mobile phones store orientation in EXIF instead of rotating pixels.
        Images from iPhone/Android often have incorrect orientation in memory.
        This ensures images display correctly.
        
        Args:
            image_path (str or Path): Path to image file
            
        Returns:
            PIL.Image: Image with corrected orientation
        """
        try:
            img = Image.open(image_path)
            # ImageOps.exif_transpose automatically corrects orientation
            img = ImageOps.exif_transpose(img)
            return img if img is not None else Image.open(image_path)
        except Exception as e:
            logger.warning(f"Could not correct EXIF orientation for {image_path}: {e}")
            return Image.open(image_path)
    
    def resize_image(self, image, target_size=None, preserve_aspect=True):
        """
        Resize image to target size.
        
        WHY: CNN models require fixed input dimensions.
        This ensures all images have consistent size for batching.
        
        Args:
            image (np.ndarray or PIL.Image): Input image
            target_size (tuple): Target size (height, width)
            preserve_aspect (bool): If True, add padding to preserve aspect ratio
            
        Returns:
            np.ndarray: Resized image
        """
        target_size = target_size or self.target_size
        
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        if preserve_aspect:
            return self._resize_with_padding(image, target_size)
        else:
            return cv2.resize(image, (target_size[1], target_size[0]))
    
    def _resize_with_padding(self, image, target_size):
        """
        Resize image while preserving aspect ratio using padding.
        
        WHY: Stretching distorts image and can affect disease pattern recognition.
        Padding preserves original proportions while fitting target size.
        
        Args:
            image (np.ndarray): Input image
            target_size (tuple): Target size (height, width)
            
        Returns:
            np.ndarray: Resized image with padding
        """
        h, w = image.shape[:2]
        target_h, target_w = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        
        # Calculate new dimensions
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize
        resized = cv2.resize(image, (new_w, new_h))
        
        # Create canvas with target size (white padding)
        if len(image.shape) == 3:
            canvas = np.full((target_h, target_w, image.shape[2]), 255, dtype=np.uint8)
        else:
            canvas = np.full((target_h, target_w), 255, dtype=np.uint8)
        
        # Place resized image in center
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
        
        return canvas
    
    def convert_to_rgb(self, image):
        """
        Convert image to RGB color space.
        
        WHY: Different formats use different color spaces:
        - JPEG: Often BGR or YCbCr in memory
        - PNG: Can be grayscale, RGBA, or RGB
        - HEIC: Implementation-dependent
        CNN models expect consistent RGB input.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: RGB image
        """
        if len(image.shape) == 2:
            # Grayscale - convert to RGB
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            # RGBA - convert to RGB
            return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        elif image.shape[2] == 3:
            # BGR (OpenCV default) - convert to RGB
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            logger.warning(f"Unexpected image shape: {image.shape}")
            return image
    
    def normalize_image(self, image):
        """
        Normalize image pixel values to 0-1 range.
        
        WHY: Neural networks train better with normalized inputs.
        Most CNN models are trained on normalized ImageNet images.
        
        Args:
            image (np.ndarray): Input image (uint8, 0-255)
            
        Returns:
            np.ndarray: Normalized image (float, 0-1)
        """
        if image.dtype == np.uint8:
            return image.astype(np.float32) / 255.0
        return image.astype(np.float32)
    
    def standardize_image(self, image_path, correct_orientation=True, normalize=False):
        """
        Complete image standardization pipeline.
        
        WHY: This is the main preprocessing function that combines all steps
        to ensure consistent image format for the model.
        
        Args:
            image_path (str or Path): Path to image
            correct_orientation (bool): Apply EXIF orientation correction
            normalize (bool): Normalize to 0-1 range
            
        Returns:
            np.ndarray: Standardized image
            bool: Success status
        """
        try:
            # Load and correct orientation
            if correct_orientation:
                pil_img = self.correct_exif_orientation(image_path)
            else:
                pil_img = Image.open(image_path)
            
            # Convert to RGB
            pil_img = pil_img.convert("RGB")
            image = np.array(pil_img)
            
            # Ensure RGB format
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize
            image = self.resize_image(image)
            
            # Normalize if requested
            if normalize:
                image = self.normalize_image(image)
            
            return image, True
            
        except Exception as e:
            logger.error(f"Standardization failed for {image_path}: {e}")
            return None, False
    
    def save_image(self, image, output_path, format="JPEG", quality=None):
        """
        Save image to file in target format.
        
        WHY: Ensures all images are saved in uniform format for consistency.
        
        Args:
            image (np.ndarray): Image to save
            output_path (str or Path): Output file path
            format (str): Output format ("JPEG" or "PNG")
            quality (int): JPEG quality (1-100)
            
        Returns:
            bool: Success status
        """
        quality = quality or self.jpeg_quality
        
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert BGR to RGB for saving
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            pil_img = Image.fromarray(image)
            
            if format.upper() == "JPEG":
                pil_img.save(output_path, "JPEG", quality=quality, optimize=True)
            elif format.upper() == "PNG":
                pil_img.save(output_path, "PNG", optimize=True)
            else:
                logger.warning(f"Unknown format {format}, defaulting to JPEG")
                pil_img.save(output_path, "JPEG", quality=quality)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save image {output_path}: {e}")
            return False
    
    @staticmethod
    def get_image_dimensions(image_path):
        """
        Get image dimensions without full loading.
        
        Args:
            image_path (str or Path): Path to image
            
        Returns:
            tuple: (height, width) or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Note: PIL returns (width, height), we return (height, width)
                return (img.height, img.width)
        except Exception as e:
            logger.error(f"Could not get dimensions for {image_path}: {e}")
            return None
    
    @staticmethod
    def is_valid_image_format(file_path):
        """
        Check if file is valid image format.
        
        Args:
            file_path (str or Path): Path to file
            
        Returns:
            bool: True if valid image format
        """
        valid_extensions = {".jpg", ".jpeg", ".png", ".heic"}
        file_ext = Path(file_path).suffix.lower()
        return file_ext in valid_extensions
