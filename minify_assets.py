import re
import os

def minify_css(content):
    # Remove comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    # Remove whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([\{\};:,])\s*', r'\1', content)
    content = content.replace(';}', '}')
    return content.strip()

def minify_js(content):
    # Very basic JS minification (safe removal of comments and whitespace)
    # Removing single line comments (risky if inside strings, but for main.js usually safe if code is standard)
    # We will use a simple approach: remove block comments, remove leading/trailing whitespace per line.
    
    # Remove block comments
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    
    lines = content.split('\n')
    minified_lines = []
    for line in lines:
        # constant removal of // comments is risky without a proper parser
        # so we will just strip whitespace and join
        line = line.strip()
        if line and not line.startswith('//'):
             minified_lines.append(line)
             
    # This is a weak minification for JS but better than nothing without external deps.
    # ideally we'd use a library. 
    return '\n'.join(minified_lines)

def process_file(file_path, minifier_func, ext):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        minified = minifier_func(content)
        
        new_path = file_path.replace(f'.{ext}', f'.min.{ext}')
        
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(minified)
            
        original_size = len(content)
        new_size = len(minified)
        print(f"Minified {file_path}: {original_size/1024:.2f}KB -> {new_size/1024:.2f}KB (Saved: {(original_size-new_size)/1024:.2f}KB)")
        return True
    except Exception as e:
        print(f"Error minifying {file_path}: {e}")
        return False

if __name__ == "__main__":
    process_file('e:/appdev/vexil-logic-games/assets/css/style.css', minify_css, 'css')
    process_file('e:/appdev/vexil-logic-games/assets/js/main.js', minify_js, 'js')
    process_file('e:/appdev/vexil-logic-games/assets/js/app-loader.js', minify_js, 'js')
