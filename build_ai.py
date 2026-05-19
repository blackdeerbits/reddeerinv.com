#!/usr/bin/env python3
"""
Build the AI Library section from markdown book sources.
"""

import os
import re
import html as html_mod
import json

PROJECT_ROOT = '/Users/siddev/reddeerinv.com'
AI_ROOT = f'{PROJECT_ROOT}/ai'

# Book definitions
BOOKS = [
    {
        'slug': 'the-waiting-game',
        'title': 'The Waiting Game',
        'subtitle': 'How Inference Economics Shapes the Future of AI',
        'description': 'A journey through the memory wall, KV caches, batch economics, speculative decoding, and custom silicon — explaining why everything in AI slows down before it gets faster.',
        'source_dir': '/Users/siddev/Desktop/llm_engineers_handbook/epub/v37/source',
        'chapters': [
            '00_introduction.md',
            '01_memory_wall.md',
            '02_kv_cache.md',
            '03_batch_economics.md',
            '04_spec_decode.md',
            '05_moe.md',
            '06_custom_silicon.md',
            '07_the_waiting_game.md',
            '08_afterword.md',
            '09_sources.md',
        ],
    },
    {
        'slug': 'beyond-the-waiting-game',
        'title': 'Beyond the Waiting Game',
        'subtitle': 'How AI is Learning to Work Around the Memory Wall',
        'description': 'The sequel exploring what comes after inference economics — architectures and techniques that reshape how models think.',
        'source_dir': '/Users/siddev/Desktop/beyond_the_waiting_game',
        'chapters': None,  # single manuscript
    },
    {
        'slug': 'the-model-that-does-everything',
        'title': 'The Model That Does Everything',
        'subtitle': 'What NVIDIA\'s Diffusion LM Means for Inference',
        'description': 'A critical analysis of NVIDIA\'s Nemotron-Labs-Diffusion — what the three-mode diffusion model means for hardware, where it breaks, and what to build now.',
        'source_dir': '/Users/siddev/Desktop/beyond_the_waiting_game/nemotron_diffusion_guide',
        'chapters': None,  # single manuscript
    },
    {
        'slug': 'slimqwen-reference',
        'title': 'SlimQwen Reference Book',
        'subtitle': 'A Guide to Compressing and Optimizing Large Language Models',
        'description': 'Practical techniques for shrinking giant AI brains: compression, mixture of experts, pruning, merging, and recovery training.',
        'source_dir': '/Users/siddev/slimqwen-reference-book/chapters',
        'chapters': [
            '01-the-ai-compression-problem.md',
            '02-mixture-of-experts.md',
            '03-the-art-of-the-cut.md',
            '04-merging-and-preserving.md',
            '05-the-recovery-training.md',
            '06-the-slow-squeeze.md',
            '07-results-and-efficiency.md',
            '08-takeaways-and-road-ahead.md',
        ],
    },
]

# ============================================================
# MARKDOWN TO HTML
# ============================================================

def md_to_html(text):
    """Convert markdown to clean HTML suitable for reading."""
    lines = text.split('\n')
    output = []
    in_ul = False
    in_ol = False
    in_blockquote = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            if in_ul:
                output.append('</ul>')
                in_ul = False
            if in_ol:
                output.append('</ol>')
                in_ol = False
            if in_blockquote:
                output.append('</blockquote>')
                in_blockquote = False
            i += 1
            continue
        
        # Headings
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            if in_ul:
                output.append('</ul>')
                in_ul = False
            if in_ol:
                output.append('</ol>')
                in_ol = False
            level = len(m.group(1))
            text = m.group(2)
            output.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue
        
        # Blockquote
        if line.startswith('> '):
            if not in_blockquote:
                output.append('<blockquote>')
                in_blockquote = True
            output.append(line[2:])
            i += 1
            continue
        
        # Unordered list
        m = re.match(r'^(-|\*)\s+(.+)$', line)
        if m:
            if not in_ul:
                output.append('<ul>')
                in_ul = True
            output.append(f'<li>{m.group(2)}</li>')
            i += 1
            continue
        
        # Ordered list
        m = re.match(r'^(\d+)\.\s+(.+)$', line)
        if m:
            if not in_ol:
                output.append('<ol>')
                in_ol = True
            output.append(f'<li>{m.group(2)}</li>')
            i += 1
            continue
        
        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            if in_ul:
                output.append('</ul>')
                in_ul = False
            if in_ol:
                output.append('</ol>')
                in_ol = False
            output.append('<hr>')
            i += 1
            continue
        
        # Regular paragraph
        if in_ul:
            output.append('</ul>')
            in_ul = False
        if in_ol:
            output.append('</ol>')
            in_ol = False
        if in_blockquote:
            output.append('</blockquote>')
            in_blockquote = False
        
        output.append(f'<p>{line}</p>')
        i += 1
    
    # Close any open tags
    if in_ul:
        output.append('</ul>')
    if in_ol:
        output.append('</ol>')
    if in_blockquote:
        output.append('</blockquote>')
    
    html = '\n'.join(output)
    
    # Inline formatting
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    return html

