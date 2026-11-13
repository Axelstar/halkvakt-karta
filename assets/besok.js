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
   Regeln: det är alltid två knappar, en till App Store och en till Google Play.
   Varje allmän knapp ("Hämta appen", "Få varningar i appen") byts mot ett par (.apppar). Besökarens
   egen butik står först och är gul (Android: Google Play, annars App Store), den andra är neutral.
   Knappar som redan gäller en butik ("Ladda ner för iPhone/Android") får bara butikens ikon.
   Utsidan ser stilen i assets/hv.css (.apppar). Utan skript står App Store-knappen kvar som förut. */
(function () {
  try {
    var PLAY = "https://play.google.com/store/apps/details?id=se.halkvakt.app";
    var android = /Android/i.test(navigator.userAgent);
    var P = {
      ios: "M16.4 1.4c0 1.1-.4 2.2-1.1 3-.8.9-2 1.5-3.1 1.4-.1-1.1.4-2.3 1.1-3 .8-.8 2.1-1.4 3.1-1.4zM20.5 17.2c-.6 1.2-.8 1.8-1.6 2.9-1 1.5-2.4 3.4-4.2 3.4-1.6 0-2-1-4.1-1s-2.6 1-4.1 1c-1.8 0-3.1-1.7-4.1-3.3C-.3 16-.6 11.1 1.1 8.4c1.2-1.9 3.1-3 4.9-3 1.8 0 3 1 4.5 1s2.4-1 4.5-1c1.6 0 3.3.9 4.5 2.4-4 2.2-3.3 7.8 1 9.4z",
      android: "M3.6 1.3c-.2.2-.3.6-.3 1v19.4c0 .4.1.8.3 1l.1.1L14.6 12v-.2L3.7 1.2l-.1.1zM18.2 15.6l-3.6-3.6v-.2l3.6-3.6h.1l4.3 2.4c1.2.7 1.2 1.8 0 2.5l-4.3 2.4h-.1zM18.3 15.6L14.6 12 3.6 22.9c.4.4 1.1.5 1.8.1l12.9-7.4M18.3 8.4L5.4 1c-.7-.4-1.4-.4-1.8.1L14.6 12l3.7-3.6z"
    };
    function ikon(g) {
      return '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="' + P[g] + '"/></svg>';
    }
    function knapp(g, href, gul) {
      var a = document.createElement("a");
      a.className = "knapp" + (gul ? "" : " neutral");
      a.href = href;
      a.innerHTML = ikon(g) + '<span class="butik-namn">' + (g === "ios" ? "App Store" : "Google Play") + "</span>";
      a.setAttribute("aria-label", "Hämta Halkvakt i " + (g === "ios" ? "App Store för iPhone" : "Google Play för Android"));
      return a;
    }
    var knappar = document.querySelectorAll('a.knapp[href*="apps.apple.com"], a.knapp[href*="play.google.com"]');
    for (var i = 0; i < knappar.length; i++) {
      var a = knappar[i];
      if (a.closest(".apppar") || a.querySelector("svg")) continue;
      var text = a.textContent;
      var g = a.getAttribute("data-plattform") || (/play\.google\.com/.test(a.href) || /Android/.test(text) ? "android" : /iPhone/.test(text) ? "ios" : "");
      if (g) { a.insertAdjacentHTML("afterbegin", ikon(g)); a.classList.add("butik"); continue; }
      var kod = (a.href.match(/[?&]ct=([^&]+)/) || [])[1] || "knapp";
      var playUrl = PLAY + "&referrer=" + encodeURIComponent("utm_source=halkvakt.se&utm_content=" + kod);
      var par = document.createElement("span");
      par.className = "apppar";
      var ios = knapp("ios", a.href, !android), and = knapp("android", playUrl, android);
      if (android) { par.appendChild(and); par.appendChild(ios); } else { par.appendChild(ios); par.appendChild(and); }
      a.parentNode.replaceChild(par, a);
    }
    // Tills sidmotorn skriver det själv: rutan bredvid knapparna ska inte säga bara iPhone.
    var rutor = document.querySelectorAll(".ladda p");
    for (var j = 0; j < rutor.length; j++) {
      if (/Gratis för iPhone(?! och Android)/.test(rutor[j].textContent))
        rutor[j].innerHTML = rutor[j].innerHTML.replace(/Gratis för iPhone(?! och Android)/, "Gratis för iPhone och Android");
    }
  } catch (e) {}
})();
