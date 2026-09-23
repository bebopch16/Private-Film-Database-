# -*- coding: utf-8 -*-
"""
build_countries.py —— 把可手动编辑的来源 countries_source.txt 转换成程序可用格式。

输入 : countries_source.txt  (TSV: iso \t 中文 \t 英文, # 开头为注释)
输出 : countries.js          (window.COUNTRY_LIST = [{iso,zh,en,flag}, ...])
       flag 字段由 iso 两位字母确定性派生为旗帜 emoji, 无需联网/外部数据。

用法 :
    python3 tools/build_countries.py
改完 countries_source.txt 后重跑即可。
"""
import os, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "countries_source.txt")
OUT = os.path.join(BASE, "countries.js")


def flag_of(iso2):
    """iso alpha-2 -> 旗帜 emoji (区域指示符)"""
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in iso2.upper())


def main():
    rows = []
    with open(SRC, "r", encoding="utf-8") as f:
        for ln, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                print(f"! 跳过第 {ln} 行(字段不足3): {line!r}")
                continue
            iso, zh, en = parts[0].strip(), parts[1].strip(), parts[2].strip()
            if not iso or not zh:
                continue
            rows.append({"iso": iso.upper(), "zh": zh, "en": en, "flag": flag_of(iso)})

    if not rows:
        raise SystemExit("没有解析到任何国家行, 请检查 countries_source.txt")

    # 用 iso 去重保序
    seen = set()
    dedup = []
    for r in rows:
        if r["iso"] in seen:
            print(f"! 重复 iso 已合并: {r['iso']} ({r['zh']})")
            continue
        seen.add(r["iso"])
        dedup.append(r)

    js = "// AUTO-GENERATED from countries_source.txt — 请勿手改本文件; 改 .txt 后运行 tools/build_countries.py\n"
    js += "window.COUNTRY_LIST = " + json.dumps(dedup, ensure_ascii=False, indent=0) + ";\n"
    js += "// zh -> iso 反查表(供 flagHtml 兜底显示旗帜)\n"
    zh2iso = {r["zh"]: r["iso"] for r in dedup}
    js += "window.COUNTRY_ZH2ISO = " + json.dumps(zh2iso, ensure_ascii=False, indent=0) + ";\n"

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(js)

    print(f"WROTE {OUT}  ({len(dedup)} 个国家/地区)")


if __name__ == "__main__":
    main()
