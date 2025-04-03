import os
import re
import hashlib
import requests
from pathlib import Path
from urllib.parse import urlparse
import cv2
import numpy as np
from twotone import twotone_convert

CACHE_DIR = "blog-base/content/images/cache"
MAX_IMAGE_WIDTH = 1200  # Maximum width to downsample to

def get_cache_path(url):
    # Create hash of URL for filename
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.jpg")

def downsample_image(img):
    height, width = img.shape[:2]
    if width > MAX_IMAGE_WIDTH:
        scale = MAX_IMAGE_WIDTH / width
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(img, (new_width, new_height))
    return img

def process_external_image(url):
    cache_path = get_cache_path(url)
    
    # Return cached path if exists
    if os.path.exists(cache_path):
        return cache_path
    
    # Download and process image
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert to OpenCV format
        img_array = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Downsample if needed
        img = downsample_image(img)
        
        # Create temp file for twotone processing
        temp_path = cache_path + ".temp"
        cv2.imwrite(temp_path, img)
        
        # Apply dithering
        twotone_convert(temp_path, cache_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return cache_path
    
    except Exception as e:
        print(f"Error processing image {url}: {e}")
        return url

def process_markdown_file(md_path):
    # Create cache directory if it doesn't exist
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    with open(md_path, 'r') as f:
        content = f.read()
    
    # Find Image metadata tag
    img_pattern = r'^Image:\s*(.+)$'
    
    def replace_image(match):
        url = match.group(1).strip()
        
        # Skip if not external URL
        if not url.startswith(('http://', 'https://')):
            return match.group(0)
        
        # Process image and get cached path
        cached_path = process_external_image(url)
        
        # Convert to relative path
        rel_path = os.path.relpath(cached_path, os.path.dirname(md_path))
        
        return f'Image: {rel_path}'
    
    # Replace Image metadata
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        match = re.match(img_pattern, line)
        if match:
            new_lines.append(replace_image(match))
        else:
            new_lines.append(line)
    
    # Write updated content
    with open(md_path, 'w') as f:
        f.write('\n'.join(new_lines))

def main():
    content_dir = "bggen/blog-base/content"
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                print(f"Processing {md_path}")
                process_markdown_file(md_path)

if __name__ == "__main__":
    main() 