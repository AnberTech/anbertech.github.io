#!/usr/bin/env python3
"""AnberTech ana sitesini üretir: 33 dilde vitrin sayfası, sitemap.xml ve llms.txt.

Kullanım (depo kökünden):  python3 _src/build.py

- Sayfa metinleri: _src/i18n/<dil>.json (yalnızca dosyası olan diller üretilir; kaynak en.json)
- Uygulama sitelerinin dil listesi, rehber adresleri ve adları kardeş depolardan okunur:
  ../TurnuVolt, ../NotHesaplayici, ../Kuafix (_src/i18n/*.json). Bu depolar aynı klasörde olmalı.
  Bir dil o uygulamanın sitesinde yoksa İngilizce sayfasına bağlanılır.
- Stil ve kod: assets/style.css, assets/app.js
.nojekyll olduğu için _src de yayınlanır; içinde gizli bilgi bulunmaz.
"""
import datetime
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_src')
SIBLINGS = os.path.dirname(ROOT)
SITE = 'https://anbertech.github.io/'
ORG = SITE + '#org'
EMAIL = 'destek.anbertech@gmail.com'

# kod, yön, yerel ad, og:locale (TurnuVolt ile aynı 33 dil)
LANGS = [
    ('tr', 'ltr', 'Türkçe', 'tr_TR'), ('en', 'ltr', 'English', 'en_US'), ('ar', 'rtl', 'العربية', 'ar_AR'),
    ('cs', 'ltr', 'Čeština', 'cs_CZ'), ('da', 'ltr', 'Dansk', 'da_DK'), ('de', 'ltr', 'Deutsch', 'de_DE'),
    ('el', 'ltr', 'Ελληνικά', 'el_GR'), ('es', 'ltr', 'Español', 'es_ES'), ('es-MX', 'ltr', 'Español (México)', 'es_MX'),
    ('fa', 'rtl', 'فارسی', 'fa_IR'), ('fi', 'ltr', 'Suomi', 'fi_FI'), ('fr', 'ltr', 'Français', 'fr_FR'),
    ('he', 'rtl', 'עברית', 'he_IL'), ('hi', 'ltr', 'हिन्दी', 'hi_IN'), ('hu', 'ltr', 'Magyar', 'hu_HU'),
    ('id', 'ltr', 'Bahasa Indonesia', 'id_ID'), ('it', 'ltr', 'Italiano', 'it_IT'), ('ja', 'ltr', '日本語', 'ja_JP'),
    ('ko', 'ltr', '한국어', 'ko_KR'), ('ms', 'ltr', 'Bahasa Melayu', 'ms_MY'), ('nb', 'ltr', 'Norsk bokmål', 'nb_NO'),
    ('nl', 'ltr', 'Nederlands', 'nl_NL'), ('pl', 'ltr', 'Polski', 'pl_PL'), ('pt-BR', 'ltr', 'Português (Brasil)', 'pt_BR'),
    ('pt-PT', 'ltr', 'Português (Portugal)', 'pt_PT'), ('ro', 'ltr', 'Română', 'ro_RO'), ('ru', 'ltr', 'Русский', 'ru_RU'),
    ('sv', 'ltr', 'Svenska', 'sv_SE'), ('th', 'ltr', 'ไทย', 'th_TH'), ('uk', 'ltr', 'Українська', 'uk_UA'),
    ('vi', 'ltr', 'Tiếng Việt', 'vi_VN'), ('zh-Hans', 'ltr', '简体中文', 'zh_CN'), ('zh-Hant', 'ltr', '繁體中文', 'zh_TW'),
]
LANG = {l[0]: l for l in LANGS}
RASTER_FLAGS = {'es', 'es-mx'}
# 17 dilli sitelerde (Not Hesaplayıcı, Kuafix) bu dillerin karşılığı
NEAR = {'es-MX': 'es', 'pt-BR': 'pt', 'pt-PT': 'pt'}

