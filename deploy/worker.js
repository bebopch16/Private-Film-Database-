/**
 * 电影工作台 · 云同步 API（与静态站点同源）
 * ============================================================
 * 设计原则
 *   · 只同步「overlay」这一个 JSON 块（用户本地编辑，约 80 KB）。
 *     烘焙基线（data.js / ratings_fyc.js / lb_data.js）随站点部署，不进云。
 *   · 存储用 Cloudflare KV 的单键 "overlay"，不建表、不写 SQL。
 *   · 鉴权用环境变量 SYNC_TOKEN（Bearer 令牌）。前端源码公开可见，
 *     该令牌的定位是「防止陌生人乱写我的数据」，不是账号体系 —— 单人自用足够。
 *   · 同一 origin 提供 API 与页面 → 无跨域问题，也不需要 CORS 头。
 *
 * 路由
 *   GET  /api/sync   读云端快照 → {v,stamp,at,device,payload} 或 {ok:true,empty:true}
 *   PUT  /api/sync   写云端快照（stamp / at 由服务端生成，客户端不能伪造时间）
 *   其他所有路径      交给静态资产（env.ASSETS）
 *
 * 部署要点
 *   · wrangler.toml 必须同时配置 [assets]（binding = "ASSETS"）与 [[kv_namespaces]]
 *   · 令牌用 `npx wrangler secret put SYNC_TOKEN` 写入，绝不写进本文件
 */

var KV_KEY = "overlay";                 // KV 里的唯一键
var MAX_BYTES = 8 * 1024 * 1024;        // 8 MB 上限：防误传超大文件把 KV 撑爆
var MAX_DEVICE = 40;                    // 设备标签最长长度

var JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  /* 云同步响应绝不能被任何中间层缓存 —— 否则「下载」会拿到旧副本 */
  "cache-control": "no-store, no-cache, must-revalidate",
  "pragma": "no-cache"
};

function jsonOut(obj, status) {
  return new Response(JSON.stringify(obj), { status: status || 200, headers: JSON_HEADERS });
}

/* 定长比较：避免 `===` 早退泄露前缀匹配长度。威胁模型很弱，但这样写是零成本的正确姿势。 */
function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  if (a.length !== b.length) return false;
  var diff = 0;
  for (var i = 0; i < a.length; i++) diff |= (a.charCodeAt(i) ^ b.charCodeAt(i));
  return diff === 0;
}

function isAuthed(req, env) {
  var h = req.headers.get("Authorization") || "";
  var m = /^Bearer\s+(\S+)\s*$/.exec(h);
  if (!m) return false;
  if (!env.SYNC_TOKEN) return false;
  /* 令牌在客户端做了 percent-encode 再放进 header —— 因为 HTTP 头只能承载 ISO-8859-1，
     若令牌含中文，原样塞进去 fetch 会直接抛 "String contains non ISO-8859-1 code point"，
     前端只能看到「网络不可达」这种完全指不出原因的报错。编码后任意字符的令牌都能用，
     且纯字母数字的令牌编码前后完全一样（与 wrangler secret 里存的值一致，便于人工核对）。 */
  var token;
  try { token = decodeURIComponent(m[1]); } catch (e) { return false; }
  return safeEqual(token, env.SYNC_TOKEN);
}

export default {
  async fetch(req, env) {
    var url = new URL(req.url);

    /* 只接管 /api/sync，其余一律交给静态站点（含 PWA 的 sw.js / manifest.json 等） */
    if (url.pathname !== "/api/sync") {
      if (!env.ASSETS || typeof env.ASSETS.fetch !== "function") {
        return new Response("ASSETS 绑定缺失：请检查 wrangler.toml 的 [assets] 配置", { status: 500 });
      }
      return env.ASSETS.fetch(req);
    }

    if (!env.SYNC_TOKEN) {
      return jsonOut({ ok: false, error: "服务端尚未配置同步令牌（SYNC_TOKEN）" }, 500);
    }
    if (!isAuthed(req, env)) {
      return jsonOut({ ok: false, error: "同步令牌不正确" }, 401);
    }

    /* ---------- 读云端快照 ---------- */
    if (req.method === "GET") {
      var raw = null;
      try { raw = await env.SYNC.get(KV_KEY); } catch (e) {
        return jsonOut({ ok: false, error: "读取云端失败：" + (e && e.message ? e.message : e) }, 502);
      }
      if (!raw) return jsonOut({ ok: true, empty: true });
      /* 直接回传原样字符串：保证「上传什么样、下载就什么样」 */
      return new Response(raw, { headers: JSON_HEADERS });
    }

    /* ---------- 写云端快照 ---------- */
    if (req.method === "PUT") {
      var body;
      try { body = await req.text(); } catch (e) {
        return jsonOut({ ok: false, error: "读取请求体失败" }, 400);
      }
      if (body.length > MAX_BYTES) {
        return jsonOut({ ok: false, error: "数据过大（超过 " + Math.round(MAX_BYTES / 1048576) + " MB）" }, 413);
      }
      var incoming;
      try { incoming = JSON.parse(body); } catch (e) {
        return jsonOut({ ok: false, error: "上传内容不是合法 JSON" }, 400);
      }
      if (!incoming || typeof incoming !== "object" || !incoming.payload || typeof incoming.payload !== "object") {
        return jsonOut({ ok: false, error: "上传内容缺少 payload 字段" }, 400);
      }

      var snap = {
        v: 1,
        stamp: Date.now(),                                  // 服务端时间，客户端不可伪造
        at: new Date().toISOString(),
        device: String(incoming.device || "").slice(0, MAX_DEVICE),
        payload: incoming.payload
      };
      var out = JSON.stringify(snap);
      try {
        await env.SYNC.put(KV_KEY, out);
      } catch (e) {
        return jsonOut({ ok: false, error: "写入云端失败：" + (e && e.message ? e.message : e) }, 502);
      }
      return jsonOut({ ok: true, stamp: snap.stamp, at: snap.at, size: out.length });
    }

    return jsonOut({ ok: false, error: "不支持的方法：" + req.method }, 405);
  }
};
