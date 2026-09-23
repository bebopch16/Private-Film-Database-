/* Service Worker: 我的电影工作台
 * 策略: 可更新的资源(index.html/data.js/ratings_fyc.js)网络优先, 离线回退缓存;
 *       静态资源(lib/assets)缓存优先, 加速二次打开并支持离线查看。
 */
var CACHE = "movie-app-v11";  /* v11: 全站图标改回 Lucide(开源,ISC) 内联 SVG, 移除 morphicons 依赖(2026-09-23) */
/* 注意: 正则不能只用 $ 结尾 —— 带查询串(data.js?v=...)时必须仍视为"可更新资源"走网络优先 */
var NETWORK_FIRST = /(index\.html|data\.js|ratings_fyc\.js|lb_data\.js|countries\.js)(\?|$)/;
var STATIC_ASSETS = [
  "./",
  "./index.html",
  "./data.js?v=20260909b",
  "./ratings_fyc.js?v=20260914b",
  "./lb_data.js?v=20260914a",
  "./lib/xlsx.full.min.js",
  "./assets/favicon.svg",
  "./assets/favicon.ico",
  "./assets/apple-touch-icon.png",
  "./assets/favicon-192x192.png",
  "./assets/favicon-512x512.png",
  "./manifest.json"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) { return c.addAll(STATIC_ASSETS); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  var url = e.request.url;

  // TMDb 剧照(image.tmdb.org): 缓存优先, 显示过剧照的影片二次打开免网络请求
  if (url.indexOf("image.tmdb.org") >= 0) {
    e.respondWith(
      caches.match(e.request).then(function (hit) {
        if (hit) return hit;
        return fetch(e.request).then(function (res) {
          if (res) {
            var cl = res.clone();
            caches.open(CACHE).then(function (c) { c.put(e.request, cl); });
          }
          return res;
        }).catch(function () { return hit; });
      })
    );
    return;
  }

  // 导航请求(打开页面/裸域/深链)一律网络优先: 保证部署更新立即生效, 离线回退缓存
  if (e.request.mode === "navigate" || NETWORK_FIRST.test(url)) {
    /* v25.18: 网关偶发 5xx(如 502) —— fetch 收到 5xx 不算网络错误、不会走 catch,
       必须显式处理: 最多尝试 3 次(间隔 350ms), 全部失败且有本地缓存则回退缓存(老用户无感) */
    /* v27.15: 网关对无版本号 URL 按 Last-Modified 做启发式缓存(可能几小时不更新),
       因此一律 fetch 带随机参数的副本(swb=时间戳)绕过边缘缓存; 结果以"原始 URL"入缓存保离线可用。 */
    var waitMs = function (ms) { return new Promise(function (done) { setTimeout(done, ms); }); };
    var bustUrl = function (u) { return u + (u.indexOf("?") >= 0 ? "&" : "?") + "swb=" + Date.now(); };
    var tryFetch = function (n) {
      return fetch(bustUrl(e.request.url)).then(function (res) {
        if (res && res.status === 200) {
          var cl = res.clone();
          caches.open(CACHE).then(function (c) {
            c.put(e.request, cl);
            if (e.request.mode === "navigate") c.put("./index.html", res.clone());
          });
          return res;
        }
        if (res && res.status >= 500 && n > 0) {
          return waitMs(350).then(function () { return tryFetch(n - 1); });
        }
        return caches.match(e.request).then(function (hit) { return hit || res; });
      }).catch(function () {
        if (n > 0) return waitMs(350).then(function () { return tryFetch(n - 1); });
        return caches.match(e.request);
      });
    };
    e.respondWith(tryFetch(2));
    return;
  }

  e.respondWith(
    caches.match(e.request).then(function (hit) {
      if (hit) return hit;
      return fetch(e.request).then(function (res) {
        if (res && res.status === 200 && res.type === "basic") {
          var cl = res.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, cl); });
        }
        return res;
      }).catch(function () {
        if (e.request.mode === "navigate") return caches.match("./index.html");
      });
    })
  );
});