# ============================================================
# PAGE TEMPLATES
# ============================================================

def book_page(title, body, extra_head=''):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_mod.escape(title)} — AI Library — Red Deer Investments</title>
  <link rel="stylesheet" href="/assets/css/style.css">
  {extra_head}
</head>
<body class="ai-section">
<div class="ai-header-bar">
  <a href="/">&larr; Back to Red Deer Investments</a> &nbsp;·&nbsp; 
  <a href="/ai/">AI Library Home</a>
</div>
<div class="container">
{body}
</div>
</body>
</html>'''

# ============================================================
# BUILD EACH BOOK
# ============================================================

all_chapters = []  # for llms.txt

for book in BOOKS:
    slug = book['slug']
    book_dir = f'{AI_ROOT}/{slug}/chapters'
    os.makedirs(book_dir, exist_ok=True)
    
    chapters = []
    
    if book['chapters']:
        # Multi-file chapters
        for cf in book['chapters']:
            path = os.path.join(book['source_dir'], cf)
            if not os.path.exists(path):
                print(f"  MISSING: {path}")
                continue
            with open(path, 'r') as f:
                raw = f.read()
            chapters.append({'file': cf, 'content': raw})
    else:
        # Single manuscript - split on headings
        path = os.path.join(book['source_dir'], 'manuscript.md')
        if os.path.exists(path):
            with open(path, 'r') as f:
                raw = f.read()
            # Remove frontmatter
            if raw.startswith('---'):
                parts = raw.split('---', 2)
                raw = parts[2] if len(parts) > 2 else raw
            
            # Split on ## headings (chapters)
            sections = re.split(r'\n(?=## )', raw.strip())
            for i, section in enumerate(sections):
                header_match = re.match(r'^## (.+)', section.strip())
                title = header_match.group(1) if header_match else f'Chapter {i+1}'
                chapters.append({'file': f'chapter-{i+1}.md', 'content': section, 'title': title})
    
    print(f"\n=== {book['title']} ({len(chapters)} chapters) ===")
    
    # Generate chapter pages
    chapter_list = []
    for i, ch in enumerate(chapters):
        title_line = ch['content'].split('\n')[0].lstrip('#').strip()
        html_content = md_to_html(ch['content'])
        
        # Find next/prev
        prev_link = ''
        next_link = ''
        if i > 0:
            prev_link = f'<a href="/ai/{slug}/chapters/{os.path.splitext(chapters[i-1]["file"])[0]}.html">&larr; Previous</a>'
        if i < len(chapters) - 1:
            next_link = f'<a href="/ai/{slug}/chapters/{os.path.splitext(chapters[i+1]["file"])[0]}.html">Next &rarr;</a>'
        
        # Chapter number badge
        ch_num = f'Chapter {i}' if i > 0 and i < len(chapters)-1 else ('Introduction' if i == 0 else '')
        if ch.get('title'):
            ch_num = ch['title']
        
        body = f'''<article>
  <div class="post-meta" style="margin-bottom:1rem;">
    <a href="/ai/{slug}/">&larr; Back to {html_mod.escape(book['title'])}</a>
  </div>
  <div class="post-body">
{html_content}
  </div>
  <div class="post-nav">
    {prev_link}
    {next_link}
  </div>
