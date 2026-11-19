#!/usr/bin/env python3
"""Händelserna till rutans flik Händelser (Axel 19/11): data/handelser.json.

Källan är appens rapportfil, som Halkvakts funktion favoriter skriver var tionde minut ur Trafikverkets
öppna data till den publika hinken favoriter (Halkvakt DECISIONS #617). Här tas bara det rutan visar:
vägarbeten, hinder och omledningar, med de fält raderna behöver. Olyckorna står redan i
data/olyckor.geojson, som skrivs var tionde minut, och tas därför inte med här.

Filen ligger på halkvakt.se så att rutan aldrig hämtar något från en annan värd: tidningssidorna lovar
att läsarnas webbläsare inte kontaktar någon tredje part.

Körs av .github/workflows/handelser.yml en gång i timmen. En källa som inte svarar, har annat schema
eller är äldre än en timme skriver ingenting: den förra filen ligger kvar, och rutan visar inte en fil
som är äldre än två och en halv timme som läget just nu.

  python3 verktyg/handelser.py            # skriver data/handelser.json
  python3 verktyg/handelser.py --kontroll # hämtar och räknar, skriver ingenting
"""
import datetime, json, os, sys, urllib.request

KALLA = 'https://xmpfztykhyvhmrzsnjrc.supabase.co/storage/v1/object/public/favoriter/rapport-snabb.json'
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UT = os.path.join(ROT, 'data', 'handelser.json')
SLAG = ('vagarbete', 'hinder', 'omledning')
FALT = ('slag', 'rubrik', 't', 'p', 'vag', 'start', 'slut', 'korfalt', 'grans', 'sev')
HOGST_MIN = 60


def bygg(rapport, nu):
    """Rapportfilen till rutans fil. Kastar ValueError när källan inte går att lita på."""
    if rapport.get('schema') != 2 or not isinstance(rapport.get('poster'), list):
        raise ValueError(f"okänt schema: {rapport.get('schema')!r}")
    skriven = datetime.datetime.fromisoformat(rapport['generated_at'].replace('Z', '+00:00'))
    alder = (nu - skriven).total_seconds() / 60
    if not -5 <= alder <= HOGST_MIN:
        raise ValueError(f'källan är {alder:.0f} minuter gammal')
    poster = [{k: p[k] for k in FALT if p.get(k) is not None} for p in rapport['poster']
              if p.get('slag') in SLAG and isinstance(p.get('p'), list) and len(p['p']) == 2 and p.get('rubrik')]
    if not poster:
        raise ValueError('källan har inga poster av de slag rutan visar')
    return {'schema': 1, 'generated_at': rapport['generated_at'],
            'kalla': 'Trafikverkets öppna data, ur Halkvakts rapportfil för appens Favoriter', 'poster': poster}


def main():
    with urllib.request.urlopen(urllib.request.Request(KALLA, headers={'User-Agent': 'halkvakt-karta'}), timeout=60) as r:
        rapport = json.load(r)
    try:
        ut = bygg(rapport, datetime.datetime.now(datetime.timezone.utc))
    except ValueError as e:
        print(f'handelser: skriver ingenting, {e}')
        return 0
    text = json.dumps(ut, ensure_ascii=False, separators=(',', ':'))
    print(f"handelser: {len(ut['poster'])} poster, {len(text.encode())} byte, källan skriven {ut['generated_at']}")
    if '--kontroll' not in sys.argv:
        with open(UT, 'w', encoding='utf-8') as f:
            f.write(text + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
