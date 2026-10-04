// sw.js - Service Worker for Offline PWA Support
const CACHE_NAME = 'ee-exam-cache-v2.1';
const CORE_ASSETS = [
  './index.html',
  './manifest.json',
  './dashboard-data.js?v=dev',
  './solutions-bundle.js?v=dev',
  './national-exams-data.js?v=dev',
  './national-solutions-bundle.js?v=dev',
  './libs/katex.min.css',
  './libs/katex.min.js',
  './libs/auto-render.min.js',
  './libs/marked.min.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(CORE_ASSETS).catch(err => {
        console.warn('SW: pre-caching partial assets failed', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }
        const toCache = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, toCache);
        });
        return response;
      }).catch(() => cached);
    })
  );
});
