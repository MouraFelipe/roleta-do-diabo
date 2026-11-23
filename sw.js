/* offline: guarda o jogo e as fontes; o online precisa de internet */
const C = "roleta-v4", CORE = ["./", "index.html", "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(C).then(c => c.addAll(CORE))); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  if (u.origin === location.origin) {      // rede primeiro (pega atualizações), cache se estiver offline
    e.respondWith(fetch(e.request).then(r => { const cp = r.clone(); caches.open(C).then(c => c.put(e.request, cp)); return r; }).catch(() => caches.match(e.request, {ignoreSearch:true}).then(r => r || caches.match("index.html"))));
  } else if (/fonts\.(googleapis|gstatic)\.com|unpkg\.com/.test(u.host)) {   // fontes e PeerJS: cache primeiro
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(n => { const cp = n.clone(); caches.open(C).then(c => c.put(e.request, cp)); return n; })));
  }
});
