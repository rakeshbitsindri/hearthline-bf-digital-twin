(function () {
  var collect = window.__HEARTHLINE_VISIT_ENDPOINT__ || "";
  if (!collect) {
    if (location.hostname.endsWith("github.io")) return;
    collect = location.origin + "/visits/collect";
  }
  var payload = JSON.stringify({
    path: location.pathname || "/",
    site: location.hostname,
    ref: (document.referrer || "").slice(0, 180),
  });
  fetch(collect, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload,
    keepalive: true,
    mode: "cors",
  }).catch(function () {});
})();
