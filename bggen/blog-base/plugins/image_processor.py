import os
import hashlib
import requests
import re
from pathlib import Path
import cv2
import numpy as np
from pelican import signals
from urllib.parse import urlparse

import cv2
import numpy as np
import sys

DRY_RUN = False  # Skip modifying markdown files

# Add user agent info
USER_AGENT = "MichaelSaxonBlog/1.0 (https://saxon.me; saxon@ucsb.edu) PythonRequests/2.31.0"

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

def twotone_convert(img_path, output_path):
    # Read image
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not read image {img_path}")
        return

    # Define color palette (in BGR format)
    palette = np.array([
        [31, 31, 40],    # Dark bg (#1f1f28)
        [186, 215, 220], # Light bg (#efede3)
        [137, 149, 126], # Theme color (medium cyan #6a9589)
        [216, 156, 126], # Link blue (#7e9cd8)
        [67, 64, 192],   # Kanagawa red (#c04043)
        [132, 195, 228], # Kanagawa yellow (#e4c384)
        [197, 92, 74],   # Kanagawa dark blue (#4a5cc5)
    ], dtype=np.float32)

    # Apply dithering
    output = floyd_steinberg_dither(img, palette)

    # Save the result
    cv2.imwrite(output_path, output)
    print(f"Saved dithered image to {output_path}")

CACHE_DIR = "content/images"
MAX_IMAGE_WIDTH = 1200

def get_cache_path(url, filepath):
    # Get the slug from the markdown filename
    slug = os.path.splitext(os.path.basename(filepath))[0]
    
    # Get extension from URL
    ext = os.path.splitext(urlparse(url).path)[1]
    if not ext:
        ext = '.jpg'  # Default to jpg if no extension
    
    return os.path.join(CACHE_DIR, f"{slug}-teaser{ext}")

def process_external_image(url, filepath):
    if not url or not url.startswith(('http://', 'https://')):
        return url
        
    cache_path = get_cache_path(url, filepath)
    
    # Return cached path if exists
    if os.path.exists(cache_path):
        return cache_path
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        img_array = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Downsample if needed
        height, width = img.shape[:2]
        if width > MAX_IMAGE_WIDTH:
            scale = MAX_IMAGE_WIDTH / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
        
        extension = os.path.splitext(url)[1]
        temp_path = cache_path + ".temp" + extension
        cv2.imwrite(temp_path, img)
        
        twotone_convert(temp_path, cache_path)
        os.remove(temp_path)
        
        return cache_path
    
    except Exception as e:
        print(f"Error processing image {url}: {e}")
        return url

def preprocess_images(pelican):
    """Process images in markdown files before Pelican processes them"""
    for dirpath, _, filenames in os.walk(pelican.settings['PATH']):
        for filename in filenames:
            if filename.endswith('.md'):
                filepath = os.path.join(dirpath, filename)
                process_markdown_file(filepath)

def process_markdown_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Find Image metadata
    img_pattern = r'^Image:\s*(.+)$'
    
    lines = content.split('\n')
    new_lines = []
    modified = False
    
    for line in lines:
        match = re.match(img_pattern, line, re.MULTILINE)
        if match:
            url = match.group(1).strip()
            if url.startswith(('http://', 'https://')):
                cached_path = process_external_image(url, filepath)
                # Make path relative without leading slash
                rel_path = cached_path  # Just use the relative path as-is
                new_lines.append(f'Image: {rel_path}')
                modified = True
                if DRY_RUN:
                    print(f"[DRY RUN] Would update {url} -> {rel_path}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    if modified and not DRY_RUN:
        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))

def register():
    """Register the plugin with Pelican"""
    signals.initialized.connect(preprocess_images) 