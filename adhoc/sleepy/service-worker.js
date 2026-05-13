// service-worker.js
self.addEventListener('install', event => {
    self.skipWaiting();
});
self.addEventListener('fetch', event => {
    // Let all requests go to the network
});
