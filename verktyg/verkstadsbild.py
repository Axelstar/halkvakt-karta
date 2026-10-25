#!/usr/bin/env python3
"""Gör montaget till en verkstadssida: press/verkstad-<slug>.jpg (Axel 25/10: "visa något från deras sida").

Verkstadens riktiga startsida öppnas i en webbläsare, och rutan med verkstadens namn läggs in på sidan,
under det första stora blocket (dator) eller efter de första skärmfulla (mobil). Bilden är en skiss:
rutan visar EXEMPELSIFFROR (halka på ungefär varannan sträcka, samma som tidningsmontagen), och sidan
är verkstadens egen så som den såg ut när bilden togs. Kakrutor döljs, inget klickas eller skickas.

Kör från repots rot (kräver: pip install playwright && playwright install chromium):
  python3 verktyg/verkstadsbild.py lattkrangt
  python3 verktyg/verkstadsbild.py lattkrangt --ut /tmp/prov.jpg     (titta först)
  python3 verktyg/verkstadsbild.py --alla
"""
import argparse, html, json, os, sys, tempfile, urllib.parse

BAND = True   # verkstäderna får bandet överst (Axel 25/10); False ger rutan inlagd på sidan

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROT, 'verktyg'))
from montage import exempeldata, KOMPOSIT  # noqa: E402
from tidningssida import strak_ur_rutan  # noqa: E402

# Döljer vanliga kakrutor och chattbubblor utan att klicka i dem. Bara inne i body: WordPress-sajter
# bär ofta en cmplz- eller cookie-klass på själva body, och då försvann hela sidan (Lättkrängt 25/10).
DOLJ = '''body :is([id*="cookie" i],[class*="cookie" i],[id*="consent" i],[class*="consent" i],[class*="cmplz" i],[id*="cmplz" i],
[id*="CybotCookiebot"],[class*="gdpr" i],[id*="gdpr" i],[class*="chat-widget" i],[id*="tidio" i],[class*="tawk" i],
#wix-cookie-banner,[data-hook="consent-banner-root"]):not(:has(iframe[src*="halkvakt.se"])){display:none!important}'''

# Bandet överst (Axel 25/10, "som på Wall Street"): fast högst upp, sidan skjuts ner lika mycket.
LAGG_IN_BAND = '''([src, mobil]) => {
  const h = mobil ? 36 : 40;
  const box = document.createElement('div');
  box.style.cssText = 'all:initial;display:block;position:fixed;left:0;right:0;top:0;height:' + h + 'px;z-index:2147483646;box-shadow:0 1px 0 rgba(0,0,0,.08)';
  const f = document.createElement('iframe');
  f.title = 'Väglaget'; f.className = 'skip-lazy no-lazyload'; f.setAttribute('data-no-lazy', '1'); f.setAttribute('loading', 'eager');
  f.style.cssText = 'all:initial;display:block;width:100%;height:' + h + 'px;border:0';
  box.appendChild(f); document.documentElement.appendChild(box);
  document.documentElement.style.setProperty('margin-top', h + 'px', 'important');
  f.src = src; scrollTo(0, mobil ? 0 : Math.min(420, Math.max(0, document.documentElement.scrollHeight - innerHeight)));
  return 500;
}'''

LAGG_IN = '''([src, mobil]) => {
  const vh = innerHeight;
  const synlig = e => { for (let x = e; x && x !== document.body; x = x.parentElement) { const c = getComputedStyle(x); if (c.display === 'none' || c.visibility === 'hidden' || +c.opacity === 0) return false; } return true; };
  // Stora, synliga block under sidhuvudet, uppifrån. Rutan läggs efter det första där den faktiskt syns.
  const block = [...document.body.querySelectorAll('section, main > div, header + div, [data-testid="section"], .elementor-section, .elementor-top-section, .e-con, .wp-block-cover, .wp-block-group, article, .entry-content > *')]
    .filter(e => { const r = e.getBoundingClientRect(); return r.top + scrollY > 40 && r.height > (mobil ? 200 : 260) && r.width > innerWidth * 0.6 && synlig(e); })
    .sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
  const box = document.createElement('div');
  box.style.cssText = 'all:initial;display:block;box-sizing:border-box;width:100%;padding:' + (mobil ? '20px 16px' : '40px 24px') + ';background:#fff;position:relative;z-index:5';
  const f = document.createElement('iframe');
  f.title = 'Väglaget'; f.className = 'skip-lazy no-lazyload'; f.setAttribute('data-no-lazy', '1'); f.setAttribute('loading', 'eager');
  f.style.cssText = 'all:initial;display:block;margin:0 auto;width:100%;max-width:480px;height:440px;border:0;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.18)';
  box.appendChild(f);
  let lagd = false;
  for (const mal of block) { mal.insertAdjacentElement('afterend', box); if (box.getBoundingClientRect().height > 300) { lagd = true; break; } }
  if (!lagd) { const m = document.querySelector('main') || document.body; m.insertBefore(box, m.children[1] || null); }
  f.src = src;   // efter insättningen, så att sajtens lazy-load inte hinner byta src mot data-src
  const top = box.getBoundingClientRect().top + scrollY;
  scrollTo(0, Math.max(0, top - (mobil ? 140 : vh - 560)));
  return box.getBoundingClientRect().height;
}'''


