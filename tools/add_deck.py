#!/usr/bin/env python3
"""Add a pitch deck preview to the site.

Usage:  python3 tools/add_deck.py path/to/deck.pdf slug "Title" "Format · Status" "One-line logline"

Renders ONLY the first 3 pages of the PDF to images/decks/<slug>/p1-3.jpg
and prints the HTML card to paste inside <div class="deck-list"> in index.html.
The PDF itself is never copied into the site — the full deck stays private
and is sent by Ekenem when someone requests it.
"""
import os, subprocess, sys, tempfile, html
from PIL import Image

pdf, slug, title, fmt, logline = sys.argv[1:6]
out = os.path.join('images', 'decks', slug)
os.makedirs(out, exist_ok=True)
with tempfile.TemporaryDirectory() as t:
    subprocess.run(['pdftoppm', '-f', '1', '-l', '3', '-r', '110', '-jpeg', pdf, os.path.join(t, 'p')], check=True)
    pages = sorted(f for f in os.listdir(t) if f.endswith('.jpg'))
    for i, f in enumerate(pages[:3], 1):
        im = Image.open(os.path.join(t, f)).convert('RGB')
        if im.width > 1400:
            im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        im.save(os.path.join(out, f'p{i}.jpg'), 'JPEG', quality=80, optimize=True, progressive=True)
        print('saved', os.path.join(out, f'p{i}.jpg'), im.size, file=sys.stderr)

e = html.escape
pages_html = '\n'.join(
    f'          <button type="button" class="deck-page" data-full="images/decks/{slug}/p{i}.jpg" aria-label="View page {i} of the {e(title)} deck">'
    f'<img src="images/decks/{slug}/p{i}.jpg" alt="{e(title)} pitch deck, page {i}" loading="lazy"/><span class="deck-pn">0{i}</span></button>'
    for i in (1, 2, 3))
print(f'''      <article class="deck" data-deck="{e(title)}">
        <div class="deck-meta">
          <div class="wnet">{e(fmt)}</div>
          <h3 class="deck-title">{e(title)}</h3>
          <p class="deck-log">{e(logline)}</p>
          <a class="btn-primary deck-req" href="mailto:efugede@gmail.com">Request full deck</a>
        </div>
        <div class="deck-pages">
{pages_html}
          <a class="deck-more deck-req" href="mailto:efugede@gmail.com"><span class="deck-lock" aria-hidden="true"></span><span>Full deck<br/>on request</span></a>
        </div>
      </article>''')
