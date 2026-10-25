# Partnerutskicken: vem vi skriver till och vad de erbjuds

Spelboken för förslagen till organisationer som inte är tidningar: radio, försäkringsbolag, NTF,
trafikskolor, fjällorter, kommuner och förbund. Axels beslut 25/10: varje typ får ett eget erbjudande,
byggt på deras egen sajt, och inget mejl går utan att Axel har läst det. Nattens agent (Research och
sidbygge) läser den här filen. Ändra här, så ändras nästa natts förslag.

Raderna ligger i redaktionslistan, samlingen `partner`
(https://claude.ai/artifact/EYhmeRRWUhP4wBM24dJfGn). Kontrollrummet visar dem.

## Fem regler

1. **Bygg på deras egen sajt.** Läs vad de redan skriver om vinterkörning, halka, vilt eller
   resvägen. Citera kort (högst en rad per sida, under 15 ord) och visa var Halkvakt passar in.
   Förlagan är `m.html`: "Där står i dag" och "Vårt förslag", steg för steg, det minsta först.
2. **Det första steget tar fem minuter.** En länk, en rad i en lista eller en ruta. Större steg kommer efter.
3. **En egen kod per partner.** Länkar till halkvakt.se och App Store-länken på sidan bär `?r=<kod>`.
   Koden är partnerns slug. Erbjudandet säger: "Ni ser själva hur många som klickar." Statistiksidan
   räknar koderna.
4. **Gratis, utan tidsgräns, och bara det vi kan visa.** Inga löften om färre skador, färre olyckor
   eller sparade kronor. Vi säger vad appen gör och var datan kommer ifrån. Inga priser, inga avtal,
   ingen exklusivitet.
5. **Ett mejl, en påminnelse efter 7 dagar, sedan slut.** Agenten lägger utkastet en natt när
   deras län är kallt (halt ≥ 1 eller kalla ≥ 3 i `data/lan.json`), med nattens siffra i första
   meningen, så att Axel kan skicka det samma morgon. Sidan kan byggas i förväg. Bara radio kan få
   läget varje kall morgon, och först efter att de sagt ja.

## Det vi får säga om Halkvakt

- Varnar med rösten för halka, frysrisk, olyckor, vilt och fartkameror, innan föraren är där.
- Bygger på Trafikverkets öppna data. Gratis, utan konto och utan reklam.
- Finns för iPhone. Android kommer i vinter.
- "Din position lämnar inte telefonen av sig själv." Ordagrant, aldrig omskrivet.
- Rutan: läget i länet just nu, uppdateras var 30:e minut, med partnerns namn och länk.

## Typerna

| typ | Vem | Vad de vill ha | Vårt erbjudande | Vad vi ber om | Ruta |
|---|---|---|---|---|---|
| `radio` | P4:s lokala kanaler | Något att säga i morgontrafiken | Läget i länet de kalla morgnarna, som färdig text att läsa: halka, stationer under noll, kallaste vägbanan, med klockslag och källa | Att de nämner källan, Trafikverket via Halkvakt | Länets ruta för deras webbsida om trafiken |
| `forsakring` | Länsförsäkringar (ett bolag per län), andra bolag med regionala sidor | Skadeförebyggande innehåll till kunderna | Rutan med deras namn på deras sida om vinterkörning, och en färdig rad till vinterutskicket | Ett tips till kunderna, med deras egen kod | Länets ruta, deras namn |
| `ntf` | NTF:s regionala förbund | Trafiksäkerhet, material till föreläsningar | Rutan för länet, och appen som verktyg att tipsa om | Tips i deras kanaler | Länets ruta, deras namn |
| `trafikskola` | Trafikskolor, halkbanor (riskutbildning 2) | Möter varje ny förare | En kort text att dela ut efter halkbanan: vad du lärde dig på banan, och en röst som säger till när det är halt på riktigt | Att de delar ut texten eller länkar | Ingen, eller länets |
| `fjall` | Fjällorter, skidanläggningar, turistbyråer | Att gästerna kommer fram | "Vägen hit just nu": rutan med sträckorna till orten | Rutan på sidan om resvägen | Länets ruta med stråk (kräver ny ort i `STRAK`, fråga Axel först) |
| `kommun` | Kommuner, länsstyrelser | Krisinformation, personal som kör (hemtjänst, skolskjuts) | Rutan på trafik- eller krissidan, och ett tips till personal som kör tidigt | Inbäddning och ett internt tips | Länets ruta, deras namn |
| `forbund` | MHF, taxi, åkerier, jägare med flera | Medlemsnytta | Appen som en gratis förmån att tipsa medlemmarna om, rutan för hela landet | En rad i medlemsbladet eller på sajten | Hela landet (`widget.html`, som M) |

## Sidan

- `<slug>.html` i roten, handbyggd efter `m.html`. Rubrik "Förslag till <namn>". Sidans iframe är
  `ruta.html?lan=<lan>&namn=<kort namn>&lank=<deras sida>&lanktext=<kort>` (eller `widget.html?namn=…`
  för hela landet), så att `python3 verktyg/rutor.py` bygger `halkvakt.se/ruta/<slug>/` själv.
- `<meta name="robots" content="noindex">`. Varumärkesguidens regler: inga utropstecken, inga emojier,
  inga långa tankstreck, du-tilltal i appens röst men ni-tilltal till organisationen i förslaget.
- Inga påhittade tal. Siffror på sidan kommer från rutan, som läser datan live.

## Mejlet

- Läggs som **utkast** i Zoho (hej@halkvakt.se, `mode: "draft"`). Skickas aldrig av agenten.
- Till: en funktionsadress läst på deras egen kontaktsida (info@, kommunikation@, trafik@ o.d.),
  aldrig en namngiven person, aldrig gissad.
- Högst 120 ord. Första meningen: dagens läge i deras län. Sedan vad de får, i en mening. Sedan
  länken till deras sida. Sist: "Allt är gratis och utan tidsgräns. Vill ni inte ha fler mejl räcker
  det att svara." Avsändare Axel Lagerlöf, Halkvakt.
- Ämne: "<Deras namn>: väglaget i <län> på er sida, gratis".
