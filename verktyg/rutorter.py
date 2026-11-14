#!/usr/bin/env python3
"""Bygger assets/ruta-orter.json: orterna som namnges på rutans kartflik (ruta.html?karta=1).

Några få orter per län, störst först, så att läsaren hittar på kartan. Koordinaten är ortssidans egen punkt
(ort/<slug>/index.html, tätortens punkt i Wikidata, CC0), så kartfliken och ortssidan pekar på samma plats.

Kör från repots rot:  python3 verktyg/rutorter.py
"""
import json, os, re

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORTER = {
    'stockholm': ['Stockholm', 'Södertälje', 'Norrtälje', 'Nynäshamn'],
    'uppsala': ['Uppsala', 'Enköping', 'Tierp', 'Östhammar'],
    'sodermanland': ['Nyköping', 'Eskilstuna', 'Katrineholm', 'Strängnäs'],
    'ostergotland': ['Linköping', 'Norrköping', 'Motala', 'Mjölby'],
    'jonkoping': ['Jönköping', 'Värnamo', 'Nässjö', 'Vetlanda', 'Tranås'],
    'kronoberg': ['Växjö', 'Ljungby', 'Älmhult', 'Alvesta'],
    'kalmar': ['Kalmar', 'Västervik', 'Oskarshamn', 'Borgholm', 'Vimmerby'],
    'gotland': ['Visby'],
    'blekinge': ['Karlskrona', 'Karlshamn', 'Ronneby', 'Sölvesborg'],
    'skane': ['Malmö', 'Helsingborg', 'Kristianstad', 'Ystad', 'Lund', 'Hässleholm'],
    'halland': ['Halmstad', 'Varberg', 'Kungsbacka', 'Falkenberg'],
    'vastra-gotaland': ['Göteborg', 'Borås', 'Skövde', 'Trollhättan', 'Uddevalla', 'Strömstad'],
    'varmland': ['Karlstad', 'Arvika', 'Kristinehamn', 'Torsby', 'Säffle'],
    'orebro': ['Örebro', 'Karlskoga', 'Lindesberg', 'Askersund'],
    'vastmanland': ['Västerås', 'Köping', 'Sala', 'Fagersta'],
    'dalarna': ['Falun', 'Borlänge', 'Mora', 'Ludvika', 'Sälen', 'Avesta'],
    'gavleborg': ['Gävle', 'Hudiksvall', 'Bollnäs', 'Söderhamn', 'Ljusdal', 'Sandviken'],
    'vasternorrland': ['Sundsvall', 'Örnsköldsvik', 'Härnösand', 'Sollefteå', 'Ånge'],
    'jamtland': ['Östersund', 'Åre', 'Strömsund', 'Bräcke', 'Krokom'],
    'vasterbotten': ['Umeå', 'Skellefteå', 'Lycksele', 'Storuman', 'Vilhelmina'],
    'norrbotten': ['Luleå', 'Kiruna', 'Piteå', 'Gällivare', 'Haparanda', 'Arjeplog', 'Boden'],
}
slugga = lambda t: re.sub(r'[^a-z0-9]+', '-', t.lower().replace('å', 'a').replace('ä', 'a').replace('ö', 'o').replace('é', 'e')).strip('-')

ut = {}
for lan, namn in ORTER.items():
    ut[lan] = []
    for n in namn:
        f = os.path.join(ROT, 'ort', slugga(n), 'index.html')
        m = re.search(r'punkt=([0-9.]+),([0-9.]+)', open(f, encoding='utf-8').read()) if os.path.exists(f) else None
        if not m: print('saknar punkt:', lan, n); continue
        ut[lan].append([n, round(float(m.group(1)), 3), round(float(m.group(2)), 3)])
json.dump(ut, open(os.path.join(ROT, 'assets/ruta-orter.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(sum(len(v) for v in ut.values()), 'orter i', len(ut), 'län')