def bygg(b, v, ut):
    st = strak_ur_rutan().get(v.get('strak') or '')
    ort = st['fran'] if st else ''
    lan_d, str_d = exempeldata(v['lan'], ort)
    tmp = tempfile.mkdtemp(prefix='verkstadsbild-')

    def band():
        q = [('lan', v['lan']), ('namn', v['namn']), ('lank', v['lank']), ('lanktext', v['lanktext'])] + ([('ort', ort or v.get('ort', ''))] if (ort or v.get('ort')) else [])
        return 'https://halkvakt.se/band.html?' + urllib.parse.urlencode(q)

    def ruta(flik):
        q = [('v', '6'), ('lan', v['lan']), ('tema', 'ljus')] + ([('strak', v['strak'])] if st else []) + [
            ('namn', v['namn']), ('lank', v['lank']), ('lanktext', v['lanktext']), ('flik', flik)]
        return 'https://halkvakt.se/ruta.html?' + urllib.parse.urlencode(q)

    start = v.get('start') or v['lank']

    def skott(bredd, hojd, dpr, mobil, flik, fil):
        ctx = b.new_context(viewport={'width': bredd, 'height': hojd}, device_scale_factor=dpr, locale='sv-SE',
                            user_agent=None if not mobil else 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
        ctx.route('**/halkvakt.se/data/lan.json*', lambda r: r.fulfill(json=lan_d))
        ctx.route('**/halkvakt.se/data/strackor.json*', lambda r: r.fulfill(json=str_d))
        pg = ctx.new_page()
        pg.goto(start, wait_until='load', timeout=45000)
        pg.wait_for_timeout(2500)
        pg.add_style_tag(content=DOLJ)
        h = pg.evaluate(LAGG_IN_BAND, [band(), mobil]) if BAND else pg.evaluate(LAGG_IN, [ruta(flik), mobil])
        if h < 300: raise RuntimeError(f'rutan syns inte på sidan (höjd {h})')
        fr = None
        for _ in range(120):
            fr = next((f for f in pg.frames if ('halkvakt.se/band.html' if BAND else 'halkvakt.se/ruta.html') in f.url), None)
            if fr and fr.evaluate("!!document.getElementById('tid')"): break
            pg.wait_for_timeout(250)
        fr.wait_for_function("document.getElementById('tid').textContent.indexOf('06:30') >= 0", timeout=40000)
        if BAND:   # stilla bild: rullningen stoppad där erbjudandet syns
            fr.add_style_tag(content='.rulle{animation:none!important}')
            if mobil:   # på mobilen syns bara en post: visa erbjudandet till verkstaden
                fr.evaluate("(() => { const a = document.querySelector('.post a'); if (!a) return; const p = a.closest('.post'); document.getElementById('rulle').style.transform = 'translateX(' + (-p.offsetLeft + 30) + 'px)'; })()")
        pg.wait_for_timeout(1500)
        pg.screenshot(path=fil)
        ctx.close()

    dator, mobil = os.path.join(tmp, 'dator.png'), os.path.join(tmp, 'mobil.png')
    skott(1280, 1100, 2, False, 'vagar', dator)
    skott(390, 832, 3, True, 'pendling' if st else 'lan', mobil)
    doman = urllib.parse.urlparse(start).netloc.replace('www.', '')
    komp = os.path.join(tmp, 'komposit.html')
    open(komp, 'w', encoding='utf-8').write(KOMPOSIT.replace('{doman}', html.escape(doman))
        .replace('{dator}', 'file://' + dator).replace('{mobil}', 'file://' + mobil))
    ctx = b.new_context(viewport={'width': 1200, 'height': 819}, device_scale_factor=2)
    pg = ctx.new_page(); pg.goto('file://' + komp); pg.wait_for_timeout(300)
    pg.screenshot(path=ut, type='jpeg', quality=86)
    ctx.close()
    print('skrev', os.path.relpath(ut, ROT) if ut.startswith(ROT) else ut)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug', nargs='?'); ap.add_argument('--ut'); ap.add_argument('--alla', action='store_true')
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    alla = json.load(open(os.path.join(ROT, 'verktyg/verkstader.json'), encoding='utf-8'))
    valda = alla if a.alla else [v for v in alla if v['slug'] == a.slug]
    if not valda: raise SystemExit(f'{a.slug} finns inte i verktyg/verkstader.json')
    os.makedirs(os.path.join(ROT, 'press'), exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for v in valda:
            try:
                bygg(b, v, a.ut if (a.ut and not a.alla) else os.path.join(ROT, 'press', f"verkstad-{v['slug']}.jpg"))
            except Exception as e:
                print(f"{v['slug']}: gick inte ({str(e).splitlines()[0][:160]})")
        b.close()


if __name__ == '__main__':
    main()
