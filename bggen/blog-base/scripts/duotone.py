import cv2
import numpy as np
from PIL import Image, ImageDraw

# Kanagawa theme colors (in BGR format since that's what OpenCV uses)
KANAGAWA_LIGHT_BG = (227, 237, 239)    # efede3 in RGB -> convert to BGR
KANAGAWA_LIGHT_TEXT = (40, 31, 31)     # 1f1f28 in RGB -> convert to BGR
KANAGAWA_DARK_BG = (40, 31, 31)        # 1f1f28 in RGB -> convert to BGR
KANAGAWA_DARK_TEXT = (186, 215, 220)   # dcd7ba in RGB -> convert to BGR

def create_halftone(image, dot_radius=4, spacing=8, threshold=0.3, angle=45):
    # Convert to grayscale and get dimensions
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    height, width = gray.shape
    
    # Calculate padding needed to prevent corner loss during rotation
    diagonal = int(np.sqrt(height**2 + width**2))
    pad_x = (diagonal - width) // 2
    pad_y = (diagonal - height) // 2
    
    # Create padded images
    padded_size = (diagonal, diagonal)
    halftone = np.zeros(padded_size, np.uint8)
    padded_gray = np.zeros(padded_size, np.uint8)
    
    # Copy original image to center of padding
    padded_gray[pad_y:pad_y+height, pad_x:pad_x+width] = gray
    
    # Calculate rotation matrix around center
    center = (diagonal // 2, diagonal // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Rotate grayscale image
    gray_rotated = cv2.warpAffine(padded_gray, M, padded_size)
    
    # Create dots in staggered pattern
    row_spacing = int(spacing * 0.866)  # Height of equilateral triangle
    
    for y in range(0, diagonal, row_spacing):
        offset = spacing // 2 if (y // row_spacing) % 2 else 0
        for x in range(offset, diagonal, spacing):
            intensity = gray_rotated[y, x] / 255.0
            
            # Apply non-linear scaling for lighter areas
            if intensity > (1 - threshold):
                scaled_intensity = ((intensity - (1 - threshold)) / threshold) ** 2
            else:
                scaled_intensity = intensity
            
            # Calculate dot radius
            r = int(scaled_intensity * dot_radius)
            if r > 0:
                cv2.circle(halftone, 
                          (x, y), 
                          r, 
                          255,
                          -1)
    
    # Rotate back
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    halftone = cv2.warpAffine(halftone, M, padded_size)
    
    # Crop to original size
    halftone = halftone[pad_y:pad_y+height, pad_x:pad_x+width]
    
    return halftone

def apply_duotone(halftone, color1, color2):
    """Map black and white to two colors"""
    # Normalize to 0-1
    normalized = halftone.astype(float) / 255
    
    # Create RGB image
    height, width = halftone.shape
    duotone = np.zeros((height, width, 3), np.uint8)
    
    # Interpolate between colors
    for i in range(3):
        duotone[:,:,i] = normalized * color1[i] + (1-normalized) * color2[i]
    
    return duotone

def process_image(input_path, output_path, dot_radius=4, spacing=8, dark_mode=False, threshold=0.3, angle=30):
    # Read image
    image = cv2.imread(input_path)
    
    # Create halftone
    halftone = create_halftone(image, dot_radius, spacing, threshold, angle)
    
    # Use dark or light theme colors
    if dark_mode:
        color1 = KANAGAWA_DARK_TEXT  # Foreground color
        color2 = KANAGAWA_DARK_BG    # Background color
    else:
        color1 = KANAGAWA_LIGHT_BG  # Foreground color
        color2 = KANAGAWA_LIGHT_TEXT    # Background color
    
    # Apply duotone
    result = apply_duotone(halftone, color1, color2)
    
    # Save result
    cv2.imwrite(output_path, result)

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Create duotone halftone images')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', help='Output image path')
    parser.add_argument('--dark', action='store_true', help='Use dark theme colors')
    parser.add_argument('--dot-radius', type=int, default=4, help='Radius of halftone dots')
    parser.add_argument('--spacing', type=int, default=8, help='Spacing between dots')
    parser.add_argument('--threshold', type=float, default=0.3, help='Darkness threshold (0-1)')
    parser.add_argument('--angle', type=float, default=30, help='Rotation angle in degrees')
    
    args = parser.parse_args()
    
    process_image(args.input, args.output, 
                 dot_radius=args.dot_radius, 
                 spacing=args.spacing,
                 dark_mode=args.dark,
                 threshold=args.threshold,
                 angle=args.angle) 