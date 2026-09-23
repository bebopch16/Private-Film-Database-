#!/bin/bash
# 电影工作台 —— 登录自动启动开关
# 用法:  ./autostart.sh on     开启(登录后自动起服务并常驻)
#        ./autostart.sh off    关闭
#        ./autostart.sh status 查看状态
#
# 说明: 用 launchd 用户级 LaunchAgent 实现, 不需要管理员权限。
#       开启后服务固定跑在 http://localhost:8080 —— origin 永远不变,
#       浏览器 IndexedDB 里的本地编辑因此不会因换地址而丢失。

LABEL=com.movieapp.local
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
PORT=8080

case "$1" in
  on)
    if [ ! -f "$PLIST" ]; then echo "缺少 $PLIST"; exit 1; fi
    launchctl bootout gui/$(id -u)/$LABEL 2>/dev/null
    if launchctl bootstrap gui/$(id -u) "$PLIST" 2>/dev/null; then
      echo "已开启: 登录后自动启动, 地址 http://localhost:$PORT"
    else
      echo "bootstrap 失败, 请手动在终端执行:"
      echo "  launchctl bootstrap gui/\$(id -u) $PLIST"
      exit 1
    fi
    ;;
  off)
    launchctl bootout gui/$(id -u)/$LABEL 2>/dev/null && echo "已关闭自动启动" || echo "原本未开启"
    ;;
  status)
    if curl -s --noproxy '*' -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/index.html"; then
      echo "服务运行中: http://localhost:$PORT"
    else
      echo "服务未运行"
    fi
    launchctl print gui/$(id -u)/$LABEL >/dev/null 2>&1 && echo "LaunchAgent: 已加载" || echo "LaunchAgent: 未加载"
    ;;
  *)
    echo "用法: $0 {on|off|status}"
    ;;
esac
