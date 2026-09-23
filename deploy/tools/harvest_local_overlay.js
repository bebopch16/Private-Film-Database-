#!/usr/bin/env node
/**
 * 从浏览器 profile 里读出指定 origin 的本地编辑(overlay), 存成 JSON。
 *
 * 用法:
 *   NODE_PATH=<playwright 模块目录> node harvest_local_overlay.js <origin> <临时profile目录> <输出json>
 *
 * 例:
 *   node harvest_local_overlay.js http://localhost:8080 /tmp/xxx /path/snapshot.json
 *
 * 原理: 先把目标 origin 的 IndexedDB 目录拷到一个临时 profile(不动真实 profile),
 *       再用 Playwright 打开该 origin, 通过 IndexedDB API 读出 movieApp/kv/overlay。
 *       页面返回 404 也没关系 —— 只要 origin 一致就能读到该 origin 的存储。
 */
const { chromium } = require('playwright-core');
const fs = require('fs');

const ORIGIN = process.argv[2];
const PROFILE = process.argv[3];
const OUT = process.argv[4];

if (!ORIGIN || !PROFILE || !OUT) {
  console.log('用法: node harvest_local_overlay.js <origin> <profileDir> <out.json>');
  process.exit(1);
}

(async () => {
  const ctx = await chromium.launchPersistentContext(PROFILE, {
    channel: 'msedge', headless: true,
    args: ['--no-proxy-server', '--no-first-run', '--no-default-browser-check'],
  });
  const page = await ctx.newPage();
  let navOk = true;
  await page.goto(ORIGIN, { waitUntil: 'domcontentloaded' }).catch(() => { navOk = false; });

  const res = await page.evaluate(async () => {
    const DB = 'movieApp', STORE = 'kv', KEY = 'overlay';
    function idbGet() {
      return new Promise((resolve, reject) => {
        const rq = indexedDB.open(DB);
        rq.onerror = () => reject(rq.error);
        rq.onsuccess = () => {
          const db = rq.result;
          if (!db.objectStoreNames.contains(STORE)) return resolve(null);
          const g = db.transaction(STORE, 'readonly').objectStore(STORE).get(KEY);
          g.onsuccess = () => resolve(g.result || null);
          g.onerror = () => reject(g.error);
        };
      });
    }
    let d = null, src = '';
    try { d = await idbGet(); if (d) src = 'IndexedDB'; } catch (e) {}
    if (!d) {
      try {
        const m = localStorage.getItem('movieApp_overlay_mirror');
        if (m) { d = JSON.parse(m); src = 'localStorage'; }
      } catch (e) {}
    }
    return { d, src };
  });

  await ctx.close();

  if (!res.d) {
    console.log('NO_DATA');
    process.exit(2);
  }
  fs.writeFileSync(OUT, JSON.stringify(res.d, null, 1), 'utf8');
  const d = res.d;
  console.log('OK ' + res.src +
    ' newFilms=' + (d.newFilms || []).length +
    ' ratings=' + Object.keys(d.ratings || {}).length +
    ' films=' + Object.keys(d.films || {}).length +
    ' fyc=' + Object.keys(d.fyc || {}).length +
    ' deleted=' + Object.keys(d.deleted || {}).length);
})();
