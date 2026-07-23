// ================================================================
// SERVICE WORKER — SeptaQuiz by Septech
// Version: 2.0 — Production ready
// Strategy: Cache-First static, Network-First API
// ================================================================

const CACHE_VERSION = 'sq-v2';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const API_CACHE     = `${CACHE_VERSION}-api`;

// Resources to pre-cache on install
const PRECACHE = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// ── INSTALL ──────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(PRECACHE).catch(e => {
        console.warn('[SW] Pre-cache partial fail:', e);
      }))
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE — clean old caches ──────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(k => k !== STATIC_CACHE && k !== API_CACHE)
          .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ── FETCH ────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  // Skip non-GET, chrome-extension, etc.
  if(req.method !== 'GET') return;
  if(!url.protocol.startsWith('http')) return;

  // API → Network first (always fresh data)
  if(url.pathname.startsWith('/api/') || url.pathname === '/health'){
    event.respondWith(networkFirst(req, API_CACHE));
    return;
  }

  // Fonts & avatars → Cache first (rarely change)
  if(url.hostname.includes('fonts.g') ||
     url.hostname.includes('ui-avatars') ||
     url.hostname.includes('fonts.gstatic')){
    event.respondWith(cacheFirst(req, STATIC_CACHE));
    return;
  }

  // Static assets → Cache first
  if(url.pathname.startsWith('/static/')){
    event.respondWith(cacheFirst(req, STATIC_CACHE));
    return;
  }

  // HTML pages → Network first with offline fallback
  event.respondWith(networkFirst(req, STATIC_CACHE));
});

// ── STRATEGIES ───────────────────────────────────────────────────
async function cacheFirst(req, cacheName) {
  const cached = await caches.match(req);
  if(cached) return cached;

  try {
    const res = await fetch(req);
    if(res.ok && res.status < 400){
      const cache = await caches.open(cacheName);
      cache.put(req, res.clone());
    }
    return res;
  } catch(err) {
    console.warn('[SW] Cache-first offline:', req.url);
    return new Response('Offline', { status: 503, headers: {'Content-Type':'text/plain'} });
  }
}

async function networkFirst(req, cacheName) {
  try {
    const res = await fetch(req, { credentials: 'same-origin' });
    if(res.ok && req.method === 'GET'){
      const cache = await caches.open(cacheName);
      cache.put(req, res.clone());
    }
    return res;
  } catch(err) {
    const cached = await caches.match(req);
    if(cached) return cached;

    // Return offline JSON for API calls
    if(req.url.includes('/api/')){
      return new Response(
        JSON.stringify({ error: 'Offline — check your connection', offline: true }),
        { status: 503, headers: {'Content-Type':'application/json'} }
      );
    }
    return new Response('Offline', { status: 503 });
  }
}
