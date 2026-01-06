import os
from pathlib import Path

def update_html_links(root_dir):
    replacements = {
        'assets/css/style.css': 'assets/css/style.min.css',
        'assets/js/main.js': 'assets/js/main.min.js',
        'assets/js/app-loader.js': 'assets/js/app-loader.min.js'
    }
    
    files_modified = 0
    
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
                    modified = False
                    
                    for original, minified in replacements.items():
                        if original in new_content:
                            new_content = new_content.replace(original, minified)
                            modified = True
                            
                    if modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_modified += 1
                        print(f"Updated: {file}")
                        
                except Exception as e:
                    print(f"Error updating {file}: {e}")

    print("-" * 30)
    print(f"Update Complete.")
    print(f"Files Modified: {files_modified}")

if __name__ == "__main__":
    update_html_links("e:/appdev/vexil-logic-games")
