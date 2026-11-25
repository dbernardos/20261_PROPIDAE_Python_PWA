const CACHE_NAME = 'sea-pwa-v1';

const HOSTNAME_WHITELIST = [
  self.location.hostname,
  'fonts.gstatic.com',
  'fonts.googleapis.com',
  'cdn.jsdelivr.net',
];

const IGNORED_PREFIXES = ['/admin/', '/login/', '/logout/', '/chaining/'];

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Ignora rotas de autenticação, admin, raiz e domínios fora da whitelist
  const isIgnoredPath =
    url.pathname === '/' ||
    IGNORED_PREFIXES.some((prefix) => url.pathname.startsWith(prefix));

  if (isIgnoredPath || !HOSTNAME_WHITELIST.includes(url.hostname)) return;

  const isDocument =
    request.mode === 'navigate' || request.destination === 'document';

  if (isDocument) {
    // Páginas HTML: Network First (valida sessão/CSRF no Django)
    event.respondWith(
      fetch(request, { cache: 'no-store' })
        .then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // Arquivos estáticos (CSS, JS, imagens, fontes): Stale-While-Revalidate
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) =>
      cache.match(request).then((cached) => {
        const fetched = fetch(request)
          .then((response) => {
            if (response.ok) {
              cache.put(request, response.clone());
            }
            return response;
          })
          .catch(() => cached);

        return cached || fetched;
      })
    )
  );
});