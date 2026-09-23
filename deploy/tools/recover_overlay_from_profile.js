const { chromium } = require('playwright-core');
const fs = require('fs');
const OLD_ORIGIN = 'https://08ff2a7b04e44edbb0367a2c7e38995b.app.workbuddy.link/';
const OUT = '/Users/sean/WorkBuddy/2026-08-25-11-55-07/recovered_overlay.json';

(async () => {
  const ctx = await chromium.launchPersistentContext('/tmp/edgerecover', {
    channel: 'msedge',
    headless: true,
    args: ['--no-first-run', '--no-default-browser-check'],
  });
  const page = await ctx.newPage();
  await page.goto(OLD_ORIGIN, { waitUntil: 'domcontentloaded' }).catch(e => console.log('goto warn:', e.message));
  console.log('origin page loaded, url =', page.url());

  const result = await page.evaluate(async () => {
    const DB = 'movieApp', STORE = 'kv', KEY = 'overlay';
    function idbGet() {
      return new Promise((resolve, reject) => {
        // 不指定版本，避免版本不匹配报错
        const rq = indexedDB.open(DB);
        rq.onerror = () => reject(rq.error);
        rq.onupgradeneeded = () => { /* 不应发生 */ };
        rq.onsuccess = () => {
          const db = rq.result;
          if (!db.objectStoreNames.contains(STORE)) return resolve(null);
          try {
            const g = db.transaction(STORE, 'readonly').objectStore(STORE).get(KEY);
            g.onsuccess = () => resolve(g.result || null);
            g.onerror = () => reject(g.error);
          } catch (e) { reject(e); }
        };
      });
    }
    let data = null, src = '';
    try { data = await idbGet(); if (data) src = 'IndexedDB'; } catch (e) { console.warn('idb err', e && e.message); }
    if (!data) {
      try {
        const m = localStorage.getItem('movieApp_overlay_mirror');
        if (m) { data = JSON.parse(m); src = 'localStorage mirror'; }
      } catch (e) {}
    }
    return { data, src };
  });

  if (!result.data) {
    console.log('NO DATA FOUND');
    await ctx.close();
    process.exit(1);
  }

  const d = result.data;
  console.log('来源:', result.src);
  console.log('本地新增影片 newFilms:', (d.newFilms || []).length);
  console.log('本地评分 ratings:', Object.keys(d.ratings || {}).length);
  console.log('影片覆盖 films:', Object.keys(d.films || {}).length);
  console.log('表彰 fyc:', Object.keys(d.fyc || {}).length);
  console.log('导演元数据 directorMeta:', Object.keys(d.directorMeta || {}).length);
  console.log('译名合并 dirAlias:', Object.keys(d.dirAlias || {}).length);
  console.log('已删除 deleted:', Object.keys(d.deleted || {}).length);

  fs.writeFileSync(OUT, JSON.stringify(d, null, 1), 'utf8');
  console.log('已保存:', OUT, fs.statSync(OUT).size, 'bytes');
  await ctx.close();
})();
