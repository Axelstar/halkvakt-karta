#!/usr/bin/env python3
"""Bygger förslagssidorna till tidningarna: halkvakt.se/<slug> (till exempel halkvakt.se/st).

Varje tidning är en post i verktyg/tidningar.json. Sidan fylls i ur mallen verktyg/tidningssida.mall.html,
som är st.html med fälten utbytta. Siffror och vägar läses ur datan, inte ur minnet:
  - länets namn och antal vägavsnitt ur data/lan.json
  - de stora vägarna (E-vägar och vägnummer under 100) och antalet sträckor ur data/strackor.json
  - pendlarstråken (orten och målen) ur STRAK i ruta.html, samma som rutan själv visar

Kör från repots rot:
  python3 verktyg/tidningssida.py            bygger alla tidningar i tidningar.json
  python3 verktyg/tidningssida.py st norran  bygger bara de nämnda
  python3 verktyg/tidningssida.py --kontroll  skriver inget, säger vad som skulle ändras och fäller på fel

Efteråt: python3 verktyg/rutor.py (tidningens egen adress halkvakt.se/ruta/<slug>/).
Ändra i mallen eller här, aldrig direkt i en genererad sida; nästa körning skriver över den.
"""
import html, json, os, re, sys, urllib.parse

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERKTYG = os.path.join(ROT, 'verktyg')
TAL = {2: 'Två', 3: 'Tre', 4: 'Fyra', 5: 'Fem', 6: 'Sex', 7: 'Sju', 8: 'Åtta'}
FALT = ['slug', 'fullnamn', 'namn', 'genitiv', 'doman', 'lank', 'lan', 'strak', 'lasarort', 'exempel_stracka', 'montage', 'kommentar']
FORBJUDET = ['—', 'lämnar aldrig telefonen', 'Positionen lämnar aldrig']


def las(p):
    return open(os.path.join(ROT, p), encoding='utf-8').read()


def lista(ord_):
    ord_ = list(ord_)
    return ord_[0] if len(ord_) == 1 else ', '.join(ord_[:-1]) + ' och ' + ord_[-1]


def strak_ur_rutan():
    """Pendlarstråken ur ruta.html: {nyckel: {'lan':…, 'fran':…, 'till':[…]}}."""
    s = las('ruta.html')
    a = s.index('var STRAK = {')
    b = s.index('\n  };', a)
    ut = {}
    for m in re.finditer(r"\n    ([a-z0-9_]+): \{([^\n]*)\n(.*?)\n    \] \}", s[a:b], re.S):
        huvud, kropp = m.group(2), m.group(3)
        lan = re.search(r"lan: '([^']+)'", huvud)
        fran = re.search(r"fran: '([^']+)'", huvud)
        ut[m.group(1)] = {
            'lan': lan.group(1) if lan else m.group(1),
            'fran': fran.group(1) if fran else None,
            'till': re.findall(r"\{ (?:fran: '[^']+', )?till: '([^']+)'", kropp),
            'delar': re.findall(r"\['([^']+)', '([^']+)'\]", kropp),
        }
    return ut


def vagnummer(v):
    v = v.replace('Väg ', '').replace('E ', 'E')
    return v


def stora_vagar(lan_slug):
    lan = next(l for l in json.loads(las('data/strackor.json'))['lan'] if l['slug'] == lan_slug)
    vagar = []
    for v in lan['vagar']:
        n = vagnummer(v['vag'])
        if n.startswith('E') or (n.isdigit() and int(n) < 100):
            vagar.append((n, len(v['strackor'])))
    return vagar


