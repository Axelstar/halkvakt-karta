#!/usr/bin/env python3
"""Bygger förslagssidorna till däckverkstäder: halkvakt.se/verkstad/<slug> (Axel 25/10).

Samma stil som tidningssidorna, men kortare och för en liten företagare: rutan med verkstadens namn,
en rad till bokningsbekräftelsen och rutan på sajten. Ingen annonsplats; länken i rutans fot går till
verkstadens egen bokning. Ingen affisch (Axel 25/10).

Posterna står i verktyg/verkstader.json. Kör från repots rot:  python3 verktyg/verkstadssida.py
Kör sedan verktyg/rutor.py, som gör verkstadens egen rutadress halkvakt.se/ruta/<slug>/.
"""
import json, os, re, sys, urllib.parse

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FALT = ['slug', 'namn', 'fullnamn', 'genitiv', 'lan', 'lank', 'lanktext', 'kommentar']
FORBJUDET = ['—', '!', 'lämnar aldrig telefonen']

def main():
    mall = open(os.path.join(ROT, 'verktyg/verkstadssida.mall.html'), encoding='utf-8').read()
    tm = open(os.path.join(ROT, 'verktyg/tidningssida.mall.html'), encoding='utf-8').read()
    css = tm[tm.index('<style>') + 7:tm.index('</style>')].split('\n', 2)[2]   # samma CSS som tidningssidorna, utan kommentarraden
    lanen = {l['slug']: l for l in json.load(open(os.path.join(ROT, 'data/lan.json'), encoding='utf-8'))['lan']}
    ruta = open(os.path.join(ROT, 'ruta.html'), encoding='utf-8').read()
    os.makedirs(os.path.join(ROT, 'verkstad'), exist_ok=True)
    skrivna = []
    for v in json.load(open(os.path.join(ROT, 'verktyg/verkstader.json'), encoding='utf-8')):
        saknas = [f for f in FALT if not v.get(f)]
        if saknas: sys.exit(f"{v.get('slug', '?')}: saknar {', '.join(saknas)} i verkstader.json")
        if v['lan'] not in lanen: sys.exit(f"{v['slug']}: länet '{v['lan']}' finns inte i data/lan.json")
        if not v['lank'].startswith('https://'): sys.exit(f"{v['slug']}: lank måste börja med https://")
        if len(v['lanktext']) > 40: sys.exit(f"{v['slug']}: lanktext är längre än 40 tecken, rutan klipper den")
        strak = v.get('strak', '')
        if strak and not re.search(r'\n\s*' + re.escape(strak) + r': \{ fran', ruta): sys.exit(f"{v['slug']}: stråket '{strak}' finns inte i STRAK i ruta.html")
        for f in FORBJUDET:
            if any(f in str(v[k]) for k in FALT): sys.exit(f"{v['slug']}: förbjuden formulering '{f}'")
        kort = lanen[v['lan']]['kort']
        f = {
            'css': css, 'slug': v['slug'], 'namn': v['namn'], 'fullnamn': v['fullnamn'], 'genitiv': v['genitiv'],
            'lan': v['lan'], 'lankort': kort, 'lank': v['lank'], 'lanktext': v['lanktext'], 'kommentar': v['kommentar'],
            'lank_visas': re.sub(r'^https://(www\.)?|/$', '', v['lank']),
            'namn_q': urllib.parse.quote(v['namn']), 'lanktext_q': urllib.parse.quote(v['lanktext']),
            'strak_param': '&amp;strak=' + strak if strak else '',
            'pendling_text': ' och pendlarvägarna' if strak else '',
            'langsta_ord': str(max(len(w) for w in 'Nya däck, och väglaget på vägen hem'.split())),
        }
        ut = mall
        for k, val in f.items(): ut = ut.replace('{{' + k + '}}', val)
        kvar = re.findall(r'\{\{[a-z_]+\}\}', ut)
        if kvar: sys.exit(f"{v['slug']}: fält kvar i mallen: {', '.join(sorted(set(kvar)))}")
        open(os.path.join(ROT, 'verkstad', v['slug'] + '.html'), 'w', encoding='utf-8').write(ut)
        skrivna.append(v['slug'])
    print(f"{len(skrivna)} verkstäder skrivna: {', '.join(skrivna)}")

if __name__ == '__main__':
    main()
