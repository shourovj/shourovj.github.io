import cv2
import numpy as np
import sys

def get_closest_color(pixel, palette):
    # Find closest color in palette using Euclidean distance
    distances = np.sqrt(np.sum((palette - pixel) ** 2, axis=1))
    return palette[np.argmin(distances)]

def floyd_steinberg_dither(img, palette):
    height, width = img.shape[:2]
    img = img.astype(np.float32)
    
    for y in range(height-1):
        for x in range(width-1):
            old_pixel = img[y, x].copy()
            new_pixel = get_closest_color(old_pixel, palette)
            img[y, x] = new_pixel
            
            error = old_pixel - new_pixel
            
            # Distribute error to neighboring pixels
            img[y, x+1] = img[y, x+1] + error * 7/16
            img[y+1, x-1] = img[y+1, x-1] + error * 3/16 if x > 0 else img[y+1, x-1]
            img[y+1, x] = img[y+1, x] + error * 5/16
            img[y+1, x+1] = img[y+1, x+1] + error * 1/16
    
    return img.clip(0, 255).astype(np.uint8)

def generate_extended_palette(palette, enable_blends=False):
    if not enable_blends:
        return palette
        
    # Start with original palette
    extended_palette = palette.copy()
    
    # Add 50% blends between each pair of colors
    num_colors = len(palette)
    for i in range(num_colors):
        for j in range(i+1, num_colors):
            # Create 50% blend
            blend = (palette[i] + palette[j]) / 2
            extended_palette = np.vstack([extended_palette, blend])
    
    return extended_palette

def twotone_convert(img_path, output_path, upscale_factor=3, enable_blends=False):
    # Read image
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not read image {img_path}")
        return

    # Get original dimensions
    orig_height, orig_width = img.shape[:2]

    # Upscale image if factor > 1
    if upscale_factor > 1:
        img = cv2.resize(img, (orig_width * upscale_factor, orig_height * upscale_factor), 
                        interpolation=cv2.INTER_CUBIC)

    # Define color palette (in BGR format)
    palette = np.array([
        [31, 31, 40],    # Dark bg (#1f1f28)
        [186, 215, 220], # Light bg (#efede3)
        [137, 149, 126], # Theme color (medium cyan #6a9589)
        #[216, 156, 126], # Link blue (#7e9cd8)
        [67, 64, 192],   # Kanagawa red (#c04043)
        [132, 195, 228], # Kanagawa yellow (#e4c384)
        [197, 92, 74],   # Kanagawa dark blue (#4a5cc5)
        [147, 131, 226], # Kanagawa magenta (#e282b5)
        [108, 236, 248], # Kanagawa bright yellow (#f8ec7c)
        [43, 43, 237],   # Kanagawa bright red (#ed2b2b)
        [75, 107, 75],   # Kanagawa dark green (#4b6b4b)
    ], dtype=np.float32)
    
    # Generate extended palette with blends if requested
    extended_palette = generate_extended_palette(palette, enable_blends)
    if enable_blends:
        print(f"Extended palette from {len(palette)} to {len(extended_palette)} colors with blends")
        
    # Apply dithering
    output = floyd_steinberg_dither(img, extended_palette)

    # Downscale back to original size if we upscaled
    if upscale_factor > 1:
        output = cv2.resize(output, (orig_width, orig_height), 
                          interpolation=cv2.INTER_AREA)

    # Save the result
    cv2.imwrite(output_path, output)
    print(f"Saved dithered image to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python twotone.py input_image output_image [upscale_factor] [enable_blends]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    upscale_factor = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    enable_blends = (sys.argv[4].lower() == 'true') if len(sys.argv) > 4 else False

    twotone_convert(input_path, output_path, upscale_factor, enable_blends)