APPS = {
    'kfx': {'name': 'Kuafix', 'repo': 'Kuafix', 'path': 'Kuafix/', 'icon': 'kuafix.png', 'cls': 'ico-kuafix', 'a': '#22d3ee', 'a2': '#34d399',
            'ios': 'https://apps.apple.com/app/id6746421487', 'ios_tr': 'https://apps.apple.com/tr/app/kuafix/id6746421487?l=tr',
            'play': 'https://play.google.com/store/apps/details?id=com.anbertech.kuafix', 'guides': ('book', 'fin', 'ai'),
            'category': 'BusinessApplication'},
    'tv': {'name': 'TurnuVolt', 'repo': 'TurnuVolt', 'path': 'TurnuVolt/', 'icon': 'turnuvolt.png', 'cls': 'ico-turnuvolt', 'a': '#fbbf24', 'a2': '#f59e0b',
           'ios': 'https://apps.apple.com/app/id6745177155', 'ios_tr': 'https://apps.apple.com/tr/app/turnuvolt/id6745177155?l=tr',
           'play': None, 'guides': ('fx',), 'category': 'SportsApplication'},
    'nh': {'name': 'Not Hesaplayıcı', 'repo': 'NotHesaplayici', 'path': 'NotHesaplayici/', 'icon': 'nothesaplayici.png', 'cls': 'ico-nothesaplayici',
           'a': '#60a5fa', 'a2': '#818cf8', 'ios': 'https://apps.apple.com/app/id6745179531',
           'ios_tr': 'https://apps.apple.com/tr/app/not-hesaplay%C4%B1c%C4%B1/id6745179531?l=tr',
           'play': None, 'guides': ('fin', 'avg', 'gpa'), 'category': 'EducationalApplication'},
    'nf': {'name': 'Formal Nöbet Çözücü', 'repo': 'NobetFormal', 'path': 'NobetFormal/', 'icon': 'nobetformal.png', 'cls': 'ico-nobet',
           'a': '#f472b6', 'a2': '#fb7185', 'ios': None, 'play': None, 'guides': (), 'category': 'BusinessApplication'},
}
ORDER = ('kfx', 'tv', 'nh', 'nf')
STR_KEYS = ['title', 'meta_desc', 'h1_a', 'h1_b', 'lead', 'aria_theme', 'aria_lang', 'soon', 'support', 'privacy',
            'kfx_tag', 'kfx_txt', 'kfx_plat', 'tv_tag', 'tv_txt', 'tv_plat', 'nh_tag', 'nh_txt', 'nh_plat',
            'nf_tag', 'nf_txt', 'nf_plat', 'nf_open', 'about_h2', 'about_p', 'faq_h2', 'rights']
FAQ_LEN = 5


def e(s):
    return html.escape(str(s), quote=True)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def load_json(path):
    def no_dupes(pairs):
        keys = [k for k, _ in pairs]
        dup = {k for k in keys if keys.count(k) > 1}
        if dup:
            sys.exit(f'{os.path.relpath(path, ROOT)}: aynı anahtar iki kez var: {sorted(dup)}')
        return dict(pairs)
    return json.loads(read(path), object_pairs_hook=no_dupes)


def check_lang(code, t):
    errs = [f'eksik/boş: {k}' for k in STR_KEYS if not isinstance(t.get(k), str) or not t[k].strip()]
    unknown = set(t) - set(STR_KEYS) - {'faq', '_note'}
    if unknown:
        errs.append(f'bilinmeyen anahtar: {sorted(unknown)}')
    faq = t.get('faq')
    if not (isinstance(faq, list) and len(faq) == FAQ_LEN and all(isinstance(x, list) and len(x) == 2 and all(isinstance(y, str) and y.strip() for y in x) for x in faq)):
        errs.append(f'faq: {FAQ_LEN} adet [soru, cevap] çifti olmalı')
    if '<' in json.dumps(t, ensure_ascii=False):
        errs.append('HTML olamaz')
    if errs:
        sys.exit(f'i18n/{code}.json hatalı:\n  ' + '\n  '.join(errs))


# ---------------------------------------------------------------- kardeş siteler

def sub_langs(repo):
    d = os.path.join(SIBLINGS, repo, '_src', 'i18n')
    if not os.path.isdir(d):
        sys.exit(f'{repo} deposu bulunamadı: {d}')
    return {f[:-5]: load_json(os.path.join(d, f)) for f in os.listdir(d) if f.endswith('.json') and not f.startswith('_')}


def sub_code(code, avail):
    if code in avail:
        return code
    if NEAR.get(code) in avail:
        return NEAR[code]
    return 'en'


