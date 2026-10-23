#!/usr/bin/env python3
"""Gör artikelmontaget till en tidningssida: press/<slug>-artikel.jpg (2400 × 1638, dator och mobil).

Standard är en neutral artikelsida med tidningens namn i Georgia, rubriken "Halt på vägarna runt <ort> i morse"
och tidningens ruta efter ingressen. Rutan visar EXEMPELSIFFROR (halka på ungefär varannan sträcka), inte
dagens läge, så montaget ser likadant ut oavsett väder. På datorn visar rutan fliken Vägarna, på mobilen
Pendling (eller Länet om tidningen saknar stråk).

Vill du hellre ha tidningens riktiga artikelsida: ta två skärmbilder själv (en artikel på tidningens sajt med
rutan inlagd efter ingressen; dator 1280 × 976, mobil 390 × 832) och ge dem med --dator och --mobil. Sätt då
montage till "egen" i tidningar.json.

Kör från repots rot (kräver: pip install playwright && playwright install chromium):
  python3 verktyg/montage.py st
  python3 verktyg/montage.py st --dator dator.png --mobil mobil.png
  python3 verktyg/montage.py st --ut /tmp/prov.jpg      (skriv någon annanstans, för att titta först)
"""
import argparse, copy, functools, html, http.server, json, os, socketserver, sys, tempfile, threading, urllib.parse

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROT, 'verktyg'))
from tidningssida import strak_ur_rutan  # noqa: E402

EXEMPELTID = '2026-10-19T04:30:00.000Z'   # visas som "Uppdaterad 06:30"
DATUMRAD = '19 oktober 2026 06:41'


def exempeldata(lan_slug, ort):
    """Kopior av data/lan.json och data/strackor.json där tidningens län har halka på ungefär varannan sträcka."""
    lan = json.load(open(os.path.join(ROT, 'data/lan.json'), encoding='utf-8'))
    strackor = json.load(open(os.path.join(ROT, 'data/strackor.json'), encoding='utf-8'))
    lan['generated_at'] = strackor['generated_at'] = EXEMPELTID
    antal = 0
    strackor_lan = []
    for l in strackor['lan']:
        if l['slug'] != lan_slug:
            continue
        strackor_lan = l['vagar']
        for i, v in enumerate(l['vagar']):
            for j, s in enumerate(v['strackor']):
                s['halt'] = (i + j) % 2 == 0
                if s['halt']:
                    s['text'] = 'Is- och snövägbana'
                    antal += 1
            if any(s['halt'] for s in v['strackor']):
                plats = ort or v['strackor'][0]['plats'].split(' - ')[0]
                v['kallast'] = {'yta': -1.8 if i % 2 else -2.6, 'namn': plats}
                v['kalla'] = 2
    for l in lan['lan']:
        if l['slug'] == lan_slug:
            forsta = next((x for v in strackor_lan for x in [v.get('kallast')] if x), None)
            l.update(halt=min(antal, l['vagavsnitt']), kalla=6, olyckor=1,
                     kallast={'yta': -2.6, 'namn': ort or (forsta['namn'] if forsta else l['kort'])})
    return lan, strackor


