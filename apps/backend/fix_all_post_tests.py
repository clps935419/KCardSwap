#!/usr/bin/env python3
"""Fix all Post-related tests to include scope and category parameters"""
import re
import glob

def add_imports_if_missing(content):
    """Add PostScope and PostCategory imports if not present"""
    if 'from app.modules.posts.domain.entities.post_enums import' in content:
        return content
    
    # Find where to add the import
    post_import_pattern = r'(from app\.modules\.posts\.domain\.entities\.post import[^\n]+)'
    if re.search(post_import_pattern, content):
        content = re.sub(
            post_import_pattern,
            r'\1\nfrom app.modules.posts.domain.entities.post_enums import PostCategory, PostScope',
            content
        )
    return content

def fix_post_initialization(content):
    """Fix Post() initialization to include scope and category"""
    # Pattern: Post(...) with named arguments
    # We need to add scope=PostScope.CITY, category=PostCategory.TRADE after status
    
    # Find Post( and add scope/category after status parameter
    pattern = r'Post\(\s*id=([^,]+),\s*owner_id=([^,]+),\s*title=([^,]+),\s*content=([^,]+),\s*status=([^,]+),'
    replacement = r'Post(\n            id=\1,\n            owner_id=\2,\n            title=\3,\n            content=\4,\n            status=\5,\n            scope=PostScope.CITY,\n            category=PostCategory.TRADE,'
    content = re.sub(pattern, replacement, content)
    
    return content

def process_file(filepath):
    """Process a single test file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original = content
        content = add_imports_if_missing(content)
        content = fix_post_initialization(content)
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✓ Fixed {filepath}")
            return True
        else:
            print(f"- No changes needed for {filepath}")
            return False
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    test_files = glob.glob('tests/unit/posts/**/*.py', recursive=True)
    test_files = [f for f in test_files if '__pycache__' not in f and '__init__' not in f]
    
    print(f"Found {len(test_files)} test files to process\n")
    fixed_count = 0
    
    for filepath in test_files:
        if process_file(filepath):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
