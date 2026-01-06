import os
from pathlib import Path

def update_references_and_cleanup(root_dir):
    extensions_to_replace = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    text_files_extensions = ['.html', '.css', '.js', '.json', '.xml', '.txt', '.md']
    
    # 1. Collect all WebP files that exist now
    webp_files = set()
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.webp'):
                # Store relative path or just filename? 
                # References might be relative. 
                # Safer: Store absolute path to check existence, but for text replacement we look for strings.
                full_path = Path(root) / file
                webp_files.add(str(full_path))

    print(f"Found {len(webp_files)} WebP files. Proceeding with text replacement...")

    # 2. Walk through text files and replace references
    replaced_count = 0
    files_modified = 0
    
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
                    for ext in extensions_to_replace:
                        # Simple string replacement
                        # Limitation: might replace substrings incorrectly if filenames overlap
                        # e.g. 'image.png' -> 'image.webp'
                        # but 'image.png.bak' -> 'image.webp.bak' (acceptable)
                        new_content = new_content.replace(ext, '.webp')
                        
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_modified += 1
                        print(f"Updated references in: {file}")
                        
                except Exception as e:
                    print(f"Error processing {file}: {e}")

    print(f"Updated {files_modified} files.")

    # 3. Cleanup old images
    # Only delete if a corresponding .webp exists
    deleted_count = 0
    saved_space = 0
    
    print("Cleaning up old image files...")
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in extensions_to_replace:
                # Check if webp equivalent exists
                webp_candidate = file_path.with_suffix('.webp')
                if webp_candidate.exists():
                    try:
                        size = file_path.stat().st_size
                        os.remove(file_path)
                        deleted_count += 1
                        saved_space += size
                        print(f"Deleted: {file}")
                    except Exception as e:
                        print(f"Error deleting {file}: {e}")
                else:
                    print(f"Skipped (no WebP found): {file}")

    print("-" * 30)
    print(f"Cleanup Complete.")
    print(f"Files Modified: {files_modified}")
    print(f"Images Deleted: {deleted_count}")
    print(f"Space Reclaimed: {saved_space / (1024*1024):.2f} MB")

if __name__ == "__main__":
    update_references_and_cleanup("e:/appdev/vexil-logic-games")