ARTIKEL = '''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--ink:#16191c;--mute:#6b737a;--rule:#e3e6e9;--bar:#eef0f2}
*{box-sizing:border-box}body{margin:0;background:#fff;color:var(--ink);font:400 17px/1.55 Georgia,"Times New Roman",serif}
.top{border-bottom:1px solid var(--rule)}
.mast{max-width:1180px;margin:0 auto;padding:22px 40px;display:flex;align-items:center;justify-content:space-between}
.namn{font:700 30px/1 Georgia,serif;letter-spacing:-.01em}
.knapp{width:96px;height:32px;border-radius:6px;background:var(--bar)}
.nav{max-width:1180px;margin:0 auto;padding:0 40px 16px;display:flex;gap:22px}
.nav i{display:block;height:12px;border-radius:6px;background:var(--bar)}
main{max-width:1180px;margin:0 auto;padding:36px 40px;display:grid;grid-template-columns:minmax(0,720px) 1fr;gap:48px}
.kick{font:700 14px/1 Arial,sans-serif;color:var(--mute);text-transform:uppercase;letter-spacing:.06em;margin:0 0 12px}
h1{font:700 46px/1.08 Georgia,serif;margin:0 0 14px;letter-spacing:-.01em}
.dat{font:400 14px Arial,sans-serif;color:var(--mute);margin:0 0 28px}
.ing{font:700 20px/1.45 Arial,sans-serif;margin:0 0 24px}
iframe{width:100%;max-width:480px;height:440px;border:0;display:block;margin:0 0 24px}
.side i{display:block;height:250px;border-radius:8px;background:var(--bar)}
@media(max-width:600px){.mast{padding:16px 20px}.namn{font-size:22px}.nav{padding:0 20px 12px;gap:14px}main{display:block;padding:24px 20px}h1{font-size:30px}.ing{font-size:17px}.side{display:none}}
</style></head><body>
<div class="top"><div class="mast"><div class="namn">{tidning}</div><div class="knapp"></div></div>
<div class="nav"><i style="width:60px"></i><i style="width:48px"></i><i style="width:70px"></i><i style="width:56px"></i><i style="width:64px"></i></div></div>
<main><article><p class="kick">{kick}</p><h1>Halt på vägarna {var} i morse</h1><p class="dat">{datum}</p>
<p class="ing">Trafikverket varnar för halka på flera vägar {var}. Här är läget just nu, sträcka för sträcka.</p>
<iframe src="{ruta}"></iframe>
<p>Halkan är värst på morgonen, innan solen hunnit värma vägbanan. Trafikverket uppmanar till försiktighet och god tid i trafiken.</p>
</article><aside class="side"><i></i></aside></main></body></html>'''

KOMPOSIT = '''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0;width:1200px;height:819px;overflow:hidden;background:#0B0E10;font-family:-apple-system,"Helvetica Neue",Arial,sans-serif}
.panel{position:absolute;left:30px;top:30px;width:1140px;height:820px;border-radius:40px;background:#111618;border:1px solid #1E282D}
.fonster{position:absolute;left:66px;top:66px;width:910px;height:800px;border-radius:14px 14px 0 0;overflow:hidden;background:#fff;box-shadow:0 30px 80px rgba(0,0,0,.5)}
.list{height:28px;background:#ECEEF0;border-bottom:1px solid #DCE0E3;position:relative}
.list i{position:absolute;top:10px;width:8px;height:8px;border-radius:50%}
.list b{position:absolute;left:328px;top:6px;width:260px;height:16px;border-radius:5px;background:#fff;font:400 9px/16px Arial,sans-serif;color:#444;text-align:center}
.fonster img{display:block;width:910px}
.telefon{position:absolute;left:835px;top:105px;width:275px;height:568px;border-radius:46px;background:#141819;padding:9px;box-shadow:0 30px 70px rgba(0,0,0,.6)}
.skarm{width:257px;height:550px;border-radius:38px;overflow:hidden;background:#fff;position:relative}
.status{height:30px;position:relative;font:600 11px/30px -apple-system,Arial,sans-serif;color:#000}
.status .kl{position:absolute;left:22px}.status .o{position:absolute;left:92px;top:7px;width:74px;height:20px;border-radius:12px;background:#000}
.status .b{position:absolute;right:20px;top:11px;width:16px;height:8px;background:#000;border-radius:1px}
.skarm img{display:block;width:257px}
.panel-botten{position:absolute;left:0;top:788px;width:1200px;height:40px;background:#0B0E10}
</style></head><body>
<div class="panel"></div>
<div class="fonster"><div class="list"><i style="left:12px;background:#FF5F57"></i><i style="left:26px;background:#FEBC2E"></i><i style="left:40px;background:#28C840"></i><b>{doman}</b></div><img src="{dator}"></div>
<div class="telefon"><div class="skarm"><div class="status"><span class="kl">9:41</span><span class="o"></span><span class="b"></span></div><img src="{mobil}"></div></div>
<div class="panel-botten"></div>
</body></html>'''


