import re
import sys

def fix_test_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add import at the top after CreatePostUseCase import
    if 'from app.modules.posts.domain.entities.post_enums import' not in content:
        content = content.replace(
            'from app.modules.posts.application.use_cases.create_post_use_case import (\n    CreatePostUseCase,\n)',
            'from app.modules.posts.application.use_cases.create_post_use_case import (\n    CreatePostUseCase,\n)\nfrom app.modules.posts.domain.entities.post_enums import PostCategory, PostScope'
        )
    
    # Fix all execute calls - add scope and category
    # Pattern 1: execute with city_code
    pattern1 = r'(await use_case\.execute\(\s*owner_id=\w+,\s*)(city_code=)'
    replacement1 = r'\1scope=PostScope.CITY,\n            category=PostCategory.TRADE,\n            \2'
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: execute with owner_id=str(uuid4()), city_code
    pattern2 = r'(await use_case\.execute\(\s*owner_id=str\(uuid4\(\)\),\s*)(city_code=)'
    replacement2 = r'\1scope=PostScope.CITY,\n                category=PostCategory.TRADE,\n                \2'
    content = re.sub(pattern2, replacement2, content)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Fixed {filepath}")

if __name__ == '__main__':
    fix_test_file('tests/unit/posts/application/use_cases/test_create_post_use_case.py')