def sub_dir(c):
    return '' if c == 'tr' else c.lower() + '/'


def app_links(key, code, S):
    """(sitedeki dil, ana sayfa, destek, gizlilik, [(rehber adı, adres)])"""
    a = APPS[key]
    base = SITE + a['path']
    if key == 'nf':
        return 'tr', base, None, None, []
    avail = S[key]
    c = sub_code(code, avail)
    t = avail[c]
    home = base + sub_dir(c)
    guides = [(t[f'{g}_name'], home + t[f'{g}_slug'] + '/') for g in a['guides']]
    return c, home, home + 'support.html', home + 'privacy.html', guides


# ---------------------------------------------------------------- sayfa

def flag(code, base):
    c = code.lower()
    return f'<img src="{base}assets/img/flags/{c}.{"png" if c in RASTER_FLAGS else "svg"}" alt="" width="20" height="14" decoding="async">'


def lang_menu(code, built, t, base):
    links = ''.join(f'<a href="{base}{sub_dir(c) or "./"}" hreflang="{c}" lang="{c}"{" aria-current=\"page\"" if c == code else ""}>'
                    f'{flag(c, base)}<span dir="{LANG[c][1]}">{e(LANG[c][2])}</span></a>' for c in built)
    return (f'<details class="lang-menu"><summary class="pill" aria-label="{e(t["aria_lang"])} / Language">{flag(code, base)}'
            f'<span>{e(code.split("-")[0].upper())}</span></summary><nav class="lm-list" aria-label="{e(t["aria_lang"])} / Language">{links}</nav></details>')


def home_url(code):
    return SITE + sub_dir(code)


def card(key, i, code, t, S, base):
    a = APPS[key]
    sc, home, sup, prv, guides = app_links(key, code, S)
    name = a['name']
    if key == 'nh':
        name = S['nh'][sc]['brand']
    stores = ''
    if key != 'nf':
        ios = a['ios_tr'] if code == 'tr' else a['ios']
        stores = (f'<a data-goatcounter-click="home-appstore-{key}-{code.lower()}" class="st" href="{e(ios)}" target="_blank" rel="noopener" aria-label="App Store">'
                  f'<svg class="ic" aria-hidden="true"><use href="#i-apple"/></svg>App Store</a>')
        if a['play']:
            play = a['play'] + ('' if code == 'tr' else f'&hl={sc}')
            stores += (f'<a data-goatcounter-click="home-googleplay-{key}-{code.lower()}" class="st" href="{e(play)}" target="_blank" rel="noopener" aria-label="Google Play">'
                       f'<svg class="ic" aria-hidden="true"><use href="#i-play"/></svg>Google Play</a>')
        else:
            stores += f'<span class="st off"><svg class="ic" aria-hidden="true"><use href="#i-play"/></svg>{e(t["soon"])}</span>'
    else:
        stores = (f'<a data-goatcounter-click="home-open-nobetformal-{code.lower()}" class="st" href="{e(home)}">'
                  f'<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg>{e(t["nf_open"])}</a>')
    gl = ''.join(f'<a href="{e(h)}">{e(n)}</a>' for n, h in guides)
    gl = f'<div class="guides">{gl}</div>' if gl else ''
    lnk = f'<span class="lnk"><a href="{e(sup)}">{e(t["support"])}</a><a href="{e(prv)}">{e(t["privacy"])}</a></span>' if sup else ''
    lang_attr = '' if sc == code or key == 'nf' else f' hreflang="{sc}"'
    return f'''<article class="card" style="--a:{a["a"]};--a2:{a["a2"]};--i:{i}">
  <a class="cover" href="{e(home)}"{lang_attr} aria-label="{e(name)}"></a>
  <div class="head"><span class="ico {a["cls"]}"><img src="{base}assets/img/{a["icon"]}" alt="" width="64" height="64"></span>
    <div class="ttl"><h2>{e(name)}</h2><p class="tag">{e(t[key + "_tag"])}</p></div><svg class="ic go" aria-hidden="true"><use href="#i-arrow"/></svg></div>
  <p class="txt">{e(t[key + "_txt"])}</p>
  {gl}<div class="stores">{stores}</div>
  <div class="foot"><span class="plat">{e(t[key + "_plat"])}</span>{lnk}</div>
</article>'''


