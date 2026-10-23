#!/usr/bin/env python3
"""Bygger tidningarnas egna adresser till rutan: halkvakt.se/ruta/<tidning>/ (Axel 23/10).

NWT:s verktyg tog inte längre iframe-kod, bara en URL. Varje tidning får därför en egen
sida som är ett skal runt ruta.html med tidningens inställningar, plus oEmbed och
twitter:player så att verktyg som bygger inbäddningen ur länken får rätt storlek.

Inställningarna läses ur tidningens förslagssida (första ruta.html-iframen), så sidan och
adressen visar alltid samma ruta. Hälsinglands fyra tidningar står i EXTRA nedan.

Kör från repots rot:  python3 verktyg/rutor.py
"""
import html, json, os, re, urllib.parse

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAS = 'https://halkvakt.se/'

# Tidningar som inte har en egen förslagssida (de delar halsingland.html).
EXTRA = {
    'ht': dict(lan='gavleborg', strak='halsingland', namn='HT', lank='https://www.ht.se/', lanktext='Mer trafik på ht.se'),
    'ljusnan': dict(lan='gavleborg', strak='ljusnan', namn='Ljusnan', lank='https://www.ljusnan.se/', lanktext='Mer trafik på ljusnan.se'),
    'soderhamnskuriren': dict(lan='gavleborg', strak='soderhamn', namn='Söderhamns-Kuriren', lank='https://www.soderhamnskuriren.se/', lanktext='Mer trafik på soderhamnskuriren.se'),
    'ljusdalsposten': dict(lan='gavleborg', strak='ljusdal', namn='Ljusdals-Posten', lank='https://www.ljusdalsposten.se/', lanktext='Mer trafik på ljusdalsposten.se'),
}
HOPPA = {'halsingland'}   # sidor som täcks av EXTRA
ORDNING = ['lan', 'strak', 'tema', 'namn', 'lank', 'lanktext']

def tidningar():
    ut = {}
    for f in sorted(os.listdir(ROT)):
        if not f.endswith('.html') or f[:-5] in HOPPA: continue
        m = re.search(r'<iframe src="ruta\.html\?([^"]+)"', open(os.path.join(ROT, f), encoding='utf-8').read())
        if not m: continue
        q = dict(urllib.parse.parse_qsl(html.unescape(m.group(1))))
        ut[f[:-5]] = {k: q[k] for k in ORDNING if k in q}
    ut.update(EXTRA)
    return ut

def sida(slug, t, kort):
    q = dict(t); q.setdefault('tema', 'ljus')
    src = BAS + 'ruta.html?v=6&' + urllib.parse.urlencode([(k, q[k]) for k in ORDNING if k in q], quote_via=urllib.parse.quote, safe=':/')
    url = f'{BAS}ruta/{slug}/'
    rubrik = f'Väglaget i {kort} just nu'
    titel = f'{t["namn"]} · {rubrik}'
    e = lambda s: html.escape(s, quote=True)
    return f'''<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(titel)}</title>
<!-- Byggd av verktyg/rutor.py, ändra där. {e(t["namn"])}:s egen adress till rutan (Axel 23/10): ett skal runt ruta.html med
     tidningens inställningar, så rutan ändras på ett ställe. oEmbed och player-taggarna låter verktyg som bygger
     inbäddningen själva ur länken hitta rätt storlek. -->
<meta name="description" content="{e(rubrik)}: länet, de stora vägarna och pendlarvägarna. Live ur Trafikverkets öppna data.">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/json+oembed" href="{url}oembed.json" title="{e(titel)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Halkvakt">
<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="Länet, de stora vägarna och pendlarvägarna. Live ur Trafikverkets öppna data.">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BAS}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="player">
<meta name="twitter:title" content="{e(titel)}">
<meta name="twitter:image" content="{BAS}og.png">
<meta name="twitter:player" content="{url}">
<meta name="twitter:player:width" content="480">
<meta name="twitter:player:height" content="440">
<link rel="icon" type="image/png" href="{BAS}favicon.png">
<style>
  html, body {{ margin: 0; height: 100%; background: transparent; }}
  iframe {{ display: block; width: 100%; height: 100%; min-height: 440px; border: 0; }}
  /* Öppnas länken direkt i ett stort fönster visas rutan som i en artikel, 480 × 440. I en tidnings ram fyller den ramen. */
  @media (min-width: 560px) and (min-height: 560px) {{
    body {{ display: grid; place-items: center; }}
    iframe {{ width: 480px; height: 440px; min-height: 0; border-radius: 16px; box-shadow: 0 20px 60px rgba(8, 11, 13, .18); }}
  }}
</style>
</head>
<body>
<iframe id="ruta" src="{e(src)}" title="{e(rubrik)}" loading="eager"></iframe>
<script>
  // Tillval som går vidare till rutan: ?flik=lan|vagar|pendling, ?tema=auto|mork, ?sponsor=…, ?sponsorlank=…
  (function () {{
    var in_ = new URLSearchParams(location.search), f = document.getElementById('ruta'), u = new URL(f.src);
    ['flik', 'tema', 'sponsor', 'sponsorlank'].forEach(function (k) {{ var v = in_.get(k); if (v) u.searchParams.set(k, v); }});
    if (u.href !== f.src) f.src = u.href;
  }})();
</script>
</body>
</html>
''', json.dumps({
        'version': '1.0', 'type': 'rich', 'title': titel,
        'provider_name': 'Halkvakt', 'provider_url': BAS,
        'width': 480, 'height': 440, 'cache_age': 86400,
        'thumbnail_url': BAS + 'og.png', 'thumbnail_width': 1200, 'thumbnail_height': 630,
        'html': f'<iframe src="{url}" width="480" height="440" style="border:0;width:100%;max-width:480px" title="{e(rubrik)}" loading="lazy"></iframe>',
    }, ensure_ascii=False, indent=2) + '\n'

if __name__ == '__main__':
    kort = {l['slug']: l['kort'] for l in json.load(open(os.path.join(ROT, 'data/lan.json'), encoding='utf-8'))['lan']}
    alla = tidningar()
    for slug, t in alla.items():
        d = os.path.join(ROT, 'ruta', slug); os.makedirs(d, exist_ok=True)
        s, o = sida(slug, t, kort[t['lan']])
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(s)
        open(os.path.join(d, 'oembed.json'), 'w', encoding='utf-8').write(o)
    print(len(alla), 'rutor:', ', '.join(alla))