def fyll(t, mall, lanen, straken):
    # strak och lasarort får vara tomma: då får sidan ingen pendlingsflik (som Jämtlands Tidning).
    fel = [k for k in FALT if not t.get(k) and k not in ('strak', 'lasarort')]
    if fel:
        raise SystemExit(f"{t.get('slug', '?')}: saknar {', '.join(fel)} i tidningar.json")
    if t['lan'] not in lanen:
        raise SystemExit(f"{t['slug']}: länet '{t['lan']}' finns inte i data/lan.json")
    st = None
    if t.get('strak'):
        st = straken.get(t['strak'])
        if not st:
            raise SystemExit(f"{t['slug']}: stråket '{t['strak']}' finns inte i STRAK i ruta.html. Lägg till det först.")
        if st['lan'] != t['lan']:
            raise SystemExit(f"{t['slug']}: stråket '{t['strak']}' hör till {st['lan']}, inte {t['lan']}")
        if not st['fran']:
            raise SystemExit(f"{t['slug']}: stråket '{t['strak']}' har ingen gemensam utgångsort (fran) och passar inte mallen")
        finns = {(v['vag'], x['plats']) for l in json.loads(las('data/strackor.json'))['lan'] if l['slug'] == t['lan']
                 for v in l['vagar'] for x in v['strackor']}
        saknas = [f"{v} '{p}'" for v, p in st['delar'] if (v, p) not in finns]
        if saknas:
            raise SystemExit(f"{t['slug']}: stråket '{t['strak']}' i ruta.html har delar som inte finns i data/strackor.json "
                             f"för {t['lan']} (namnen måste stå exakt som där): {'; '.join(saknas)}")
        if not t.get('lasarort'):
            raise SystemExit(f"{t['slug']}: lasarort saknas (en ort läsarna pendlar till, helst ett av stråkens mål)")
        if not any(t['lasarort'] in m for m in st['till']):
            print(f"  obs {t['slug']}: lasarort '{t['lasarort']}' är inget av stråkens mål ({', '.join(st['till'])}). Kontrollera att den ligger på ett av dem.")
    vagar = stora_vagar(t['lan'])
    e_vagar = [n for n, _ in vagar if n.startswith('E')]
    v = {
        'slug': t['slug'], 'fullnamn': t['fullnamn'], 'namn': t['namn'], 'genitiv': t['genitiv'],
        'doman': t['doman'], 'lank': t['lank'], 'lan': t['lan'],
        'exempel_stracka': t['exempel_stracka'], 'kommentar': t['kommentar'],
        'lankort': lanen[t['lan']]['kort'],
        'vagavsnitt': str(lanen[t['lan']]['vagavsnitt']),
        'vagar_rubrik': (lista(e_vagar) if len(e_vagar) < 3 else ', '.join(e_vagar[:-1]) + ' och ' + e_vagar[-1]) + ' och riksvägarna',
        'antal_strackor': str(sum(n for _, n in vagar)),
        'vagar_lista': lista(n for n, _ in vagar),
        'namn_q': t['namn'].replace(' ', '%20'),
        'lanktext_q': urllib.parse.quote('Mer trafik på ' + t['doman']),
    }
    if st:
        v.update({
            'ort': st['fran'],
            'strak_param': '&amp;strak=' + t['strak'],
            'lead_vagar': f"i {v['lankort']}, på de stora vägarna och på pendlarvägarna från {st['fran']}",
            'lasarfraga': 'till ' + t['lasarort'],
            'antal_vyer': 'Tre',
            'pendling_kort': (f'<div class="kort"><small>Pendling</small><h3>Från {st["fran"]}</h3><p>'
                              f'{TAL.get(len(st["till"]), str(len(st["till"])))} stråk som läsarna kör varje dag: till '
                              f'{lista(st["till"])}. Rutan visar vilken del som har halka.</p></div>'),
            'pendling_rad': '<tr><td><code>&amp;flik=pendling</code></td><td>Öppnar på pendlarvägarna</td></tr>',
        })
    else:
        v.update({'ort': '', 'strak_param': '', 'lead_vagar': f"i {v['lankort']} och på länets stora vägar",
                  'lasarfraga': 'på vägen', 'antal_vyer': 'Två', 'pendling_kort': '', 'pendling_rad': ''})
    v['montage'] = montage(t, v)
    ut = mall
    for k, val in v.items():
        ut = ut.replace('{{' + k + '}}', val)
    kvar = re.findall(r'\{\{[a-z_]+\}\}', ut)
    if kvar:
        raise SystemExit(f"{t['slug']}: tomma fält kvar i mallen: {kvar}")
    for f in FORBJUDET:
        if f in ut:
            raise SystemExit(f"{t['slug']}: förbjuden formulering på sidan: {f!r}")
    return ut


