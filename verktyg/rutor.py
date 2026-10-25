#!/usr/bin/env python3
"""Bygger tidningarnas egna adresser till rutan: halkvakt.se/ruta/<tidning>/ (Axel 23/10).

NWT:s verktyg tog inte längre iframe-kod, bara en URL. Varje tidning får därför en egen
sida som är ett skal runt ruta.html med tidningens inställningar, plus oEmbed och
twitter:player så att verktyg som bygger inbäddningen ur länken får rätt storlek.

Inställningarna läses ur tidningens förslagssida (första ruta.html-iframen), så sidan och
adressen visar alltid samma ruta. Hälsinglands fyra tidningar står i EXTRA nedan.

En förslagssida som bäddar in widget.html i stället (M Sverige, m.html, Bengt 23/10: hela landet,
utan län) får ett skal runt widget.html, 480 × 320 (Axel 23/10: "skapa en länk som här").

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
# Rutan eller widgeten: sidan som skalet bäddar in, dess version, höjd, tillval som går vidare och beskrivning.
SORT = {
    'ruta': dict(sida='ruta.html', v='6', hojd=440, tillval=['flik', 'tema', 'sponsor', 'sponsorlank'],
                 tillvaltext='?flik=lan|vagar|pendling, ?tema=auto|mork, ?sponsor=…, ?sponsorlank=…',
                 vad='länet, de stora vägarna och pendlarvägarna'),
    'widget': dict(sida='widget.html', v='3', hojd=320, tillval=['tema'], tillvaltext='?tema=auto|mork',
                   vad='halka, vägväderstationer under noll och den kallaste vägbanan'),
}

def tidningar():
    ut = {}
    # Tidningarnas förslagssidor ligger i roten, verkstädernas i verkstad/ (Axel 25/10).
    filer = [f for f in sorted(os.listdir(ROT))] + ['verkstad/' + f for f in sorted(os.listdir(os.path.join(ROT, 'verkstad')))] if os.path.isdir(os.path.join(ROT, 'verkstad')) else sorted(os.listdir(ROT))
    for f in filer:
        if not f.endswith('.html') or f[:-5] in HOPPA: continue
        m = re.search(r'<iframe src="/?(ruta|widget)\.html\?([^"]+)"', open(os.path.join(ROT, f), encoding='utf-8').read())
        if not m: continue
        q = dict(urllib.parse.parse_qsl(html.unescape(m.group(2))))
        if m.group(1) == 'widget' and 'namn' not in q: continue   # pressidans exempel på widgeten, ingen förslagssida
        slug = os.path.basename(f)[:-5]
        ut[slug] = {k: q[k] for k in ORDNING if k in q}
        if m.group(1) == 'widget': ut[slug]['sort'] = 'widget'
    ut.update(EXTRA)
    return ut

def sida(slug, t, kort):
    s = SORT[t.get('sort', 'ruta')]
    q = dict(t); q.setdefault('tema', 'ljus')
    src = BAS + s['sida'] + '?v=' + s['v'] + '&' + urllib.parse.urlencode([(k, q[k]) for k in ORDNING if k in q], quote_via=urllib.parse.quote, safe=':/')
    url = f'{BAS}ruta/{slug}/'
    rubrik = f'Väglaget i {kort} just nu'
    titel = f'{t["namn"]} · {rubrik}'
    e = lambda s: html.escape(s, quote=True)
    h, vad, Vad = s['hojd'], s['vad'], s['vad'][0].upper() + s['vad'][1:]
    tillval = '[' + ', '.join(f"'{k}'" for k in s['tillval']) + ']'
    return f'''<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(titel)}</title>
<!-- Byggd av verktyg/rutor.py, ändra där. {e(t["namn"])}:s egen adress till rutan (Axel 23/10): ett skal runt {s['sida']} med
     tidningens inställningar, så rutan ändras på ett ställe. oEmbed och player-taggarna låter verktyg som bygger
     inbäddningen själva ur länken hitta rätt storlek. -->
<meta name="description" content="{e(rubrik)}: {vad}. Live ur Trafikverkets öppna data.">
<link rel="canonical" href="{url}">
<link rel="alternate" type="application/json+oembed" href="{url}oembed.json" title="{e(titel)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Halkvakt">
<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{Vad}. Live ur Trafikverkets öppna data.">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BAS}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="player">
<meta name="twitter:title" content="{e(titel)}">
<meta name="twitter:image" content="{BAS}og.png">
<meta name="twitter:player" content="{url}">
<meta name="twitter:player:width" content="480">
<meta name="twitter:player:height" content="{h}">
<link rel="icon" type="image/png" href="{BAS}favicon.png">
<style>
  html, body {{ margin: 0; height: 100%; background: transparent; }}
  iframe {{ display: block; width: 100%; height: 100%; min-height: {h}px; border: 0; }}
  /* Öppnas länken direkt i ett stort fönster visas rutan som i en artikel, 480 × {h}. I en tidnings ram fyller den ramen. */
  @media (min-width: 560px) and (min-height: 560px) {{
    body {{ display: grid; place-items: center; }}
    iframe {{ width: 480px; height: {h}px; min-height: 0; border-radius: 16px; box-shadow: 0 20px 60px rgba(8, 11, 13, .18); }}
  }}
</style>
</head>
<body>
<iframe id="ruta" src="{e(src)}" title="{e(rubrik)}" loading="eager"></iframe>
<script>
  // Tillval som går vidare till rutan: {s['tillvaltext']}
  (function () {{
    var in_ = new URLSearchParams(location.search), f = document.getElementById('ruta'), u = new URL(f.src);
    {tillval}.forEach(function (k) {{ var v = in_.get(k); if (v) u.searchParams.set(k, v); }});
    if (u.href !== f.src) f.src = u.href;
  }})();
</script>
<script src="/assets/ruta-besok.js" data-sida="/ruta/{slug}/"></script>
</body>
</html>
''', json.dumps({
        'version': '1.0', 'type': 'rich', 'title': titel,
        'provider_name': 'Halkvakt', 'provider_url': BAS,
        'width': 480, 'height': h, 'cache_age': 86400,
        'thumbnail_url': BAS + 'og.png', 'thumbnail_width': 1200, 'thumbnail_height': 630,
        'html': f'<iframe src="{url}" width="480" height="{h}" style="border:0;width:100%;max-width:480px" title="{e(rubrik)}" loading="lazy"></iframe>',
    }, ensure_ascii=False, indent=2) + '\n'

if __name__ == '__main__':
    kort = {l['slug']: l['kort'] for l in json.load(open(os.path.join(ROT, 'data/lan.json'), encoding='utf-8'))['lan']}
    alla = tidningar()
    for slug, t in alla.items():
        d = os.path.join(ROT, 'ruta', slug); os.makedirs(d, exist_ok=True)
        s, o = sida(slug, t, kort[t['lan']] if 'lan' in t else 'Sverige')
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(s)
        open(os.path.join(d, 'oembed.json'), 'w', encoding='utf-8').write(o)
    print(len(alla), 'rutor:', ', '.join(alla))
