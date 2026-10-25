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
# Valfria: strak (nyckel i STRAK), plattform (wix|wordpress|annat), bokning (URL), kundkontakt (sms|bokning|mejl, standard mejl)
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
        if strak and not re.search(r'\n\s*' + re.escape(strak) + r': \{ (lan: [^,]+, )?fran', ruta): sys.exit(f"{v['slug']}: stråket '{strak}' finns inte i STRAK i ruta.html")
        for f in FORBJUDET:
            if any(f in str(v[k]) for k in FALT): sys.exit(f"{v['slug']}: förbjuden formulering '{f}'")
        kort = lanen[v['lan']]['kort']
        f = {
            'css': css, 'slug': v['slug'], 'namn': v['namn'], 'fullnamn': v['fullnamn'], 'genitiv': v['genitiv'],
            'lan': v['lan'], 'lankort': kort, 'lank': urllib.parse.quote(v['lank'], safe=':/'), 'lanktext': v['lanktext'], 'kommentar': v['kommentar'],
            'lank_visas': re.sub(r'^https://(www\.)?|/$', '', v['lank']),
            'namn_q': urllib.parse.quote(v['namn']), 'lanktext_q': urllib.parse.quote(v['lanktext']),
            'strak_param': '&amp;strak=' + strak if strak else '',
            'pendling_text': ' och pendlarvägarna' if strak else '',
        }
        pl = v.get('plattform', '').lower()
        f['kod_instruktion'] = {'wix': 'i Wix under Lägg till, Bädda in kod, Bädda in HTML',
                                'wordpress': 'i WordPress med blocket Anpassad HTML'}.get(pl, 'för verktyg som tar iframe (Wix: Bädda in kod, WordPress: blocket Anpassad HTML)')
        f['steg2_text'] = {'wix': 'Rutan läggs in i Wix-redigeraren på några minuter, till exempel på startsidan.',
                           'wordpress': 'Rutan läggs in i WordPress på några minuter, till exempel på startsidan.'}.get(pl, 'Den som sköter er sajt klistrar in länken eller koden, till exempel på startsidan.')
        bokar = v.get('bokning', '')
        f['steg2_rubrik'] = 'Rutan på startsidan, med länk till er bokning' if bokar else 'Rutan på startsidan, med ert namn'
        kk = v.get('kundkontakt', 'mejl')
        f['steg1_rubrik'], f['steg1_text'] = {
            'sms': ('En rad i sms:et till kunden', 'Skickar ni sms när kunden bokat eller kan hämta bilen? Lägg till den här raden.'),
            'bokning': ('En rad i bokningsbekräftelsen', 'Er bokning skickar en bekräftelse till kunden. Lägg till den här raden i texten.'),
            'mejl': ('En rad i mejlen till kunderna', 'Svarar ni kunderna på mejl? Lägg till den här raden i signaturen.'),
            'paminnelse': ('En rad i påminnelsen inför säsongen', 'Ni påminner kunderna inför nästa säsong. Lägg till den här raden i påminnelsen.'),
        }[kk]
        f['halsning'] = f"Hej {v['personer']}. " if v.get('personer') else ''
        f['om'] = v.get('om', '')
        f['lank_mal'] = 'er bokning' if bokar else 'er sajt'
        f['langsta_ord'] = str(max(len(w.strip(',')) for w in ('Nya däck hos ' + v['namn'] + ', och väglaget på vägen hem').split()))
        f['kanal_visas'] = {'sms': 'Sms', 'bokning': 'Bokningsbekräftelse', 'mejl': 'Mejl', 'paminnelse': 'Påminnelse'}[kk]
        f['exempel_text'] = {'sms': f"Hej! Din bil är klar att hämtas hos {v['namn']}.",
                             'bokning': f"Hej! Din tid för däckbyte hos {v['namn']} är bokad. Välkommen.",
                             'mejl': f"Hej! Tack för bokningen, vi ses hos {v['namn']}.",
                             'paminnelse': f"Hej! Dags att byta till vinterdäck. Boka din tid hos {v['namn']}."}[kk]
        bild = f"press/verkstad-{v['slug']}.jpg"
        doman = re.sub(r'^https?://(www\.)?|/.*$', '', v.get('start') or v['lank'])
        f['montage_sektion'] = (f'''
<section>
  <div class="wrap stack" style="gap:28px">
    <p class="steg">Så kan det se ut hos er</p>
    <h2>Rutan på {doman}</h2>
    <figure class="montage"><a href="/{bild}"><img src="/{bild}" alt="Skiss: rutan med {f['genitiv']} namn inlagd på {doman}, på dator och mobil" loading="lazy" width="2400" height="1638"></a>
      <figcaption>Skiss med er startsida och exempelsiffror. Inget är ändrat på er sajt.</figcaption></figure>
  </div>
</section>
''' if os.path.exists(os.path.join(ROT, bild)) else '')
        f['band_q'] = '&amp;'.join(k + '=' + urllib.parse.quote(val, safe=':/') for k, val in
                                   [('lan', v['lan']), ('namn', v['namn']), ('ort', v.get('ort', '')), ('lank', v['lank']), ('lanktext', v['lanktext'])] if val)
        f['ort'] = v.get('ort', '') or kort
        f['kod_instruktion_kort'] = {'wix': 'i Wix under Lägg till, Bädda in kod, Bädda in HTML',
                                     'wordpress': 'i WordPress med blocket Anpassad HTML eller i temats sidhuvud'}.get(pl, 'där er sajt tar inbäddad kod')
        if os.path.exists(os.path.join(ROT, bild)):
            f['hero_klass'] = 'stack'
            f['hero_hoger'] = (f'''<div class="wrap"><figure class="montage"><a href="/{bild}"><img src="/{bild}" alt="Skiss: bandet med {f['genitiv']} namn överst på {doman}, på dator och mobil" width="2400" height="1638"></a>
      <figcaption>Skiss: bandet överst på {doman}, med exempelsiffror. Inget är ändrat på er sajt.</figcaption></figure></div>''')
            f['ruta_dold'] = 'hidden'
        else:
            f['hero_hoger'], f['ruta_dold'], f['hero_klass'] = '', '', 'tva'
        ut = mall
        for k, val in f.items(): ut = ut.replace('{{' + k + '}}', val)
        kvar = re.findall(r'\{\{[a-z_]+\}\}', ut)
        if kvar: sys.exit(f"{v['slug']}: fält kvar i mallen: {', '.join(sorted(set(kvar)))}")
        open(os.path.join(ROT, 'verkstad', v['slug'] + '.html'), 'w', encoding='utf-8').write(ut)
        skrivna.append(v['slug'])
    print(f"{len(skrivna)} verkstäder skrivna: {', '.join(skrivna)}")

if __name__ == '__main__':
    main()