def jsonld(code, t, S):
    graph = [{'@type': 'Organization', '@id': ORG, 'name': 'AnberTech', 'url': SITE, 'email': EMAIL,
              'logo': SITE + 'assets/img/icon-512.png', 'description': t['lead'],
              'owns': [{'@id': SITE + APPS[k]['path'] + '#app'} for k in ORDER]}]
    for k in ORDER:
        a = APPS[k]
        sc, home, *_ = app_links(k, code, S)
        name = S['nh'][sc]['brand'] if k == 'nh' else a['name']
        node = {'@type': 'WebApplication' if k == 'nf' else 'MobileApplication', '@id': SITE + a['path'] + '#app', 'name': name,
                'url': home, 'description': t[k + '_txt'], 'applicationCategory': a['category'],
                'author': {'@id': ORG}, 'publisher': {'@id': ORG}}
        if k == 'nf':
            node.update({'operatingSystem': 'Any (web browser)', 'inLanguage': 'tr', 'isAccessibleForFree': True,
                         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'TRY'}})
        else:
            node['operatingSystem'] = 'iOS, iPadOS' + (', Android' if a['play'] else '')
            node['downloadUrl'] = [x for x in (a['ios'], a['play']) if x]
        if k == 'nh':
            node['alternateName'] = 'Grade Calculator' if name != 'Grade Calculator' else 'Not Hesaplayıcı'
        graph.append(node)
    url = home_url(code)
    graph.append({'@type': 'WebSite', '@id': SITE + '#website', 'name': 'AnberTech', 'url': SITE, 'publisher': {'@id': ORG}})
    graph.append({'@type': 'FAQPage', '@id': url + '#faq', 'inLanguage': code, 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in t['faq']]})
    return ('<script type="application/ld+json">' +
            json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') +
            '</script>')


def build(code, T, built, S, symbols):
    t = T[code]
    base = '' if code == 'tr' else '../'
    url = home_url(code)
    alts = ''.join(f'<link rel="alternate" hreflang="{c}" href="{home_url(c)}">\n' for c in built)
    cards = '\n'.join(card(k, i, code, t, S, base) for i, k in enumerate(ORDER))
    faq = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in t['faq'])
    page = f'''<!doctype html>
<html lang="{code}" dir="{LANG[code][1]}" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t["title"])}</title>
<meta name="description" content="{e(t["meta_desc"])}">
<link rel="canonical" href="{url}">
{alts}<link rel="alternate" hreflang="x-default" href="{home_url("en")}">
<link rel="icon" type="image/png" href="{base}assets/img/favicon.png">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<meta property="og:title" content="{e(t["title"])}">
<meta property="og:description" content="{e(t["meta_desc"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{LANG[code][3]}">
<meta property="og:image" content="{SITE}assets/img/icon-512.png">
<meta name="theme-color" content="#08090d">
<link rel="stylesheet" href="{base}assets/style.css?v=2">
<script>try{{var s=localStorage.getItem('ab_theme');var d=s||(matchMedia('(prefers-color-scheme: light)').matches?'light':'dark');document.documentElement.setAttribute('data-theme',d)}}catch(e){{}}</script>
<script data-goatcounter="https://anbertech.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
{jsonld(code, t, S)}
</head>
<body>
{symbols}
<div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>
<div class="wrap">
<header>
<a class="brand" href="./"><img class="logo logo-d" src="{base}assets/img/logo-mark.png" alt="" width="34" height="31"><img class="logo logo-l" src="{base}assets/img/logo-mark-ink.png" alt="" width="34" height="31"><span>Anber<span style="color: #D4AF37;">Tech</span></span></a>
  <div class="tools">{lang_menu(code, built, t, base)}
  <button class="pill sq" id="theme" type="button" aria-label="{e(t["aria_theme"])}"><span class="sun">☀</span><span class="moon">☾</span></button></div>
</header>
<main>
  <section class="hero">
    <h1>{e(t["h1_a"])} <span class="grad">{e(t["h1_b"])}</span></h1>
    <p class="sub">{e(t["lead"])}</p>
  </section>
  <section class="grid">
{cards}
  </section>
  <section class="about"><h2>{e(t["about_h2"])}</h2><p>{e(t["about_p"])}</p></section>
  <section class="faq"><h2>{e(t["faq_h2"])}</h2>{faq}</section>
</main>
<footer>
  <a class="mail" href="mailto:{EMAIL}">{EMAIL}</a>
  <span>© 2026 AnberTech · {e(t["rights"])}</span>
</footer>
</div>
<script src="{base}assets/app.js?v=2"></script>
</body>
</html>
'''
    write(os.path.join(ROOT, sub_dir(code), 'index.html'), page)