def montage(t, v):
    if t['montage'] == 'inget':
        return ''
    bild = f"press/{t['slug']}-artikel.jpg"
    if not os.path.exists(os.path.join(ROT, bild)):
        raise SystemExit(f"{t['slug']}: {bild} saknas. Gör montaget först (verktyg/montage.py) eller sätt montage till \"inget\".")
    if t['montage'] == 'egen':
        alt = (f"Bildmontage: en artikel på {t['doman']}, Halt på vägarna runt {v['ort'] or v['lankort']} i morse, med {t['genitiv']} "
               "väglagsruta efter ingressen. På datorn visar rutan fliken Vägarna, på mobilen fliken Pendling.")
        not_ = ('Bildmontage med exempelsiffror: så kan rutan se ut i en artikel hos er, på dator och mobil. '
                'Tryck på bilden för full storlek. Rutan överst på sidan är live.')
    elif t['montage'] == 'neutral':
        alt = f"Bildmontage: en exempelartikel om halka med {t['genitiv']} väglagsruta efter ingressen, på dator och mobil."
        not_ = ('Bildmontage med exempelsiffror: så kan rutan se ut i en artikel, på dator och mobil. '
                'Artikelsidan är en neutral skiss, inte er sajt. Tryck på bilden för full storlek. Rutan överst på sidan är live.')
    else:
        raise SystemExit(f"{t['slug']}: montage ska vara egen, neutral eller inget, inte {t['montage']!r}")
    return f'''<section>
  <div class="wrap stack" style="gap:28px">
    <div class="stack">
      <p class="etikett">I en artikel</p>
      <h2>Så kan det se ut en morgon med halka</h2>
    </div>
    <figure class="montage">
      <a href="{bild}?v=1" target="_blank" rel="noopener"><img src="{bild}?v=1" width="2400" height="1638" alt="{html.escape(alt, quote=True)}" loading="lazy"></a>
    </figure>
    <p class="not">{not_}</p>
  </div>
</section>

'''


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    kontroll = '--kontroll' in sys.argv
    mall = open(os.path.join(VERKTYG, 'tidningssida.mall.html'), encoding='utf-8').read()
    lanen = {l['slug']: l for l in json.loads(las('data/lan.json'))['lan']}
    straken = strak_ur_rutan()
    alla = json.load(open(os.path.join(VERKTYG, 'tidningar.json'), encoding='utf-8'))['tidningar']
    slugs = [t['slug'] for t in alla]
    dubbla = {s for s in slugs if slugs.count(s) > 1}
    if dubbla:
        raise SystemExit('Samma slug två gånger i tidningar.json: ' + ', '.join(dubbla))
    valda = [t for t in alla if not args or t['slug'] in args]
    okanda = set(args) - set(slugs)
    if okanda:
        raise SystemExit('Finns inte i tidningar.json: ' + ', '.join(sorted(okanda)))
    andrade = []
    for t in valda:
        sida = fyll(t, mall, lanen, straken)
        p = os.path.join(ROT, t['slug'] + '.html')
        gammal = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        if gammal == sida:
            continue
        andrade.append(t['slug'] + ('' if gammal else ' (ny)'))
        if not kontroll:
            open(p, 'w', encoding='utf-8').write(sida)
    verb = 'skulle ändras' if kontroll else 'skrivna'
    print(f"{len(valda)} tidningar, {len(andrade)} {verb}: {', '.join(andrade) or 'inga'}")


if __name__ == '__main__':
    main()