class TystHanterare(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--dator'); ap.add_argument('--mobil'); ap.add_argument('--ut')
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright

    t = next((x for x in json.load(open(os.path.join(ROT, 'verktyg/tidningar.json'), encoding='utf-8'))['tidningar']
              if x['slug'] == a.slug), None)
    if not t:
        raise SystemExit(f'{a.slug} finns inte i verktyg/tidningar.json. Lägg in tidningen där först.')
    st = strak_ur_rutan().get(t.get('strak') or '')
    ort = st['fran'] if st else t.get('ort', '')   # utan stråk: tidningens ort om den står i tidningar.json
    lankort = next(l['kort'] for l in json.load(open(os.path.join(ROT, 'data/lan.json'), encoding='utf-8'))['lan'] if l['slug'] == t['lan'])
    lan_d, str_d = exempeldata(t['lan'], ort)
    ut = a.ut or os.path.join(ROT, 'press', f"{a.slug}-artikel.jpg")
    tmp = tempfile.mkdtemp(prefix='montage-')

    srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(TystHanterare, directory=ROT))
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    bas = f'http://127.0.0.1:{port}/'

    def ruta(flik):
        q = [('lan', t['lan']), ('tema', 'ljus')] + ([('strak', t['strak'])] if st else []) + [
            ('namn', t['namn']), ('lank', t['lank']), ('lanktext', 'Mer trafik på ' + t['doman']),
            ('sponsor', 'Er annonsör här'), ('flik', flik)]
        return bas + 'ruta.html?' + urllib.parse.urlencode(q)

    with sync_playwright() as p:
        b = p.chromium.launch()

        def skott(bredd, hojd, dpr, flik, fil):
            ctx = b.new_context(viewport={'width': bredd, 'height': hojd}, device_scale_factor=dpr)
            ctx.route('**/data/lan.json*', lambda r: r.fulfill(json=lan_d))
            ctx.route('**/data/strackor.json*', lambda r: r.fulfill(json=str_d))
            ctx.route('**/assets/*besok.js*', lambda r: r.fulfill(body='', content_type='text/javascript'))
            sida = os.path.join(ROT, '.montage-artikel.html')
            open(sida, 'w', encoding='utf-8').write(ARTIKEL.replace('{tidning}', html.escape(t['fullnamn']))
                .replace('{kick}', html.escape(ort or lankort)).replace('{var}', html.escape('runt ' + ort if ort else 'i ' + lankort)).replace('{datum}', DATUMRAD).replace('{ruta}', html.escape(ruta(flik))))
            try:
                pg = ctx.new_page()
                pg.goto(bas + '.montage-artikel.html', wait_until='networkidle')
                fr = pg.frames[1]
                fr.wait_for_function("document.getElementById('tid').textContent.indexOf('06:30') >= 0", timeout=15000)
                pg.wait_for_timeout(1200)
                pg.screenshot(path=fil)
            finally:
                os.remove(sida)
            ctx.close()

        dator, mobil = a.dator, a.mobil
        if not dator:
            dator = os.path.join(tmp, 'dator.png'); skott(1280, 1100, 2, 'vagar', dator)
        if not mobil:
            mobil = os.path.join(tmp, 'mobil.png'); skott(390, 832, 3, 'pendling' if st else 'lan', mobil)

        komp = os.path.join(tmp, 'komposit.html')
        open(komp, 'w', encoding='utf-8').write(KOMPOSIT.replace('{doman}', html.escape(t['doman']))
            .replace('{dator}', 'file://' + os.path.abspath(dator)).replace('{mobil}', 'file://' + os.path.abspath(mobil)))
        ctx = b.new_context(viewport={'width': 1200, 'height': 819}, device_scale_factor=2)
        pg = ctx.new_page(); pg.goto('file://' + komp); pg.wait_for_timeout(300)
        pg.screenshot(path=ut, type='jpeg', quality=86)
        b.close()
    srv.shutdown()
    print('skrev', os.path.relpath(ut, ROT) if ut.startswith(ROT) else ut)


if __name__ == '__main__':
    main()
