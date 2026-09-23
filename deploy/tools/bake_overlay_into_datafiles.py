#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把本地 overlay(浏览器 IndexedDB 里的用户编辑) 烘焙进基础数据文件
data.js (window.MOVIE_DATA.movies) 与 ratings_fyc.js (window.RATINGS / window.FYC)。

目的: 用户数据不再只存在浏览器里 —— 一旦网址/域名变更导致 IndexedDB 失效,
      数据仍然随站点一起存在。

烘焙逻辑严格复刻 app 的 effectiveFilms(), 保证结果一致且幂等:
  - newFilms 追加进基础列表
  - 与 newFilms 同 key 的基础条目跳过(避免重复)
  - deleted 标记的基础条目移除
  - films 覆盖合并进基础条目
评分/表彰: 按 key 合并, 已存在则覆盖字段, 不存在则新增。
"""
import json, re, sys, shutil, os, time

BASE = "/Users/sean/WorkBuddy/2026-08-24-22-07-23/电影片单App/"
OVERLAY = sys.argv[1] if len(sys.argv) > 1 else "/Users/sean/WorkBuddy/2026-08-25-11-55-07/recovered_overlay.json"
BAK = BASE + "backups/pre_bake_" + time.strftime("%Y%m%d_%H%M%S")
os.makedirs(BAK, exist_ok=True)

for f in ("data.js", "ratings_fyc.js"):
    shutil.copy2(BASE + f, BAK + "/" + f)
print("已备份到:", BAK)

# ---------- 读取 ----------
djs = open(BASE + "data.js", encoding="utf-8").read()
mdata = json.loads(re.search(r'window\.MOVIE_DATA\s*=\s*(\{.*\})\s*;?\s*$', djs, re.S).group(1))
movies = mdata["movies"]

rjs = open(BASE + "ratings_fyc.js", encoding="utf-8").read()
RATINGS = json.loads(re.search(r'window\.RATINGS\s*=\s*(\[.*?\])\s*;?\s*(?=window\.|$)', rjs, re.S).group(1))
FYC = json.loads(re.search(r'window\.FYC\s*=\s*(\[.*?\])\s*;?\s*(?=window\.|$)', rjs, re.S).group(1))

ov = json.load(open(OVERLAY, encoding="utf-8"))
newFilms = ov.get("newFilms", [])
ovFilms = ov.get("films", {})
deleted = ov.get("deleted", {}) or {}
if "--no-delete" in sys.argv:
    # 自动烘焙场景: 不把"删除"固化进基础文件, 避免误删被永久写死
    deleted = {}
ovRatings = ov.get("ratings", {}) or {}
ovFyc = ov.get("fyc", {}) or {}
mergeMap = ov.get("merge", {}) or {}

def resolve(k):
    seen, cur = set(), k
    while mergeMap.get(cur) and cur not in seen:
        seen.add(cur); cur = mergeMap[cur]
    return cur
ovFilms = {resolve(k): v for k, v in ovFilms.items()}

print("原始: movies=%d  RATINGS=%d  FYC=%d" % (len(movies), len(RATINGS), len(FYC)))
print("overlay: newFilms=%d films覆盖=%d deleted=%d ratings=%d fyc=%d"
      % (len(newFilms), len(ovFilms), len(deleted), len(ovRatings), len(ovFyc)))

# ---------- 复刻 effectiveFilms ----------
def bkey(m):
    return "%s|%s" % (m.get("year"), m.get("title"))

cnt = {}
for m in list(movies) + list(newFilms):
    cnt.setdefault(bkey(m), set()).add(m.get("director") or "")
DUP = {b for b, v in cnt.items() if len(v) > 1}

def film_key(m):
    b = bkey(m)
    return b + "|" + str(m.get("director") or "") if b in DUP else b

nfKeys = {film_key(nf) for nf in newFilms}
out = []
removed_deleted, skipped_dup = 0, 0
for m in movies:
    k = film_key(m)
    if deleted.get(k):
        removed_deleted += 1
        continue
    if k in nfKeys:
        skipped_dup += 1
        continue
    o = ovFilms.get(k)
    out.append({**m, **o} if o else m)
out.extend(newFilms)
print("片单烘焙: 删除标记移除=%d  与新增重复跳过=%d  最终=%d" % (removed_deleted, skipped_dup, len(out)))

# key -> movie, 供评分/表彰补全导演等信息
movByKey = {film_key(m): m for m in out}

# ---------- 合并评分 ----------
added_r, merged_r = 0, 0
for k, v in ovRatings.items():
    k = resolve(k)
    year_s, _, title = k.partition("|")
    try:
        year = int(year_s)
    except Exception:
        year = v.get("year")
    hit = None
    for r in RATINGS:
        rk = [resolve(x) for x in (r.get("filmKeys") or [])]
        rt = "%s|%s" % (r.get("year"), r.get("title"))
        if rt == k or k in rk:
            hit = r
            break
    if hit:
        for f in ("w", "t", "d", "score", "ratedAt", "genre", "review"):
            if v.get(f) is not None:
                hit[f] = v[f]
        merged_r += 1
    else:
        mv = movByKey.get(k, {})
        RATINGS.append({
            "year": year,
            "title": title,
            "director": mv.get("director", ""),
            "w": v.get("w"), "t": v.get("t"), "d": v.get("d"),
            "score": v.get("score"),
            "ratedAt": v.get("ratedAt", ""),
            "genre": v.get("genre", ""),
            "review": v.get("review", ""),
            "filmKeys": [k],
        })
        added_r += 1
print("评分烘焙: 更新=%d  新增=%d  最终=%d" % (merged_r, added_r, len(RATINGS)))

# ---------- 合并表彰 ----------
added_f, merged_f = 0, 0
for k, v in ovFyc.items():
    k = resolve(k)
    year_s, _, title = k.partition("|")
    try:
        year = int(year_s)
    except Exception:
        year = v.get("year")
    hit = None
    for f in FYC:
        fk = [resolve(x) for x in (f.get("filmKeys") or [])]
        ft = "%s|%s" % (f.get("year"), f.get("title"))
        if ft == k or k in fk:
            hit = f
            break
    if hit:
        if v.get("cats") is not None:
            hit["cats"] = v["cats"]
        if v.get("region"):
            hit["region"] = v["region"]
        merged_f += 1
    else:
        FYC.append({
            "year": year,
            "region": v.get("region", ""),
            "title": title,
            "cats": v.get("cats", []),
            "filmKeys": [k],
        })
        added_f += 1
print("表彰烘焙: 更新=%d  新增=%d  最终=%d" % (merged_f, added_f, len(FYC)))

# ---------- 写回 ----------
mdata["movies"] = out
with open(BASE + "data.js", "w", encoding="utf-8") as f:
    f.write("/* 由 parse_excel.py + enrich/merge.py 自动生成, v25 经 enrich/v25_final2.py 修正 —— 请勿手改。\n"
            "   v27.15: 已烘焙并入用户本地编辑(newFilms/films 覆盖/deleted), 使数据随站点持久存在。 */\n")
    f.write("window.MOVIE_DATA = ")
    f.write(json.dumps(mdata, ensure_ascii=False, indent=1))
    f.write(";\n")

with open(BASE + "ratings_fyc.js", "w", encoding="utf-8") as f:
    f.write("/* 评分与表彰数据: 由 enrich/build_ratings_fyc.py 生成 + 人工补充 —— 请勿手改。\n"
            "   v27.15: 已烘焙并入用户本地评分与表彰。 */\n")
    f.write("window.RATINGS = ")
    f.write(json.dumps(RATINGS, ensure_ascii=False, separators=(",", ":")))
    f.write(";\nwindow.FYC = ")
    f.write(json.dumps(FYC, ensure_ascii=False, separators=(",", ":")))
    f.write(";\n")

# ---------- 校验 ----------
d2 = json.loads(re.search(r'window\.MOVIE_DATA\s*=\s*(\{.*\})\s*;?\s*$',
                          open(BASE + "data.js", encoding="utf-8").read(), re.S).group(1))
r2 = open(BASE + "ratings_fyc.js", encoding="utf-8").read()
R2 = json.loads(re.search(r'window\.RATINGS\s*=\s*(\[.*?\])\s*;?\s*(?=window\.|$)', r2, re.S).group(1))
F2 = json.loads(re.search(r'window\.FYC\s*=\s*(\[.*?\])\s*;?\s*(?=window\.|$)', r2, re.S).group(1))
print("写回校验: movies=%d RATINGS=%d FYC=%d  (JSON 可解析 OK)" % (len(d2["movies"]), len(R2), len(F2)))

for t in ("烈火战车", "蔷薇修剪术", "盒子里的羊"):
    inm = sum(1 for m in d2["movies"] if m.get("title") == t)
    inr = sum(1 for r in R2 if r.get("title") == t)
    print("  校验 %s: 片单=%d 评分=%d" % (t, inm, inr))
