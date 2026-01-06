import os
from PIL import Image
from pathlib import Path

def convert_to_webp(directory):
    total_savings = 0
    params = [
        ('assets/img', 80), # default quality
    ]
    
    extensions = {'.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG'}
    
    print(f"Scanning directory: {directory}")
    
    count = 0
    errors = 0
    skips = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions:
                # Target path
                webp_path = file_path.with_suffix('.webp')
                
                # Skip if webp already exists and is newer? 
                # For now, just overwrite or create.
                
                try:
                    # Open image
                    with Image.open(file_path) as img:
                        # Convert to RGB if necessary (for PNGs with alpha that might be saved as JPG, 
                        # but WebP handles RGBA fine).
                        # However, converting PNG to WebP keeps transparency.
                        
                        # Get original size
                        original_size = file_path.stat().st_size
                        
                        # Save as WebP
                        img.save(webp_path, 'WEBP', quality=80)
                        
                        # Get new size
                        new_size = webp_path.stat().st_size
                        
                        savings = original_size - new_size
                        total_savings += savings
                        
                        print(f"Converted: {file} | {original_size/1024:.1f}KB -> {new_size/1024:.1f}KB | Saved: {savings/1024:.1f}KB")
                        count += 1
                        
                except Exception as e:
                    print(f"Error converting {file}: {e}")
                    errors += 1

    print("-" * 30)
    print(f"Conversion Complete.")
    print(f"Total Images: {count}")
    print(f"Total Space Saved: {total_savings / (1024*1024):.2f} MB")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    convert_to_webp("e:/appdev/vexil-logic-games/assets/img")