</article>'''
        
        ch_filename = os.path.splitext(ch['file'])[0]
        html_out = book_page(title_line, body)
        with open(f'{book_dir}/{ch_filename}.html', 'w') as f:
            f.write(html_out)
        
        # Track for book landing
        chapter_list.append({
            'num': i,
            'title': title_line,
            'filename': f'{ch_filename}.html',
            'url': f'/ai/{slug}/chapters/{ch_filename}.html'
        })
        
        # Track for llms.txt
        all_chapters.append({
            'book': book['title'],
            'chapter': title_line,
            'url': f'https://reddeerinv.com/ai/{slug}/chapters/{ch_filename}.html'
        })
        
        print(f"  [{i}] {title_line}")
    
    # Generate book landing page
    chapter_links = '<ul class="chapter-list">\n'
    for ch in chapter_list:
        num_label = f'{ch["num"]}' if ch["num"] > 0 else ''
        chapter_links += f'  <li><span class="chapter-num">{num_label}</span><a href="{ch["url"]}">{html_mod.escape(ch["title"])}</a></li>\n'
    chapter_links += '</ul>'
    
    landing_body = f'''<div class="book-card" style="padding:3rem 2rem;">
  <h1 style="font-family:system-ui;font-size:1.8rem;font-weight:600;margin-bottom:0.3rem;color:var(--color-ai);">{html_mod.escape(book['title'])}</h1>
  <p class="book-meta">{html_mod.escape(book['subtitle'])}</p>
  <p style="font-size:0.9rem;line-height:1.6;margin:1rem 0 2rem;">{html_mod.escape(book['description'])}</p>
  <h2 style="font-family:system-ui;font-size:1.1rem;font-weight:600;margin-bottom:1rem;">Contents</h2>
  {chapter_links}
</div>'''
    
    # JSON-LD
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": book['title'],
        "author": {"@type": "Person", "name": "the_red_deer"},
        "description": book['description'],
        "numberOfPages": len(chapters),
        "publisher": "Red Deer Investments"
    }
    
    extra_head = f'<script type="application/ld+json">{json.dumps(json_ld)}</script>'
    
    html_out = book_page(f'{book["title"]}', landing_body, extra_head)
    os.makedirs(f'{AI_ROOT}/{slug}', exist_ok=True)
    with open(f'{AI_ROOT}/{slug}/index.html', 'w') as f:
        f.write(html_out)
    
    print(f"  Landing page: /ai/{slug}/")

# ============================================================
# AI LIBRARY LANDING PAGE
# ============================================================

book_cards = ''
for book in BOOKS:
    book_cards += f'''
<div class="book-card">
  <h2><a href="/ai/{book['slug']}/">{html_mod.escape(book['title'])}</a></h2>
  <p class="book-meta">{html_mod.escape(book['subtitle'])}</p>
  <p>{html_mod.escape(book['description'])}</p>
</div>'''

ai_landing = f'''<div style="max-width:var(--max-width);margin:0 auto;padding:3rem 1.5rem;">
  <h1 style="font-family:system-ui;font-size:2rem;font-weight:600;margin-bottom:0.3rem;color:var(--color-ai);">AI Library</h1>
  <p class="book-meta" style="font-size:0.85rem;margin-bottom:2.5rem;line-height:1.5;">A growing repository of short-form books exploring inference economics, model compression, and the architecture of modern AI — written for both human readers and AI agents.</p>
  {book_cards}
  <div style="margin-top:2.5rem;padding-top:1.5rem;border-top:1px solid var(--color-border);">
    <p style="font-size:0.8rem;color:var(--color-text-muted);">This section is also optimized for LLM and AI agent consumption. See <a href="/ai/llms.txt">llms.txt</a> for machine-readable structured content.</p>
  </div>
</div>'''

with open(f'{AI_ROOT}/index.html', 'w') as f:
    f.write(book_page('AI Library', ai_landing))

print("\n=== AI LANDING PAGE ===")
print("  /ai/index.html")

# ============================================================
# LLMS.TXT
# ============================================================

llms = f'''# Red Deer Investments — AI Library

> Structured content for LLMs and AI agents. This file serves as a machine-readable entrypoint to the AI section.

## Available Books

'''

for book in BOOKS:
    llms += f'### {book["title"]}\n'
    llms += f'- Description: {book["description"]}\n'
    llms += f'- Landing page: https://reddeerinv.com/ai/{book["slug"]}/\n'
    llms += f'- Chapters:\n'
    for ch in all_chapters:
        if ch['book'] == book['title']:
            llms += f'  - [{ch["chapter"]}](https://reddeerinv.com{ch["url"]})\n'
    llms += '\n'

llms += '''
## How to read

Each book is rendered as clean semantic HTML with chapter navigation, JSON-LD structured data, and accessible headings. All pages are static HTML — no JavaScript required.

## Metadata format

Every book page includes:
- JSON-LD (schema.org/Book) in the <head>
- Semantic HTML5 landmarks (<article>, <nav>, <section>)
- Reading progress via chapter ordering
- Next/Previous navigation

## Crawl settings

- Rate limit: none (static files on CDN)
- Prefer: text/html
- Sitemap: https://reddeerinv.com/sitemap.xml
'''

with open(f'{AI_ROOT}/llms.txt', 'w') as f:
    f.write(llms)

print("\n=== llms.txt ===")
print("  /ai/llms.txt")
print("\n=== AI SECTION BUILD COMPLETE ===")
