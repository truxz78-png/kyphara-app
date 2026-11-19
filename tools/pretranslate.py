"""Makes the ready-made translation packs tr/<lang>.json for every language of the menu.

With a pack, the app shows a language instantly and complete (no slow, half-translated page).
Hand-reviewed texts (FIX in index.html and legal-tr.js) still win over the pack.
Run it from Termux after changing texts of the page (Google blocks it from GitHub with 429):
    python3 tools/pretranslate.py            (all languages, about 5-8 minutes)
    python3 tools/pretranslate.py be uk ru   (only these)
Then: git add tr && git commit -m "Translation packs" && git push
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tr')
UA = {'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/124 Mobile Safari/537.36'}


def read(n):
    return open(os.path.join(ROOT, n), encoding='utf-8').read()


class Texts(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack = []; self.out = []
    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'img', 'input', 'meta', 'link', 'hr', 'source'): return
        a = dict(attrs)
        skip = tag in ('script', 'style', 'noscript', 'title', 'head') or a.get('translate') == 'no' \
            or 'notranslate' in (a.get('class') or '').split()
        self.stack.append(skip or (self.stack[-1] if self.stack else False))
    def handle_endtag(self, tag):
        if tag in ('br', 'img', 'input', 'meta', 'link', 'hr', 'source'): return
        if self.stack: self.stack.pop()
    def handle_data(self, d):
        d = ' '.join(d.split())
        if d and re.search(r'[^\W\d_]', d) and not (self.stack and self.stack[-1]) and d not in self.out:
            self.out.append(d)


def texts():
    out = []
    for name in ('index.html', 'privacy.html', 'terms.html'):
        p = Texts(); p.feed(read(name)); out += [t for t in p.out if t not in out]
    idx = read('index.html')
    dyn = ['Hide', 'About these links'] + re.findall(r"'([^']+)'", re.search(r'const SKIN=\[(.*?)\];', idx).group(1))
    return out + [d for d in dyn if d not in out]


def gt(lang, lines, tries=4):
    url = ('https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=' + lang +
           '&dt=t&q=' + urllib.parse.quote('\n'.join(lines)))
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                j = json.load(r)
            out = ''.join(x[0] for x in j[0]).split('\n')
            return [s.strip() for s in out]
        except Exception as e:
            last = e; time.sleep(3 * (i + 1))
    raise last


def cap(k, s):
    return s[:1].upper() + s[1:] if re.match(r'[A-Z]', k) and s else s


BRAND = 'Kyphara'; TOKEN = 'XQ7'   # the brand is sent as XQ7 so Google never changes it (Кифара, किफ़ारा...)


def prot(k):
    return k.replace(BRAND, TOKEN)


def unprot(v):
    return re.sub(r'XQ7|Xq7|xq7|ХQ7|XК7', BRAND, v)


def pack(lang, items):
    res, chunks, cur, n = {}, [], [], 0
    for k in items:
        if n + len(k) > 1500 and cur: chunks.append(cur); cur, n = [], 0
        cur.append(k); n += len(k) + 1
    if cur: chunks.append(cur)
    for c in chunks:
        o = gt(lang, [prot(k) for k in c])
        if len(o) != len(c):          # badly split: one by one
            o = [gt(lang, [prot(k)])[0] for k in c]
        for k, v in zip(c, o):
            if v and v == prot(k) and len(k) > 12:   # came back in English: ask again alone
                time.sleep(0.4); v = gt(lang, [prot(k)])[0]
            if v: res[k] = cap(k, unprot(v))
        time.sleep(0.4)
    return res


def main():
    menu = re.search(r"const LANGS=\{(.*?)\};", read('index.html')).group(1)
    langs = sys.argv[1:] or re.findall(r"(?:^|,)'?([a-zA-Z-]+)'?:'", menu)
    langs = [l for l in langs if l != 'en']
    items = texts()
    os.makedirs(OUT, exist_ok=True)
    print(f'{len(items)} texts x {len(langs)} languages')
    bad = []
    for i, lang in enumerate(langs, 1):
        try:
            res = pack(lang, items)
            miss = [k for k in items if k not in res]
            with open(os.path.join(OUT, lang + '.json'), 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, separators=(',', ':'))
            print(f'[{i}/{len(langs)}] {lang}: {len(res)}/{len(items)}' + (f'  ({len(miss)} missing)' if miss else ' ✓'))
            if miss: bad.append(lang)
        except Exception as e:
            print(f'[{i}/{len(langs)}] {lang}: ERROR {e}'); bad.append(lang)
    print('Done.' if not bad else 'Run again for: ' + ' '.join(bad))


if __name__ == '__main__':
    main()
