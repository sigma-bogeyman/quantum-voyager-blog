"""
build.py — regenerates the Quantum Voyager site from Markdown source files.

Usage:
    python3 build.py

Reads:
    content/posts/*.md   (one file per post, with frontmatter)
    content/pages/*.md   (section pages: Tech-Tactics, SciSphere, etc.)

Writes:
    index.html, posts/*.html, pages/*.html   (ready for GitHub Pages)

Frontmatter fields for a post:
    title:    Post title
    date:     YYYY-MM-DD (or YYYY-MM-DD HH:MM:SS)
    status:   publish | draft
    category: tech-tactics | quantum-quill | unchartered-dimensions | scisphere | (blank)
    image:    full URL to a featured image (optional)
"""

import frontmatter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT_POSTS = ROOT / 'content' / 'posts'
CONTENT_PAGES = ROOT / 'content' / 'pages'
OUT = ROOT

NAV_PAGES = [
    ('Tech-Tactics', 'tech-tactics'),
    ("Quantum Quill's", 'quantum-quills'),
    ('Uncharted Dimensions', 'uncharted-dimensions'),
    ('Scisphere', 'uncharted-dimensions-2'),
    ('Contact', 'contact'),
]

PAGE_TO_CATEGORY = {
    'tech-tactics': 'tech-tactics',
    'quantum-quills': 'quantum-quill',
    'uncharted-dimensions': 'unchartered-dimensions',
    'uncharted-dimensions-2': 'scisphere',
}

FALLBACK_GRADIENTS = [
    'linear-gradient(135deg,#7d8a9c,#4a5262)',
    'linear-gradient(135deg,#9c8a6a,#5c4a3a)',
    'linear-gradient(135deg,#8a7a9c,#4a3a5c)',
    'linear-gradient(135deg,#6a8a7a,#3a5c4a)',
]


def fmt_date(raw):
    if not raw:
        return None
    raw = str(raw)
    for pattern in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            dt = datetime.strptime(raw, pattern)
            return dt.strftime('%d %b %Y').upper()
        except ValueError:
            continue
    return None


def sort_key(post):
    raw = str(post.get('date') or '')
    for pattern in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(raw, pattern)
        except ValueError:
            continue
    return datetime.min


def nav_html(depth=''):
    links = ''.join(f'<a href="{depth}pages/{slug}.html">{label}</a>\n' for label, slug in NAV_PAGES)
    return f'<a href="{depth}index.html">Home</a>\n{links}'


def header_html(depth=''):
    return f'''<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{depth}index.html">THE <span>QUANTUM</span> VOYAGER</a>
    <nav class="site-nav">
      {nav_html(depth)}
    </nav>
  </div>
</header>'''


def footer_html():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <p>&copy; {datetime.now().year} The Quantum Voyager &mdash; case file relayed via GitHub Pages</p>
    <p>Infinity &amp; Beyond</p>
  </div>
</footer>'''


def page_shell(title, depth, body, css_depth=None):
    if css_depth is None:
        css_depth = depth
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} &mdash; The Quantum Voyager</title>
<link rel="stylesheet" href="{css_depth}assets/style.css">
</head>
<body>
{header_html(depth)}
{body}
{footer_html()}
</body>
</html>'''


def thumb_style(post, idx):
    img = post.get('image')
    if img:
        return f"background-image:url('{img}');"
    return f"background:{FALLBACK_GRADIENTS[idx % len(FALLBACK_GRADIENTS)]};"


def load_posts():
    posts = []
    for path in sorted(CONTENT_POSTS.glob('*.md')):
        post = frontmatter.load(path)
        data = dict(post.metadata)
        data['slug'] = path.stem
        data['body'] = post.content
        posts.append(data)
    return posts


def load_pages():
    pages = []
    for path in sorted(CONTENT_PAGES.glob('*.md')):
        pg = frontmatter.load(path)
        data = dict(pg.metadata)
        data['slug'] = data.get('slug', path.stem)
        data['body'] = pg.content
        pages.append(data)
    return pages


def build_entries_html(post_list, log_number, link_prefix='posts/'):
    out = ''
    for idx, post in enumerate(post_list):
        num = log_number[post['slug']]
        status_class = 'status-confirmed' if post['status'] == 'publish' else 'status-draft'
        status_label = 'CONFIRMED' if post['status'] == 'publish' else 'UNCONFIRMED'
        date_str = fmt_date(post.get('date')) or 'undated'
        out += f'''<div class="entry">
  <div class="entry-thumb" style="{thumb_style(post, idx)}">
    <div class="tape tl"></div><div class="tape br"></div>
    <div class="entry-num">{num}</div>
  </div>
  <div class="entry-body">
    <h2><a href="{link_prefix}{post['slug']}.html">{post['title']}</a></h2>
    <div class="entry-meta">{date_str}</div>
  </div>
  <div class="status-tag {status_class}">{status_label}</div>
</div>
'''
    return out


