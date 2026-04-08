/**
 * Gemma Medical -- Service Worker for PWA Offline Caching.
 *
 * Strategy:
 *   - Static assets: cache-first (fast loads, update in background)
 *   - API calls: network-first with offline fallback
 *   - Old caches cleaned on activate
 */

const CACHE_NAME = "gemma-medical-v1";

const STATIC_ASSETS = [
    "/",
    "/index.html",
    "/css/styles.css",
    "/css/ai-assistant.css",
    "/js/ai-assistant.js",
    "/manifest.json",
    "/assets/icon-192.svg",
    "/assets/icon-512.svg",
];

/**
 * Install: pre-cache all static assets.
 */
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log("[SW] Caching static assets");
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

/**
 * Activate: clean up old caches from previous versions.
 */
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => {
                        console.log("[SW] Deleting old cache:", name);
                        return caches.delete(name);
                    })
            );
        })
    );
    self.clients.claim();
});

/**
 * Fetch: route requests based on type.
 *   - /api/* : network-first with offline fallback JSON
 *   - Everything else: cache-first with network fallback
 */
self.addEventListener("fetch", (event) => {
    const url = new URL(event.request.url);

    // API calls: network-first
    if (url.pathname.startsWith("/api/")) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    return response;
                })
                .catch(() => {
                    return new Response(
                        JSON.stringify({
                            error: "offline",
                            message: "You are offline. Please reconnect to use AI features.",
                        }),
                        {
                            status: 503,
                            headers: { "Content-Type": "application/json" },
                        }
                    );
                })
        );
        return;
    }

    // Static assets: cache-first
    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) {
                // Return cached version, update cache in background
                fetch(event.request).then((response) => {
                    if (response && response.ok) {
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, response);
                        });
                    }
                });
                return cached;
            }

            // Not in cache: fetch from network and cache it
            return fetch(event.request).then((response) => {
                if (response && response.ok) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            });
        })
    );
});
