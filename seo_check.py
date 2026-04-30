import os
import re
from pathlib import Path

def check_seo(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for title
    if not re.search(r'<title[^>]*>.*?</title>', content, re.IGNORECASE | re.DOTALL):
        issues.append("Missing <title> tag")
    
    # Check for meta description
    if not re.search(r'<meta[^>]*name=["\']description["\'][^>]*>', content, re.IGNORECASE):
        issues.append("Missing meta description")
    
    # Check for viewport meta
    if not re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*>', content, re.IGNORECASE):
        issues.append("Missing viewport meta tag")
    
    # Check for H1
    h1_count = len(re.findall(r'<h1[^>]*>.*?</h1>', content, re.IGNORECASE | re.DOTALL))
    if h1_count == 0:
        issues.append("No H1 tag found")
    elif h1_count > 1:
        issues.append(f"Multiple H1 tags ({h1_count})")
    
    # Check images without alt
    img_tags = re.findall(r'<img[^>]*>', content, re.IGNORECASE)
    images_without_alt = 0
    for img in img_tags:
        if not re.search(r'alt=["\'][^"\']*["\']', img, re.IGNORECASE):
            images_without_alt += 1
    if images_without_alt > 0:
        issues.append(f"{images_without_alt} images without alt attribute")
    
    return issues

def main():
    root_dir = Path('.')
    html_files = list(root_dir.rglob('*.html'))
    
    total_files = len(html_files)
    files_with_issues = 0
    
    for file_path in html_files:
        issues = check_seo(file_path)
        if issues:
            files_with_issues += 1
            print(f"\n{file_path}:")
            for issue in issues:
                print(f"  - {issue}")
    
    print(f"\nSummary: Checked {total_files} HTML files, {files_with_issues} have SEO issues.")

if __name__ == "__main__":
    main()