def build_sitemap(built):
    today = datetime.date.today().isoformat()
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for c in built:
        out.append(f'  <url><loc>{home_url(c)}</loc><lastmod>{today}</lastmod><priority>1.0</priority>')
        out += [f'    <xhtml:link rel="alternate" hreflang="{c2}" href="{home_url(c2)}" />' for c2 in built]
        out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{home_url("en")}" />')
        out.append('  </url>')
    out.append('</urlset>')
    write(os.path.join(ROOT, 'sitemap.xml'), '\n'.join(out) + '\n')


def build_llms(S):
    _, kh, *_ , kg = app_links('kfx', 'en', S)
    _, th, *_ , tg = app_links('tv', 'en', S)
    _, nhh, *_ , ng = app_links('nh', 'en', S)
    lines = [
        '# AnberTech',
        '',
        '> AnberTech is an independent app developer from Turkey. It makes simple mobile apps and free web tools, each for one everyday job: '
        'hair salon appointments (Kuafix), tournaments and fixtures (TurnuVolt), grade and GPA calculation (Not Hesaplayıcı / Grade Calculator) '
        'and on-call rosters for doctors (Formal Nöbet Çözücü).',
        '',
        '## Apps',
        '',
        f'- [Kuafix]({SITE}Kuafix/): hair salon and barber booking app for Turkey (one app for hairdressers and customers): booking calendar, '
        'payment and income tracking, busy-hour statistics, online booking and AI hairstyle try-on. iPhone, iPad and Android. The app is in Turkish. '
        'Free to download and free for customers; hairdresser panel needs Hairdresser Premium (399 TL/month) after a 1-month free trial. '
        f'Guides: {", ".join(h for _, h in kg)}. Details: {SITE}Kuafix/llms.txt',
        f'- [TurnuVolt]({SITE}TurnuVolt/): tournament and league organizer for any game, from football to chess and esports: league and knockout fixtures, '
        'scores, standings, podium. iPhone and iPad (Android coming soon), 33 languages, one-time purchase. '
        f'Free web fixture generator: {tg[0][1]}. Details: {SITE}TurnuVolt/llms.txt',
        f'- [Not Hesaplayıcı / Grade Calculator]({SITE}NotHesaplayici/): course average, the final exam grade needed to pass, and GPA (GANO) tracking. '
        'Free, ad-free, offline, no account. iPhone and iPad (Android coming soon), 17 languages. '
        f'Free web calculators: {", ".join(h for _, h in ng)}. Details: {SITE}NotHesaplayici/llms.txt',
        f'- [Formal Nöbet Çözücü]({SITE}NobetFormal/): free in-browser tool that builds balanced monthly on-call (nöbet) schedules for hospital doctors '
        f'around overtime targets, leave and holidays. Turkish. Details: {SITE}NobetFormal/llms.txt',
        '',
        '## Contact',
        '',
        f'- {EMAIL}',
        '',
    ]
    write(os.path.join(ROOT, 'llms.txt'), '\n'.join(lines))


def main():
    T = {}
    for code, *_ in LANGS:
        p = os.path.join(SRC, 'i18n', f'{code}.json')
        if os.path.exists(p):
            T[code] = load_json(p)
            check_lang(code, T[code])
    built = [c for c, *_ in LANGS if c in T]
    if not {'tr', 'en'} <= set(built):
        sys.exit('i18n/tr.json ve i18n/en.json gerekli')
    S = {'kfx': sub_langs('Kuafix'), 'tv': sub_langs('TurnuVolt'), 'nh': sub_langs('NotHesaplayici')}
    symbols = read(os.path.join(SRC, 'symbols.svg')).strip()
    for c in built:
        build(c, T, built, S, symbols)
    build_sitemap(built)
    build_llms(S)
    print('üretildi:', ', '.join(built))


if __name__ == '__main__':
    main()
