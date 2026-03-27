import os
import re

templates_dir = r"c:\React Projects\ImpactNexus\Admorph\templates"

def fix_template(content):
    # Fix :root variables
    content = re.sub(r'--primary:\s*\{\s*\{\s*theme\.primary_color\s*\}\s*\}\s*;', r'--primary: {{ theme.primary_color }};', content)
    content = re.sub(r'--secondary:\s*\{\s*\{\s*theme\.secondary_color\s*\}\s*\}\s*;', r'--secondary: {{ theme.secondary_color }};', content)
    content = re.sub(r'--text-color:\s*\{\s*\{\s*theme\.text_color\s*\}\s*\}\s*;', r'--text-color: {{ theme.text_color }};', content)
    content = re.sub(r'--border-radius:\s*\{\s*\{\s*theme\.border_radius\s*\}\s*\}\s*;', r'--border-radius: {{ theme.border_radius }};', content)
    
    # Fix width/height with spaces
    content = re.sub(r'width:\s*\{\s*\{\s*ratio\.width\s*\}\s*\}\s*px;', r'width: {{ ratio.width }}px;', content)
    content = re.sub(r'height:\s*\{\s*\{\s*ratio\.height\s*\}\s*\}\s*px;', r'height: {{ ratio.height }}px;', content)
    
    # Generic fix for multi-line {{ }} in CSS
    def clean_tags(match):
        inner = match.group(1).strip()
        # remove internal newlines and extra spaces
        inner = re.sub(r'\s+', ' ', inner)
        return f'{{{{ {inner} }}}}'
    
    content = re.sub(r'\{\s*\{(.*?)\}\s*\}', clean_tags, content, flags=re.DOTALL)
    
    # Fix cases like "px;" being on a new line after the tag
    content = re.sub(r'\}\}\s+px;', r'}}px;', content)
    
    return content

for filename in os.listdir(templates_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            old_content = f.read()
            
        new_content = fix_template(old_content)
        
        if old_content != new_content:
            with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)
            print(f"Fixed {filename}")
        else:
            print(f"No changes needed for {filename}")
