/* Halkvakt besöksräknare: en rad per sidvisning, utan kakor, IP eller användar-id.
   Skickar bara sidans sökväg, varifrån besökaren kom (domänen), en eventuell ?r=-kod och mobil/dator.
   Servern räknar en anonym dagsbesökare (hash med dagligt salt som slängs, IP:n sparas aldrig).

   28/10: klick på App Store- och Play-länkar räknas som "appklick".
   Våra egna enheter: öppna valfri sida med ?oss=1 en gång (?oss=0 tar bort). Det sparar en markering
   i den här webbläsaren, bara hos oss, och våra visningar räknas sedan som "oss" och hålls utanför siffrorna.
   statistik.html sätter samma markering när nyckeln skrivs in. */
(function () {
  try {
    if (location.hostname !== "halkvakt.se" || navigator.webdriver) return;
    var q = new URLSearchParams(location.search);
    var oss = false;
    try {
      if (q.get("oss") === "1") localStorage.setItem("hv-oss", "1");
      if (q.get("oss") === "0") localStorage.removeItem("hv-oss");
      oss = localStorage.getItem("hv-oss") === "1";
    } catch (e) {}
    var ref = "";
    if (document.referrer) {
      var h = new URL(document.referrer).hostname;
      ref = h === location.hostname ? "(intern)" : h;
    }
    var kod = q.get("r") || q.get("utm_source") || "";
    var mobil = /Mobi|Android|iPhone/i.test(navigator.userAgent) ? "m" : "d";
    var url = "https://xmpfztykhyvhmrzsnjrc.supabase.co/functions/v1/besok";
    function skicka(o) {
      var d = JSON.stringify(o);
      if (!(navigator.sendBeacon && navigator.sendBeacon(url, d))) {
        fetch(url, { method: "POST", body: d, keepalive: true, mode: "no-cors" });
      }
    }
    var bas = { p: location.pathname, r: ref, k: kod, m: mobil };
    if (oss) bas.o = 1;
    skicka(bas);

    // Klick till App Store eller Play (även länkar som läggs in senare på sidan).
    document.addEventListener("click", function (e) {
      try {
        var a = e.target && e.target.closest && e.target.closest("a[href]");
        if (!a) return;
        var g = /apps\.apple\.com/.test(a.href) ? "ios" : /play\.google\.com/.test(a.href) ? "android" : "";
        if (!g) return;
        var o = { p: location.pathname, r: ref, k: kod, m: mobil, t: "k", g: g };
        if (oss) o.o = 1;
        skicka(o);
      } catch (x) {}
    }, true);
  } catch (e) {}
})();
