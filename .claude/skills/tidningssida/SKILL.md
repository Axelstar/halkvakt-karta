---
name: tidningssida
description: Bygger en förslagssida till en lokaltidning på halkvakt.se/<tidning> (som halkvakt.se/st), med tidningens egen väglagsruta, pendlarstråk, artikelmontage och egen rutadress. Använd när en ny tidning ska få en sida, när en befintlig tidningssida ska rättas, eller när någon säger "gör en sida till <tidning>".
---

# Tidningssidorna på halkvakt.se

Varje lokaltidning vi kontaktar får en egen sida, till exempel https://halkvakt.se/st. Sidan visar tidningens
egen väglagsruta live (deras namn, deras länk, en annonsrad de kan sälja), ett artikelmontage, koden att klistra
in och villkoren. Förlagan är `st.html`. Alla sidor byggs av samma verktyg, så de ser likadana ut och rättas på
ett ställe.

Allt sker i repot **Axelstar/halkvakt-karta** (sajten halkvakt.se, GitHub Pages). Det som behövs:

| Fil | Vad den är |
|---|---|
| `verktyg/tidningar.json` | En post per tidning. Det enda du fyller i för hand. |
| `verktyg/tidningssida.py` | Bygger `<slug>.html` ur mallen. Siffror och vägar läses ur datan. |
| `verktyg/tidningssida.mall.html` | Mallen (st.html med fält). Ändra här om alla sidor ska ändras. |
| `verktyg/montage.py` | Gör `press/<slug>-artikel.jpg`, artikeln på dator och mobil. |
| `verktyg/rutor.py` | Gör tidningens egen rutadress `halkvakt.se/ruta/<slug>/`. |
| `ruta.html`, `STRAK` | Pendlarstråken. En ny ort läggs till här. |

**Ändra aldrig en genererad sida för hand.** Nästa körning skriver över den. Ändra posten, mallen eller verktyget.

## Gången

### 1. Hämta repot färskt

```
git clone https://github.com/Axelstar/halkvakt-karta   # eller: git pull --rebase origin main
cd halkvakt-karta
```

`data/` skrivs av en bot var 30:e minut, så hämta alltid senaste innan du bygger och `git pull --rebase` före push.

### 2. Finns tidningen redan?

Sök på slug och namn i `verktyg/tidningar.json`. Hälsinglands fyra tidningar (HT, Ljusnan, Söderhamns-Kuriren,
Ljusdals-Posten) delar `halsingland.html` och byggs inte av det här verktyget; `nwt.html` är också handbyggd.
Rör inte dem.

### 3. Samla uppgifterna om tidningen

Kontrollera på tidningens egen sajt, gissa inte. Fråga den som bad om sidan när något är oklart.

| Fält | Exempel (ST) | Regel |
|---|---|---|
| `slug` | `st` | Adressen: halkvakt.se/st. Gemener, inga å/ä/ö. Gärna domänens första del. |
| `fullnamn` | `Sundsvalls Tidning` | Tidningens hela namn som det står i deras logga. |
| `namn` | `ST` | Det rutan heter ("ST · Väglaget"). Förkortningen om tidningen själv använder den, annars hela namnet. |
| `genitiv` | `ST:s` | Kolon bara efter förkortning: `ST:s`, `VK:s`. Annars bara s: `Norrans`, `Dala-Demokratens`, `Enköpings-Postens`. Slutar namnet på s blir det oförändrat. |
| `doman` | `st.nu` | Utan www. |
| `lank` | `https://www.st.nu/` | Tidningens startsida (eller trafiksida om de har en). |
| `lan` | `vasternorrland` | Länets slug ur `data/lan.json`. |
| `strak` | `sundsvall` | Nyckeln i `STRAK` i ruta.html för tidningens ort. Se steg 4. Tom (`""`) om orten inte har stråk; då får sidan två vyer i stället för tre. |
| `lasarort` | `Härnösand` | En ort läsarna pendlar till. Ett av stråkens mål. Används i "Är det halt till Härnösand i morse?". Tom om `strak` är tom. |
| `exempel_stracka` | `Sundsvall Trafikplats Skönsmon–Gnarp` | En sträcka på en E-väg nära orten, med Trafikverkets namn ur `data/strackor.json`, men med kort tankstreck `–` utan mellanslag i stället för ` - `. |
| `montage` | `neutral` | `neutral` (standard), `egen` (riktig artikel från tidningens sajt, bara om Axel ber om det) eller `inget`. |
| `kommentar` | `Förslaget till ST (Bengt 24/10): samma upplägg som de andra tidningssidorna, byggd av generatorn för tidningssidorna.` | Vem som bad om sidan och datum. Behåll resten av meningen ordagrant. |

Se vilka län och vägar som finns:

```
python3 -c "import json;[print(l['slug'],'·',l['kort']) for l in json.load(open('data/lan.json'))['lan']]"
python3 -c "
import json,sys;l=[x for x in json.load(open('data/strackor.json'))['lan'] if x['slug']==sys.argv[1]][0]
for v in l['vagar']:
  for s in v['strackor']: print(repr(v['vag']), repr(s['plats']))" vasternorrland
```

### 4. Pendlarstråken (bara om orten saknas i STRAK)

Öppna `ruta.html` och sök på `var STRAK = {`. Finns orten redan som nyckel (t.ex. `sundsvall`, `umea`, `falun`)
använder du den. Annars lägger du till en ny post sist bland tidningssidornas stråk, efter samma mönster
(exemplet finns redan i STRAK och visar bara formen):

