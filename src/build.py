"""Builds index.html from src/template.html + links.json + dictionaries (src/fix_es.json, src/i18n/*.txt).
Run from anywhere:  python3 src/build.py"""
import json, html, glob, os
SRC = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SRC)
p = lambda *a: os.path.join(*a)
L = json.load(open(p(ROOT, 'links.json'), encoding='utf-8'))
def S(lid, brand, title, desc, label='Shop on', nt=False):
    off = html.escape(L[lid]['official'])
    cls = ' class="notranslate"' if nt else ''
    return (f'<div class="store"><div><b{cls}>{title}</b><span>{desc}</span></div>'
            f'<a class="go" data-link="{lid}" href="{off}" target="_blank" rel="noopener sponsored">{label} <span class="notranslate">{brand}</span><em>Opens partner site ↗</em></a></div>\n')
C = lambda lid, title, desc, brand='Udemy': S(lid, brand, title, desc, 'Browse on')
G = {
'w-stores': S('shein-beauty', 'SHEIN', 'SHEIN Beauty', 'Makeup, nails, wigs and beauty tools at low prices', nt=True),
'stores': S('foreo', 'FOREO', 'FOREO', 'Facial cleansing brushes and skincare devices from Sweden', nt=True),
'makeup': S('ae-makeup', 'AliExpress', 'Makeup', 'Palettes, lipsticks, brushes and makeup kits'),
'skincare': S('ae-skincare', 'AliExpress', 'Skincare', 'Cleansers, serums, masks and moisturizers'),
'hair': S('ae-hair', 'AliExpress', 'Hair care', 'Hair oils, shampoos, treatments and hair tools'),
'nails': S('ae-nails', 'AliExpress', 'Nails', 'Gel polish, UV lamps, nail art and press-on nails'),
'india': S('nykaa', 'Nykaa', 'Nykaa', "India's leading beauty store: makeup, skincare, hair care and fragrance", nt=True)
       + S('hok-makeup', 'HOK Makeup', 'HOK Makeup', 'Makeup and Korean beauty brands', nt=True),
'luxury': S('forest-essentials', 'Forest Essentials', 'Forest Essentials', 'Luxury Ayurvedic skincare, hair care and fragrances from India', nt=True),
'middle-east': S('bbw-me', 'Bath & Body Works', 'Bath & Body Works', 'Body mists, lotions, shower gels and candles', nt=True)
       + S('vs-me', "Victoria's Secret", "Victoria's Secret Beauty", 'Fragrances, body mists and beauty gift sets', nt=True)
       + S('vperfumes', 'Vperfumes', 'Vperfumes', 'Designer and niche perfumes, bakhoor and gift sets', nt=True)
       + S('dermazone', 'DermaZone', 'DermaZone', 'Korean skincare, hair care and dermocosmetics', nt=True),
'men': S('ae-beard', 'AliExpress', 'Beard and shaving', 'Beard oils, balms, trimmers and shavers'),
'shipping': S('planet-express', 'Planet Express', 'US address for your orders', 'Get a US address and ship your online purchases anywhere.', 'Go to')
          + S('shipito', 'Shipito', 'Worldwide package forwarding', 'US warehouse address and package forwarding worldwide.', 'Go to'),
'c-face': C('udemy-makeup', 'Makeup courses', 'From everyday makeup to professional makeup artistry')
        + C('udemy-esthetician', 'Esthetician and skincare courses', 'Facials, skin analysis and skincare treatments')
        + C('udemy-lashes', 'Eyelash extension courses', 'Classic and volume lash techniques'),
'c-nails': C('udemy-nails', 'Nail courses', 'Nail art, gel and acrylic nails'),
'c-hair': C('udemy-hairstyling', 'Hairstyling courses', 'Updos, curls and styles for events')
        + C('udemy-haircut', 'Haircut courses', 'Cutting techniques step by step')
        + C('udemy-braiding', 'Hair braiding courses', 'Braids for every hair type')
        + C('udemy-barber', 'Barber courses', "Men's cuts, fades and beard trims"),
'c-business': C('udemy-perfume', 'Perfume-making courses', 'Create your own fragrances')
            + C('udemy-salon', 'Beauty salon business courses', 'Open and grow your own salon'),
'c-diploma': C('ioa', 'Beauty diplomas', 'Online courses for nail technicians, lash artists, makeup and more', 'International Open Academy'),
}
t = open(p(SRC, 'template.html'), encoding='utf-8').read()
FIX = {}
if os.path.exists(p(SRC, 'fix_es.json')):
    FIX['es'] = json.load(open(p(SRC, 'fix_es.json'), encoding='utf-8'))
kf = p(SRC, 'i18n', 'keys.txt')
K = open(kf, encoding='utf-8').read().splitlines() if os.path.exists(kf) else []
for fn in sorted(glob.glob(p(SRC, 'i18n', '*.txt'))):
    code = os.path.basename(fn)[:-4]
    if code == 'keys': continue
    V = open(fn, encoding='utf-8').read().splitlines()
    assert len(V) == len(K), f"{code}.txt has {len(V)} lines, keys.txt has {len(K)}"
    FIX[code] = dict(zip(K, V))
t = t.replace('@@FIX@@', json.dumps(FIX, ensure_ascii=False, separators=(',', ':')))
t = t.replace('@@LINKS@@', json.dumps(L, separators=(',', ':')))
for k, v in G.items(): t = t.replace('@@' + k + '@@', v)
assert '@@' not in t
open(p(ROOT, 'index.html'), 'w', encoding='utf-8').write(t)
print('index.html built:', ', '.join(sorted(FIX)) or 'English only')
