import os
import re
from pathlib import Path

def apply_lazy_loading(root_dir):
    files_modified = 0
    images_patched = 0
    
    # Regex to find img tags.
    # We want to match <img ... > and ensure it doesn't have loading="..."
    # This regex is a bit simplistic but works for standard HTML.
    # It looks for <img [attributes] >
    
    # Strategy: Find all <img ...> strings.
    # For each match, check if 'loading=' is present.
    # If not, insert 'loading="lazy"' before the closing > or />
    
    img_pattern = re.compile(r'<img\s+([^>]+)>', re.IGNORECASE)
    
    print(f"Scanning for HTML files in {root_dir}")
    
    for root, dirs, files in os.walk(root_dir):
        if 'node_modules' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.html'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    file_changed = False
                    
                    def replacement(match):
                        attrs = match.group(1)
                        # Check if loading attribute exists
                        if 'loading=' not in attrs.lower():
                            # Check if it's a critical image (e.g., hero/banner)
                            # Heuristic: if class contains 'hero', 'banner', 'logo' maybe skip?
                            # User asked for "all pages and images", but lazy loading LCP images (hero) hurts performance.
                            # Let's skip if class has 'hero-bg' or it's the logo.
                            
                            # However, to be safe and broadly compliant with "all", I'll apply to most.
                            # But I'll preserve LCP if I see explicit "priority" or "eager" (unlikely here).
                            
                            nonlocal images_patched
                            images_patched += 1
                            return f'<img {attrs} loading="lazy">'
                        
                        return match.group(0) # No change
                    
                    new_content = img_pattern.sub(replacement, content)
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_modified += 1
                        # print(f"Updated: {file}")
                        
                except Exception as e:
                    print(f"Error updating {file}: {e}")

    print("-" * 30)
    print(f"Update Complete.")
    print(f"Files Modified: {files_modified}")
    print(f"Images Patched: {images_patched}")

if __name__ == "__main__":
    apply_lazy_loading("e:/appdev/vexil-logic-games")
