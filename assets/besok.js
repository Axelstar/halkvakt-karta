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

/* 13/11: appknapparna. Halkvakt finns för iPhone och Android, och alla sidor laddar den här filen.
   Varje .knapp som går till App Store eller Google Play får sin butiks ikon (iPhone/Android).
   De allmänna knapparna ("Hämta appen", "Få varningar i appen") får båda ikonerna och går dit
   besökaren kan installera: Android-telefon till Google Play, iPhone till App Store, dator till
   startsidans Appen-del (båda knapparna och QR-koden). Utan skript går knappen till App Store som förut. */
(function () {
  try {
    var PLAY = "https://play.google.com/store/apps/details?id=se.halkvakt.app";
    var ua = navigator.userAgent;
    var android = /Android/i.test(ua);
    var ios = /iPhone|iPad|iPod/i.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
    var P = {
      ios: "M16.4 1.4c0 1.1-.4 2.2-1.1 3-.8.9-2 1.5-3.1 1.4-.1-1.1.4-2.3 1.1-3 .8-.8 2.1-1.4 3.1-1.4zM20.5 17.2c-.6 1.2-.8 1.8-1.6 2.9-1 1.5-2.4 3.4-4.2 3.4-1.6 0-2-1-4.1-1s-2.6 1-4.1 1c-1.8 0-3.1-1.7-4.1-3.3C-.3 16-.6 11.1 1.1 8.4c1.2-1.9 3.1-3 4.9-3 1.8 0 3 1 4.5 1s2.4-1 4.5-1c1.6 0 3.3.9 4.5 2.4-4 2.2-3.3 7.8 1 9.4z",
      android: "M17.6 9.5l1.8-3.2c.2-.3 0-.7-.3-.9-.3-.1-.6 0-.8.3l-1.9 3.2a11.4 11.4 0 0 0-8.9 0L5.6 5.7c-.2-.3-.5-.4-.8-.2-.3.2-.4.5-.2.8l1.8 3.2A10.8 10.8 0 0 0 1 18h22a10.8 10.8 0 0 0-5.4-8.5zM7 15.3a1.3 1.3 0 1 1 0-2.6 1.3 1.3 0 0 1 0 2.6zm10 0a1.3 1.3 0 1 1 0-2.6 1.3 1.3 0 0 1 0 2.6z"
    };
    function ikon(g) {
      return '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true" style="flex:none;display:block">'
        + '<path d="' + P[g] + '"/></svg>';
    }
    function play(kod) {
      return PLAY + "&referrer=" + encodeURIComponent("utm_source=halkvakt.se&utm_content=" + (kod || "knapp"));
    }
    var knappar = document.querySelectorAll('a.knapp[href*="apps.apple.com"], a.knapp[href*="play.google.com"]');
    for (var i = 0; i < knappar.length; i++) {
      var a = knappar[i];
      if (a.querySelector(".appikoner")) continue;
      var text = a.textContent;
      var g = a.getAttribute("data-plattform")
        || (/play\.google\.com/.test(a.href) || /Android/.test(text) ? "android" : /iPhone/.test(text) ? "ios" : "");
      var span = document.createElement("span");
      span.className = "appikoner";
      span.style.cssText = "display:inline-flex;align-items:center;gap:5px";
      span.innerHTML = g ? ikon(g) : ikon("ios") + ikon("android");
      a.insertBefore(span, a.firstChild);
      if (g) continue;
      var kod = (a.href.match(/[?&]ct=([^&]+)/) || [])[1];
      if (android) a.href = play(kod);
      else if (!ios) a.href = "/#appen";
    }
  } catch (e) {}
})();
