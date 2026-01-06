import os
import re
from pathlib import Path

def fix_broken_links(root_dir):
    text_files_extensions = ['.html', '.css', '.js', '.json', '.xml' ]
    # Naive assumption: We replaced .png, .jpg, .jpeg with .webp
    # We want to find .webp references that are INVALID.
    
    # invalid categories:
    # 1. External links (http/https) -> Revert to .png/.jpg (we have to guess, but we can check likelyhood)
    #    Actually, most external links in this project might be icons or CDNs. 
    #    Risk: We don't know if original was png or jpg.
    #    Mitigation: Check if the URL works? Too slow.
    #    Better: Just look at common patterns. 
    
    # 2. Local files that don't exist as .webp
    
    files_fixed = 0
    total_reversions = 0
    
    print(f"Scanning for broken WebP links in {root_dir}")
    
    for root, dirs, files in os.walk(root_dir):
        if 'node_modules' in root or '.git' in root:
            continue
            
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in text_files_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    
                    # Regex to find .webp strings
                    # We look for strings ending in .webp
                    # This is tricky because we need the context (path).
                    # Let's find common file path patterns: 
                    # src="...", url('...'), href="..."
                    
                    # Simple approach: Find all string tokens ending in .webp
                    # This might be fragile, but let's try a regex for typical paths
                    # matches:  assets/img/foo.webp,  favicon.webp,  https://.../foo.webp
                    
                    matches = list(set(re.findall(r'[\"\']([^\"\']+\.webp)[\"\']', content)))
                    
                    file_changed = False
                    
                    for match in matches:
                        # Match is the full path string inside quotes, e.g. "assets/img/logo.webp"
                        
                        # Case 1: External Link
                        if match.startswith('http'):
                            print(f"[EXT] Found external WebP link: {match} in {file}")
                            # Heuristic: Revert to png (most common for web graphics)
                            # Or check if we can guess. 
                            # If it was google fonts or similar, unlikely to end in image ext.
                            # If it's a CDN image...
                            # Let's try reverting to .png as safe default if we broke it.
                            reverted = match.replace('.webp', '.png')
                            new_content = new_content.replace(match, reverted)
                            file_changed = True
                            total_reversions += 1
                        
                        # Case 2: Local File
                        else:
                            # Resolve path relative to current file (if relative) or root (if absolute-like)
                            # Web paths are tricky. 
                            # If starts with /, it's root relative.
                            # If relative, it depeneds on file location.
                            
                            # Let's check if the file exists on disk at the presumed location.
                            # We assume the project root is e:\appdev\vexil-logic-games
                            project_root = Path(root_dir)
                            
                            # Construct candidate path
                            candidate_path = None
                            
                            if match.startswith('/'):
                                # Absolute from root
                                candidate_path = project_root / match.lstrip('/')
                            else:
                                # Relative to current file
                                candidate_path = Path(root) / match
                            
                            # Also handle "assets/..." from css file which might be in assets/css/
                            # If CSS is in assets/css/style.css and refers to "../img/foo.webp"
                            
                            # Simplified check:
                            # 1. Does absolute path exist?
                            # 2. Does root-relative path exist?
                            
                            exists = False
                            if candidate_path and candidate_path.exists():
                                exists = True
                            
                            # Check clean paths (remove anchors/queries if any - regex didn't imply them but good practice)
                            
                            if not exists:
                                # Try to find if .png or .jpg version exists
                                # This confirms we broke a link to a non-existent webp where original still exists
                                
                                # Check for .png
                                png_candidate_path = candidate_path.with_suffix('.png')
                                jpg_candidate_path = candidate_path.with_suffix('.jpg')
                                jpeg_candidate_path = candidate_path.with_suffix('.jpeg')
                                
                                original_ext = None
                                if png_candidate_path.exists(): origin_ext = '.png'
                                elif jpg_candidate_path.exists(): origin_ext = '.jpg'
                                elif jpeg_candidate_path.exists(): origin_ext = '.jpeg'
                                else: origin_ext = None
                                
                                if origin_ext:
                                    print(f"[MISSING] WebP not found: {match}. Reverting to {origin_ext}")
                                    reverted = match.replace('.webp', origin_ext)
                                    new_content = new_content.replace(match, reverted)
                                    file_changed = True
                                    total_reversions += 1
                                else:
                                    # Neither WebP nor Original exists. Only revert if we are sure it was broken by us.
                                    # E.g. favicon.
                                    if 'favicon' in match:
                                        print(f"[ICON] Reverting favicon to .png blindly")
                                        reverted = match.replace('.webp', '.png')
                                        new_content = new_content.replace(match, reverted)
                                        file_changed = True
                                        total_reversions += 1

                    if file_changed:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_fixed += 1
                        
                except Exception as e:
                    print(f"Error checking {file}: {e}")

    print("-" * 30)
    print(f"Fix Complete.")
    print(f"Files Modified: {files_fixed}")
    print(f"Links Reverted: {total_reversions}")

if __name__ == "__main__":
    fix_broken_links("e:/appdev/vexil-logic-games")
