#!/usr/bin/env python3
"""AnberTech ana sitesini üretir: 33 dilde vitrin sayfası, sitemap.xml ve llms.txt.

Kullanım (depo kökünden):  python3 _src/build.py

- Sayfa metinleri: _src/i18n/<dil>.json (yalnızca dosyası olan diller üretilir; kaynak en.json)
- Uygulama sitelerinin dil listesi, rehber adresleri ve adları kardeş depolardan okunur:
  ../TurnuVolt, ../NotHesaplayici, ../Kuafix, ../PinkOrBlue, ../WeddingInvite (_src/i18n/*.json). Bu depolar aynı klasörde olmalı.
  Bir dil o uygulamanın sitesinde yoksa en yakın akraba dile (NEAR), o da yoksa İngilizce sayfasına bağlanılır.
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
# Sitesinde olmayan dil için en yakın akraba dil (o da yoksa en)
NEAR = {'es-MX': 'es', 'pt-BR': 'pt', 'pt-PT': 'pt', 'zh-Hant': 'zh-Hans'}

APPS = {
    'kfx': {'name': 'Kuafix', 'repo': 'Kuafix', 'path': 'Kuafix/', 'icon': 'kuafix.png', 'cls': 'ico-kuafix', 'a': '#22d3ee', 'a2': '#34d399',
            'ios': 'https://apps.apple.com/app/id6746421487', 'ios_tr': 'https://apps.apple.com/tr/app/kuafix/id6746421487?l=tr',
            'play': 'https://play.google.com/store/apps/details?id=com.anbertech.kuafix', 'guides': ('book', 'fin', 'ai'),
            'category': 'BusinessApplication'},
    'tv': {'name': 'TurnuVolt', 'repo': 'TurnuVolt', 'path': 'TurnuVolt/', 'icon': 'turnuvolt.png', 'cls': 'ico-turnuvolt', 'a': '#fbbf24', 'a2': '#f59e0b',
           'ios': 'https://apps.apple.com/app/id6745177155', 'ios_tr': 'https://apps.apple.com/tr/app/turnuvolt/id6745177155?l=tr',
           'play': 'https://play.google.com/store/apps/details?id=com.anbertech.turnuvolt', 'guides': ('fx', 'table', 'bracket'), 'category': 'SportsApplication'},
    'nh': {'name': 'Not Hesaplayıcı', 'repo': 'NotHesaplayici', 'path': 'NotHesaplayici/', 'icon': 'nothesaplayici.png', 'cls': 'ico-nothesaplayici',
           'a': '#60a5fa', 'a2': '#818cf8', 'ios': 'https://apps.apple.com/app/id6745179531',
           'ios_tr': 'https://apps.apple.com/tr/app/not-hesaplay%C4%B1c%C4%B1/id6745179531?l=tr',
           'play': 'https://play.google.com/store/apps/details?id=com.anbertech.nothesaplayici', 'guides': ('fin', 'avg', 'gpa'), 'category': 'EducationalApplication'},
    'nf': {'name': 'Formal Nöbet Çözücü', 'repo': 'NobetFormal', 'path': 'NobetFormal/', 'icon': 'nobetformal.png', 'cls': 'ico-nobet',
           'a': '#f472b6', 'a2': '#fb7185', 'ios': None, 'play': None, 'guides': ('liste', 'adil'), 'category': 'BusinessApplication'},
    'pob': {'name': 'PinkOrBlue', 'repo': 'PinkOrBlue', 'path': 'PinkOrBlue/', 'icon': 'pinkorblue.png', 'cls': 'ico-pob',
            'a': '#FF8FB8', 'a2': '#7EC8FF', 'ios': None, 'play': None, 'guides': ('party', 'vote', 'far'), 'category': 'LifestyleApplication', 'web': True},
    'is': {'name': 'WeddingInvite', 'repo': 'WeddingInvite', 'path': 'WeddingInvite/', 'icon': 'weddinginvite.png', 'cls': 'ico-is',
           'a': '#b9a77a', 'a2': '#a8a9ad', 'ios': None, 'play': None, 'guides': ('make', 'engage', 'rsvp'), 'category': 'LifestyleApplication'},
    # Sence: henüz yayında değil ('soon'). Kart yalnız TR/EN sitesine gider, iki mağaza da "Yakında" (ana sitenin "soon" metni);
    # 33 dile ayrı metin yok: kartın tek satırı Sence sitesinin kendi dilinden (TR, diğer bütün diller EN). JSON-LD'ye girmez.
    'sc': {'name': 'Sence', 'repo': 'Sence', 'path': 'Sence/', 'icon': 'sence.png', 'cls': 'ico-sence', 'a': '#22d3ee', 'a2': '#a78bfa',
           'ios': None, 'play': None, 'guides': (), 'category': 'SocialNetworkingApplication', 'soon': True,
           'tag': {'tr': 'Kararsız mısın? Herkes oylasın', 'en': 'Ask it. The crowd votes.'}},
}
ORDER = ('kfx', 'pob', 'tv', 'nh', 'is', 'nf', 'sc')
# Tek dilli (Türkçe) web sayfaları: kart doğrudan sayfayı açar, destek/gizlilik bağlantısı yok
TR_ONLY = ('nf',)
# PinkOrBlue bu dillerde gösterilmez (doğum öncesi cinsiyet açıklaması Hindistan ve Çin'de yasal olarak kısıtlı)
HIDE = {'pob': {'hi', 'zh-Hans', 'zh-Hant'}}
POB_DOCS = {'tr': ('destek/', 'gizlilik/')}
STR_KEYS = ['title', 'meta_desc', 'h1_a', 'h1_b', 'lead', 'aria_theme', 'aria_lang', 'soon', 'support', 'privacy',
            'kfx_tag', 'kfx_txt', 'kfx_plat', 'tv_tag', 'tv_txt', 'tv_plat', 'nh_tag', 'nh_txt', 'nh_plat',
            'nf_tag', 'nf_txt', 'nf_plat', 'nf_open', 'nf_g_liste', 'nf_g_adil', 'pob_tag', 'pob_txt', 'pob_plat', 'pob_open', 'is_tag', 'is_txt', 'is_plat', 'is_open', 'about_h2', 'about_p', 'faq_h2', 'rights']
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


def sub_guides(repo):
    """Rehber metinleri ayrı dosyada tutan siteler (WeddingInvite, NobetFormal): _src/guides/<dil>.json; yoksa boş"""
    d = os.path.join(SIBLINGS, repo, '_src', 'guides')
    if not os.path.isdir(d):
        return {}
    return {f[:-5]: load_json(os.path.join(d, f)) for f in os.listdir(d) if f.endswith('.json') and not f.startswith('_')}


def sub_code(code, avail):
    if code in avail:
        return code
    if NEAR.get(code) in avail:
        return NEAR[code]
    return 'en'


def sub_dir(c):
    return '' if c == 'tr' else c.lower() + '/'


def app_links(key, code, S, t=None):
    """(sitedeki dil, ana sayfa, destek, gizlilik, [(rehber adı, adres)]). t: ana sitenin o dildeki metinleri (Nöbet kapsül adları için)"""
    a = APPS[key]
    base = SITE + a['path']
    if a.get('soon'):   # yayında olmayan uygulama (Sence): yalnız TR ve EN sitesi var
        c = 'tr' if code == 'tr' else 'en'
        return c, base + sub_dir(c), None, None, []
    if key in TR_ONLY:   # yalnız Türkçe site: kapsül yazısı ana sayfanın dilinde, adres Türkçe rehber
        G = S.get('nf_g', {}).get('tr')
        guides = [((t or {}).get(f'nf_g_{x}') or G[f'{x}_name'], base + G[f'{x}_slug'] + '/') for x in a['guides']] if G else []
        return 'tr', base, None, None, guides
    avail = S[key]
    if key == 'pob':   # web uygulaması: dil klasörü + oda kurma sayfası; destek/gizlilik klasör adresli
        c = sub_code(code, avail)
        home = base + sub_dir(c)
        sup, prv = POB_DOCS.get(c, ('support/', 'privacy/'))
        G = S.get('pob_g', {}).get(c)   # rehberler _src/guides/<dil>.json
        return c, home, home + sup, home + prv, [(G[f'{g}_name'], home + G[f'{g}_slug'] + '/') for g in a['guides']] if G else []
    c = sub_code(code, avail)
    t = avail[c]
    home = base + sub_dir(c)
    if key == 'is':   # web davetiyesi: destek/gizlilik sayfası yok; rehberler _src/guides/<dil>.json
        G = S.get('is_g', {}).get(c)
        return c, home, None, None, [(G[f'{g}_name'], home + G[f'{g}_slug'] + '/') for g in a['guides']] if G else []
    G = S.get(key + '_g', {}).get(c, {})   # ek rehberler _src/guides/<dil>.json (TurnuVolt); fikstür aracı gibi araçlar i18n'de
    guides = [(src[f'{g}_name'], home + src[f'{g}_slug'] + '/') for g in a['guides'] for src in [t if f'{g}_slug' in t else G] if f'{g}_slug' in src]
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
    sc, home, sup, prv, guides = app_links(key, code, S, t)
    name = a['name']
    if key == 'nh':
        name = S['nh'][sc]['brand']
    stores = ''
    hl = '' if sc == code else f' hreflang="{sc}"'
    if a.get('soon'):   # iki mağaza da "Yakında", bağlantısız
        stores = (f'<span class="st off"><svg class="ic" aria-hidden="true"><use href="#i-apple"/></svg>{e(t["soon"])}</span>'
                  f'<span class="st off"><svg class="ic" aria-hidden="true"><use href="#i-play"/></svg>{e(t["soon"])}</span>')
    elif a['ios']:
        ios = a['ios_tr'] if code == 'tr' else a['ios']
        stores = (f'<a data-goatcounter-click="hub/{code.lower()}/appstore-{key}" class="st" href="{e(ios)}" target="_blank" rel="noopener" aria-label="App Store">'
                  f'<svg class="ic" aria-hidden="true"><use href="#i-apple"/></svg>App Store</a>')
        if a['play']:
            play = a['play'] + ('' if code == 'tr' else f'&hl={sc}')
            stores += (f'<a data-goatcounter-click="hub/{code.lower()}/googleplay-{key}" class="st" href="{e(play)}" target="_blank" rel="noopener" aria-label="Google Play">'
                       f'<svg class="ic" aria-hidden="true"><use href="#i-play"/></svg>Google Play</a>')
        else:
            stores += f'<span class="st off"><svg class="ic" aria-hidden="true"><use href="#i-play"/></svg>{e(t["soon"])}</span>'
    else:   # web sitesi: "aç" düğmesi (PinkOrBlue'da parti odası sayfası), kapsüller ayrıca görünür
        target = home + S['pob'][sc]['fx_slug'] + '/' if key == 'pob' else home
        stores = (f'<a data-goatcounter-click="hub/{code.lower()}/open-{key}" class="st" href="{e(target)}"{hl}>'
                  f'<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg>{e(t[key + "_open"])}</a>')
    gl = ''.join(f'<a data-goatcounter-click="hub/{code.lower()}/guide-{key}" href="{e(h)}"{hl}>{e(n)}</a>' for n, h in guides)
    gl = f'<div class="guides">{gl}</div>' if gl else ''
    # Sade kart: ikon, ad, tek satır, rehber kapsülleri, mağaza/aç düğmesi. Uzun açıklama (*_txt) yalnız JSON-LD'de,
    # platform/fiyat (*_plat) ve destek/gizlilik bağlantıları uygulamanın kendi sitesinde.
    return f'''<article class="card" style="--a:{a["a"]};--a2:{a["a2"]};--i:{i}">
  <a class="cover" href="{e(home)}"{hl} aria-label="{e(name)}"></a>
  <div class="head"><span class="ico {a["cls"]}"><img src="{base}assets/img/{a["icon"]}" alt="" width="64" height="64"></span>
    <div class="ttl"><h2>{e(name)}</h2><p class="tag"{"" if sc == code or "tag" not in a else f' lang="{sc}"'}>{e(a["tag"][sc] if "tag" in a else t[key + "_tag"])}</p></div><svg class="ic go" aria-hidden="true"><use href="#i-arrow"/></svg></div>
  {gl}<div class="stores">{stores}</div>
</article>'''


def jsonld(code, t, S):
    graph = [{'@type': 'Organization', '@id': ORG, 'name': 'AnberTech', 'url': SITE, 'email': EMAIL,
              'logo': SITE + 'assets/img/icon-512.png', 'description': t['lead'],
              'owns': [{'@id': SITE + APPS[k]['path'] + '#app'} for k in ORDER if code not in HIDE.get(k, ()) and not APPS[k].get('soon')]}]
    for k in ORDER:
        if code in HIDE.get(k, ()) or APPS[k].get('soon'):
            continue
        a = APPS[k]
        sc, home, *_ = app_links(k, code, S)
        name = S['nh'][sc]['brand'] if k == 'nh' else a['name']
        node = {'@type': 'WebApplication' if not a['ios'] else 'MobileApplication', '@id': SITE + a['path'] + '#app', 'name': name,
                'url': home, 'description': t[k + '_txt'], 'applicationCategory': a['category'],
                'author': {'@id': ORG}, 'publisher': {'@id': ORG}}
        if k in TR_ONLY:
            node.update({'operatingSystem': 'Any (web browser)', 'inLanguage': 'tr', 'isAccessibleForFree': True,
                         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'TRY'}})
        elif not a['ios']:
            node.update({'operatingSystem': 'Any (web browser)', 'inLanguage': sorted(S[k]), 'isAccessibleForFree': True,
                         'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}})
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
    shown = [k for k in ORDER if code not in HIDE.get(k, ())]
    cards = '\n'.join(card(k, i, code, t, S, base) for i, k in enumerate(shown))
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
<link rel="stylesheet" href="{base}assets/style.css?v=5">
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
        'on-call rosters for doctors (Formal Nöbet Çözücü), live online gender reveal parties (PinkOrBlue) and online wedding invitations (WeddingInvite).',
        '',
        '## Apps',
        '',
        f'- [Kuafix]({SITE}Kuafix/): hair salon and barber booking app for Turkey (one app for hairdressers and customers): booking calendar, '
        'payment and income tracking, busy-hour statistics, online booking and AI hairstyle try-on. iPhone, iPad and Android. The app is in Turkish. '
        'Free to download and free for customers; hairdresser panel needs Hairdresser Premium (399 TL/month) after a 1-month free trial. '
        f'Guides: {", ".join(h for _, h in kg)}. Details: {SITE}Kuafix/llms.txt',
        f'- [TurnuVolt]({SITE}TurnuVolt/): tournament and league organizer for any game, from football to chess and esports: league and knockout fixtures, '
        'scores, standings, podium. iPhone, iPad and Android, 33 languages, one-time purchase. '
        f'Free web fixture generator: {tg[0][1]}. Details: {SITE}TurnuVolt/llms.txt',
        f'- [Not Hesaplayıcı / Grade Calculator]({SITE}NotHesaplayici/): course average, the final exam grade needed to pass, and GPA (GANO) tracking. '
        'Free, ad-free, offline, no account. iPhone, iPad and Android, 17 languages. '
        f'Free web calculators: {", ".join(h for _, h in ng)}. Details: {SITE}NotHesaplayici/llms.txt',
        f'- [Formal Nöbet Çözücü]({SITE}NobetFormal/): free in-browser tool that builds balanced monthly on-call (nöbet) schedules for hospital doctors '
        f'around overtime targets, leave and holidays. Turkish. Details: {SITE}NobetFormal/llms.txt',
        '',
        f'- [PinkOrBlue]({SITE}PinkOrBlue/): free online gender reveal party in the browser. Parents share one link; family and friends (around 30 people) '
        'vote boy or girl, add guesses, inflate one balloon together by tapping and see the result on every screen in the same second; message wall, '
        'mini game and Instagram story card. No app or account, room data deleted 7 days after the party, 15 languages. '
        f'Create a room: {SITE}PinkOrBlue/en/virtual-gender-reveal/ (Turkish: {SITE}PinkOrBlue/cinsiyet-partisi/). Details: {SITE}PinkOrBlue/llms.txt',
        f'- [WeddingInvite]({SITE}WeddingInvite/): online wedding and engagement invitation in the browser: opening animation, '
        'music, countdown, directions, weather, add-to-calendar and RSVP in one link. No app or account. '
        f'Live demo in {len(S["is"])} languages (Elif & Ege, sample data); English: {SITE}WeddingInvite/en/. Details: {SITE}WeddingInvite/llms.txt',
        f'- [Sence]({SITE}Sence/en/): coming soon to the App Store and Google Play. Ask a question under a nickname and the crowd votes: '
        'Yes/No, Pick (2–4 options) or Rate (0–10); votes stay private, only the numbers are shown. Turkish and English, 18+. '
        f'Details: {SITE}Sence/llms.txt',
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
    S = {'kfx': sub_langs('Kuafix'), 'tv': sub_langs('TurnuVolt'), 'nh': sub_langs('NotHesaplayici'), 'pob': sub_langs('PinkOrBlue'),
         'is': sub_langs('WeddingInvite'), 'is_g': sub_guides('WeddingInvite'), 'nf_g': sub_guides('NobetFormal'), 'pob_g': sub_guides('PinkOrBlue'), 'tv_g': sub_guides('TurnuVolt')}
    symbols = read(os.path.join(SRC, 'symbols.svg')).strip()
    for c in built:
        build(c, T, built, S, symbols)
    build_sitemap(built)
    build_llms(S)
    print('üretildi:', ', '.join(built))


if __name__ == '__main__':
    main()
