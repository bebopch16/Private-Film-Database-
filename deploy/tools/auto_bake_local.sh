#!/bin/bash
# 电影工作台 —— 把浏览器里的本地编辑自动镜像回数据文件(安全网)
#
# 作用: 即使浏览器数据被清 / 换浏览器 / 忘了导出备份,
#       最近一次运行本脚本时的编辑也已固化进 data.js 与 ratings_fyc.js。
#
# 用法: ./auto_bake_local.sh          # 抽取 + 有变化就烘焙
#       ./auto_bake_local.sh force    # 忽略对比, 强制烘焙一次
#
# 说明:
#   * 只读浏览器 profile 的副本, 不改动真实 profile
#   * 用 --no-delete, 不把"删除"固化(避免误删被永久写死)
#   * localhost 与 127.0.0.1 是两个不同 origin(各自的 IndexedDB), 两个都会抽

set -u
APP="/Users/sean/WorkBuddy/2026-08-24-22-07-23/电影片单App"
EDGE="$HOME/Library/Application Support/Microsoft Edge/Default"
PORT=8080

NODE=/Users/sean/.workbuddy/binaries/node/versions/22.22.2-2/bin/node
export NODE_PATH=/Users/sean/.workbuddy/binaries/node/workspace/node_modules
PY=/Users/sean/.workbuddy/binaries/python/envs/default/bin/python

mkdir -p "$APP/backups"
CHANGED=0

# 1) 确保本地服务在跑(抽取需要同源页面)
if ! curl -s --noproxy '*' -o /dev/null --max-time 2 "http://localhost:$PORT/index.html"; then
  ( cd "$APP/deploy" && nohup /usr/bin/python3 -m http.server "$PORT" --bind 127.0.0.1 >/tmp/movieapp-local.log 2>&1 & )
  sleep 2
fi

# 2) 逐个 origin 抽取并烘焙
for HOST in localhost 127.0.0.1; do
  ORIGIN="http://$HOST:$PORT"
  # origin 对应的 IndexedDB 目录名: localhost -> http_localhost_8080, 127.0.0.1 -> http_127.0.0.1_8080
  if [ "$HOST" = "localhost" ]; then DBDIR="http_localhost_${PORT}.indexeddb.leveldb";
  else DBDIR="http_127.0.0.1_${PORT}.indexeddb.leveldb"; fi

  [ -d "$EDGE/IndexedDB/$DBDIR" ] || continue

  TMP=$(mktemp -d)
  mkdir -p "$TMP/Default/IndexedDB"
  cp -R "$EDGE/IndexedDB/$DBDIR" "$TMP/Default/IndexedDB/" 2>/dev/null
  [ -d "$EDGE/Local Storage" ] && cp -R "$EDGE/Local Storage" "$TMP/Default/" 2>/dev/null

  SNAP="$APP/backups/local_overlay_${HOST}.json"
  LAST="$APP/backups/local_overlay_${HOST}_last.json"

  if "$NODE" "$APP/tools/harvest_local_overlay.js" "$ORIGIN" "$TMP" "$SNAP" >/tmp/harvest_${HOST}.log 2>&1; then
    echo "[$HOST] $(cat /tmp/harvest_${HOST}.log)"
    if [ "${1:-}" = "force" ] || [ ! -f "$LAST" ] || ! cmp -s "$SNAP" "$LAST"; then
      cp "$SNAP" "$LAST"
      echo "[$HOST] 检测到新的本地编辑, 烘焙中…"
      "$PY" "$APP/tools/bake_overlay_into_datafiles.py" "$SNAP" --no-delete | tail -3
      CHANGED=1
    else
      echo "[$HOST] 无变化, 跳过"
    fi
  else
    echo "[$HOST] 该 origin 暂无本地编辑数据"
  fi
  rm -rf "$TMP"
done

if [ "$CHANGED" = "1" ]; then
  cp "$APP/data.js" "$APP/ratings_fyc.js" "$APP/deploy/"
  echo "已同步到 deploy/。刷新浏览器即可看到(数据已固化进站点文件)"
fi
