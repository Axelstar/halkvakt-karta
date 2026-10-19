/* Halkvakt besöksräknare: en rad per sidvisning, utan kakor, IP eller användar-id.
   Skickar bara sidans sökväg, varifrån besökaren kom (domänen), en eventuell ?r=-kod och mobil/dator. */
(function () {
  try {
    if (location.hostname !== "halkvakt.se" || navigator.webdriver) return;
    var q = new URLSearchParams(location.search);
    var ref = "";
    if (document.referrer) {
      var h = new URL(document.referrer).hostname;
      ref = h === location.hostname ? "(intern)" : h;
    }
    var d = JSON.stringify({
      p: location.pathname,
      r: ref,
      k: q.get("r") || q.get("utm_source") || "",
      m: /Mobi|Android|iPhone/i.test(navigator.userAgent) ? "m" : "d"
    });
    var url = "https://xmpfztykhyvhmrzsnjrc.supabase.co/functions/v1/besok";
    if (!(navigator.sendBeacon && navigator.sendBeacon(url, d))) {
      fetch(url, { method: "POST", body: d, keepalive: true, mode: "no-cors" });
    }
  } catch (e) {}
})();