```js
    // <Tidning> (<vem> <datum>): stråken från <ort>.
    harnosand: { lan: 'vasternorrland', fran: 'Härnösand', strak: [
      { till: 'Sundsvall', delar: [['E 4', 'Härnösand - Sundsvall']] },
      { till: 'Docksta', delar: [['E 4', 'Gallsäter - Härnösand'], ['E 4', 'Docksta - Gallsäter']] }
    ] },
```

- 4 till 6 mål som folk faktiskt pendlar till, inom länet.
- Varje del är `['<vag>', '<plats>']` **exakt** som i `data/strackor.json` (stavning, mellanslag, ` - `).
  Generatorn stoppar om en del inte finns, eftersom rutan annars tyst hoppar över den.
- Ingen temperatur på stråken, bara halka per sträcka. Det är beslutat (DECISIONS #611).
- Finns ingen rimlig stråkkedja i datan för orten: låt bli och sätt `strak` till `""`. Skriv det i svaret.

### 5. Lägg in posten och gör montaget

Lägg posten sist i `"tidningar"` i `verktyg/tidningar.json`. Gör sedan montaget:

```
pip install playwright && playwright install chromium     # första gången
python3 verktyg/montage.py <slug>
```

Det skriver `press/<slug>-artikel.jpg`: en neutral artikelsida med tidningens namn, rubriken "Halt på vägarna runt
<ort> i morse" och tidningens ruta med **exempelsiffror** (halka på ungefär varannan sträcka). Sidan säger under
bilden att siffrorna är exempel och att artikelsidan är en skiss. **Titta på bilden** innan du går vidare:
rätt namn överst i rutan, rätt domän i adressfältet, Vägarna på datorn, Pendling på mobilen.

`montage: "egen"` betyder en skärmbild av en riktig artikel på tidningens sajt med rutan inlagd. Gör det bara om
Axel ber om det: ta skärmbilderna själv (dator 1280 × 976, mobil 390 × 832) och kör
`python3 verktyg/montage.py <slug> --dator dator.png --mobil mobil.png`.

### 6. Bygg sidan och rutadressen

```
python3 verktyg/tidningssida.py <slug>
python3 verktyg/rutor.py
python3 verktyg/tidningssida.py --kontroll      # ska säga "0 skulle ändras"
git status --short                              # bara de nya filerna och ev. ruta.html
```

Ändrar körningen andra tidningars sidor än den nya, stanna och ta reda på varför innan du pushar.
Raden `obs …` är en varning, inget fel.

### 7. Titta på sidan innan den går ut

```
python3 -m http.server 8000      # öppna http://localhost:8000/<slug>.html
```

Kontrollera på dator och i 390 px bredd: rutan överst visar tidningens namn och länets läge, flikarna går att
svepa, Pendling visar rätt ort, montaget laddar, ingen sidledsrullning. Läs texterna en gång: rätt län, rätt ort,
rätt genitiv.

### 8. Publicera

```
git add <slug>.html press/<slug>-artikel.jpg ruta/<slug> verktyg/tidningar.json ruta.html
git commit -m "Tidningssida för <Fullnamn>"
git pull --rebase origin main && git push origin HEAD:main
```

GitHub Pages publicerar på 1 till 2 minuter. Kontrollera sedan att https://halkvakt.se/<slug> och
https://halkvakt.se/ruta/<slug>/ svarar och visar tidningens namn (`curl -s https://halkvakt.se/<slug> | grep -c "<namn>"`).

### 9. Säg vad som är klart

Ge länken till sidan och rutadressen, och nämn det som avviker (inga stråk, egen ort, en gissning du fick göra).
**Skicka aldrig mejl till tidningen själv.** Utskicken går via Axel och morgonuppgiften; säg bara att sidan är
klar att länka till och att den bör in i redaktionslistan.

## Regler som gäller på sidorna

Mallen följer redan reglerna. Skriver du ny text någonstans gäller samma sak:

- **Inga påhittade tal.** Antal vägavsnitt, vägar och sträckor räknas ur `data/`. Montaget är märkt som exempel.
- **Positionsmeningen:** "ingen position lämnar telefonen automatiskt". Aldrig "Positionen lämnar aldrig telefonen".
- **Inga långa tankstreck (—)**, inga utropstecken. Kort streck (–) bara mellan orter: Sundsvall–Gnarp.
- Sidorna är `noindex` och ligger inte i `sitemap.xml`. Lägg inte in dem där.
- Rutan har ingen spårning och inga kakor. Lägg aldrig till skript i `ruta.html`, `widget.html` eller `ruta/`.
- Halkvakt är fristående från Trafikverket. Skriv aldrig att vi samarbetar med dem.

## När generatorn stoppar

| Meddelande | Gör så här |
|---|---|
| `saknar … i tidningar.json` | Fyll i fältet. |
| `länet '…' finns inte` | Använd slug ur `data/lan.json`, t.ex. `vasternorrland`, inte "Västernorrland". |
| `stråket '…' finns inte i STRAK` | Lägg till stråket (steg 4) eller sätt `strak` till `""`. |
| `har delar som inte finns i data/strackor.json` | Stavningen skiljer sig. Kopiera namnet exakt ur listan i steg 3. |
| `… saknas. Gör montaget först` | Kör `verktyg/montage.py <slug>` eller sätt `montage` till `"inget"`. |
| `förbjuden formulering` | En text i posten bryter mot reglerna ovan. Skriv om den. |
