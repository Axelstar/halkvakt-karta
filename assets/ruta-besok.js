/* Räknar rutans visningar hos tidningarna (Axel 23/10). Samma räknare som besok.js och samma regler:
   inga kakor, ingen IP, inget användar-id. En rad per visning med rutans adress, sajten den visas på
   (bara domänen) och mobil/dator. Sammanställs under "Rutorna hos tidningarna" på statistik.html.

   ruta/<tidning>/:  <script src="/assets/ruta-besok.js" data-sida="/ruta/nwt/"></script>
   ruta.html:        <script src="assets/ruta-besok.js" data-sida="/ruta.html"></script>  (räknas bara när någon
                     bäddat in ruta.html direkt; inuti våra egna sidor och ruta/<tidning>/ räknas den inte) */
(function () {
  try {
    var s = document.currentScript, sida = s && s.getAttribute("data-sida");
    if (!sida || location.hostname !== "halkvakt.se" || navigator.webdriver) return;
    var inramad = true;
    try { inramad = window.top !== window; } catch (e) {}
    // Sajten närmast utanför rutan: ancestorOrigins där webbläsaren har det, annars referrer.
    var vard = "";
    try { if (location.ancestorOrigins && location.ancestorOrigins.length) vard = new URL(location.ancestorOrigins[0]).hostname; } catch (e) {}
    try { if (!vard && document.referrer) vard = new URL(document.referrer).hostname; } catch (e) {}
    var egen = /(^|\.)halkvakt\.se$/.test(vard);
    var kod = "";
    if (sida === "/ruta.html") {
      if (!inramad || egen) return;                       // bara direkt inbäddad hos någon annan
      kod = (new URLSearchParams(location.search).get("namn") || "halkvakt").slice(0, 40);
    }
    var r = !inramad ? "" : egen ? "(intern)" : (vard || "(inbaddad)");
    var o = { p: sida, r: r, k: kod, m: /Mobi|Android|iPhone/i.test(navigator.userAgent) ? "m" : "d" };
    try { if (localStorage.getItem("hv-oss") === "1") o.o = 1; } catch (e) {}   // våra egna enheter (se besok.js)
    var d = JSON.stringify(o);
    var url = "https://xmpfztykhyvhmrzsnjrc.supabase.co/functions/v1/besok";
    if (!(navigator.sendBeacon && navigator.sendBeacon(url, d))) {
      fetch(url, { method: "POST", body: d, keepalive: true, mode: "no-cors" });
    }
  } catch (e) {}
})();
