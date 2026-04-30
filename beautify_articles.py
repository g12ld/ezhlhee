import os
import re
from pathlib import Path

# --- TEMPLATES ---

HEADER_TEMPLATE = """
<header>
    <div class="container header-content">
        <div class="logo"><img src="https://i.ibb.co/8DhNMfds/14.png" alt="ازهلها"></div>
        <div class="menu-toggle" onclick="toggleMenu(this)"><span></span><span></span><span></span></div>
        <nav>
            <ul>
                <li><a href="../index.html#hero">الرئيسية</a></li>
                <li><a href="../index.html#services-tabs">الباقات والخدمات</a></li>
                <li><a href="../index.html#portfolio">أعمالنا</a></li>
                <li><a href="../index.html#partners">شركاؤنا</a></li>
                <li><a href="../index.html#blog">المدونة</a></li>
            </ul>
        </nav>
    </div>
</header>
"""

FOOTER_TEMPLATE = """
<footer>
    <div class="container footer-content">
        <h2 class="section-title">تواصل معنا</h2>
        <form class="contact-form">
            <input type="text" placeholder="الاسم الكامل">
            <input type="email" placeholder="البريد الإلكتروني">
            <textarea rows="5" placeholder="رسالتك"></textarea>
            <button class="btn-main" type="submit">إرسال الرسالة</button>
        </form>
    </div>
</footer>
"""

WHATSAPP_LINK = "https://wa.me/966501940155?text=مرحبا%20انا%20زائر%20من%20مقالة%20موقع%20ازهلها"

def extract_meta_tag(content, name):
    """Extracts a meta tag by name."""
    pattern = f'<meta name="{name}" content="(.*?)">'
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else f'<meta name="{name}" content="">'

def extract_title(content):
    """Extracts the title tag."""
    match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else '<title></title>'

def extract_body_content(content):
    """Extracts content from within the <body> tag."""
    match = re.search(r'<body[^>]*>(.*?)</body>', content, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    
    body_content = match.group(1).strip()
    
    # Attempt to remove old header, main, footer if they exist to avoid duplication
    body_content = re.sub(r'<header.*?</header>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
    body_content = re.sub(r'<main.*?</main>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
    body_content = re.sub(r'<footer.*?</footer', '', body_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove script tags and the whatsapp/back buttons if they were already there
    body_content = re.sub(r'<script.*?</script>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
    body_content = re.sub(r'<a href="[^"]*wa\.me[^"]*".*?</a>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
    body_content = re.sub(r'<a href="[^"]*index\.html".*?</a>', '', body_content, flags=re.DOTALL | re.IGNORECASE)


    return body_content.strip()


def process_article(file_path):
    """Reads an article, transforms it, and overwrites it."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Extract essential parts from the original file
        title_tag = extract_title(original_content)
        description_tag = extract_meta_tag(original_content, "description")
        keywords_tag = extract_meta_tag(original_content, "keywords")
        
        # The main content is whatever is in the body
        body_inner_content = extract_body_content(original_content)
        
        # If the body was empty or only contained boilerplate, we might get nothing.
        # Fallback to a simple body regex if our cleaning removed everything.
        if not body_inner_content:
             body_match = re.search(r'<body[^>]*>(.*?)</body>', original_content, re.IGNORECASE | re.DOTALL)
             if body_match:
                 body_inner_content = body_match.group(1).strip()


        # Build the new HTML structure
        new_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {title_tag}
    {description_tag}
    {keywords_tag}
    <link rel="stylesheet" href="../style.css">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap" rel="stylesheet">
</head>
<body>
    {HEADER_TEMPLATE}

    <main class="article-content container">
        {body_inner_content}
        <a href="{WHATSAPP_LINK}" class="whatsapp-button">تواصل معنا عبر واتساب</a>
        <a href="../index.html" class="back-home">العودة للصفحة الرئيسية</a>
    </main>

    {FOOTER_TEMPLATE}

    <script>
        function toggleMenu(e){{
            const nav = document.querySelector('header nav');
            nav.classList.toggle('active');
        }}
    </script>
</body>
</html>"""

        # Overwrite the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        print(f"Successfully processed: {file_path.name}")

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")


def main():
    articles_dir = Path('articles')
    if not articles_dir.is_dir():
        print(f"Directory not found: {articles_dir}")
        return

    html_files = list(articles_dir.glob('*.html'))
    
    print(f"Found {len(html_files)} articles to process.")

    for file_path in html_files:
        process_article(file_path)

    print("Finished processing all articles.")

if __name__ == "__main__":
    main()