def main():
    posts = load_posts()
    pages = load_pages()

    published = [p for p in posts if p.get('status') == 'publish']
    drafts = [p for p in posts if p.get('status') != 'publish']
    published.sort(key=sort_key, reverse=True)
    ordered_posts = published  # drafts are excluded from the public site entirely

    log_number = {}
    for i, post in enumerate(ordered_posts):
        log_number[post['slug']] = str(len(ordered_posts) - i).zfill(3)

    # ---------- Post pages (published only — drafts are never written) ----------
    (OUT / 'posts').mkdir(exist_ok=True)
    for post in published:
        status_class = 'status-confirmed' if post['status'] == 'publish' else 'status-draft'
        status_label = 'CONFIRMED' if post['status'] == 'publish' else 'UNCONFIRMED'
        date_str = fmt_date(post.get('date')) or 'DATE UNKNOWN'

        photo_html = ''
        if post.get('image'):
            photo_html = f'''<div class="article-photo">
  <div class="photo-inner" style="background-image:url('{post['image']}');">
    <div class="tape tl"></div><div class="tape br"></div>
    <div class="caption">FIG. 1 &mdash; CASE {log_number[post['slug']]}</div>
  </div>
</div>'''

        body_html = f'''<div class="article-header">
  <a class="back-link" href="../index.html">&larr; Back to case log</a>
  <h1>{post['title']}</h1>
  <div class="article-meta">
    <span>{date_str}</span>
    <span class="status-tag {status_class}">{status_label}</span>
  </div>
</div>
{photo_html}
<article class="content">
<div class="stamp-box">CASE {log_number[post['slug']]}</div>
{post['body']}
</article>'''

        html_doc = page_shell(post['title'], '../', body_html)
        (OUT / 'posts' / f"{post['slug']}.html").write_text(html_doc, encoding='utf-8')

    # ---------- Section / static pages ----------
    (OUT / 'pages').mkdir(exist_ok=True)
    for pg in pages:
        category_slug = PAGE_TO_CATEGORY.get(pg['slug'])
        section_html = ''
        if category_slug:
            matching = [p for p in ordered_posts if p.get('category') == category_slug]
            if matching:
                entries_html_pg = build_entries_html(matching, log_number, link_prefix='../posts/')
                section_html = f'''<div class="log">
  <div class="log-heading">Case Log</div>
  {entries_html_pg}
</div>'''
            else:
                section_html = '''<div class="log">
  <p style="color: var(--faded); font-family: var(--mono); font-size: 0.85rem; padding: 20px 2px;">No cases filed in this section yet.</p>
</div>'''

        body_html = f'''<div class="article-header">
  <a class="back-link" href="../index.html">&larr; Back to home</a>
  <h1>{pg['title']}</h1>
</div>
<article class="content">
{pg['body']}
</article>
{section_html}'''
        html_doc = page_shell(pg['title'], '../', body_html)
        (OUT / 'pages' / f"{pg['slug']}.html").write_text(html_doc, encoding='utf-8')

    # ---------- Index ----------
    entries_html = build_entries_html(ordered_posts, log_number, link_prefix='posts/')
    index_body = f'''<div class="hero">
  <div class="eyebrow">Pioneering Ideas in an Infinite Universe</div>
  <h1>Genesis</h1>
  <p class="lede">Welcome to <em>The Quantum Voyager</em>, a space where curiosity meets exploration. Here, we delve into the mysteries of the universe, the marvels of technology, and the intricate dance of science and humanity. Whether you're a tech enthusiast, a science aficionado, or someone seeking thought-provoking insights, this is your gateway to journeys that expand the mind and spark imagination. Let's voyage into the unknown, one article at a time.</p>
</div>
<div class="log">
  <div class="log-heading">Case Log</div>
  {entries_html}
</div>'''
    index_doc = page_shell('The Quantum Voyager', '', index_body, css_depth='')
    (OUT / 'index.html').write_text(index_doc, encoding='utf-8')

    print(f"Built {len(posts)} posts ({len(published)} published, {len(drafts)} draft) and {len(pages)} section pages.")


if __name__ == '__main__':
    main()
