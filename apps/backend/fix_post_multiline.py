#!/usr/bin/env python3
import re
import glob

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Add imports if missing
    if 'PostScope' not in content or 'PostCategory' not in content:
        if 'from app.modules.posts.domain.entities.post import' in content:
            content = content.replace(
                'from app.modules.posts.domain.entities.post import',
                'from app.modules.posts.domain.entities.post import'
            )
            if 'from app.modules.posts.domain.entities.post_enums import' not in content:
                # Add import after Post import
                pattern = r'(from app\.modules\.posts\.domain\.entities\.post import [^\n]+)'
                replacement = r'\1\nfrom app.modules.posts.domain.entities.post_enums import PostCategory, PostScope'
                content = re.sub(pattern, replacement, content)
    
    # Fix Post() initialization - find status= line and add scope/category after it
    # Pattern: status=PostStatus.XXXX, followed by newline
    # We need to add scope and category before expires_at
    
    # Find Post( ... status=... with city_code but missing scope
    patterns = [
        # Pattern 1: status on its own line, city_code present, missing scope
        (r'(Post\([^)]*status=PostStatus\.\w+,)\s*\n(\s+)(expires_at=)',
         r'\1\n\2scope=PostScope.CITY,\n\2category=PostCategory.TRADE,\n\2\3'),
        
        # Pattern 2: status on its own line, city_code present, NO expires_at nearby
        (r'(Post\([^)]*status=PostStatus\.\w+,)\s*\n(\s+)(city_code=)',
         r'\1\n\2scope=PostScope.CITY,\n\2category=PostCategory.TRADE,\n\2\3'),
    ]
    
    for pattern, replacement in patterns:
        # Check if scope is already present
        if 'scope=' not in content or content.count('scope=') < content.count('Post('):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Fixed {filepath}")
        return True
    else:
        print(f"- Skipped {filepath}")
        return False

# Process all test files
test_files = glob.glob('tests/unit/posts/**/*.py', recursive=True)
test_files = [f for f in test_files if '__pycache__' not in f and '__init__' not in f]

for f in test_files:
    fix_file(f)
