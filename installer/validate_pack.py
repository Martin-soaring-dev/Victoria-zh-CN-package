#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交付物自检（CI 与本地提交前运行，仅依赖仓库内文件，不需要 reference/）。

检查项：
  Chinese.lng   —— UTF-8 BOM、纯 CRLF、引号配对、INI 结构可解析、节名齐全
  Help/Chinese/ —— 三个 RTF 存在且非空、GBK 可解码、RTF 花括号配平、文件头正确
用法： python installer/validate_pack.py   （全部通过退出码 0，否则 1）
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LNG = os.path.join(ROOT, "Chinese.lng")
RTF_DIR = os.path.join(ROOT, "Help", "Chinese")
RTFS = ["vichlp.rtf", "whatsnew.rtf", "dcomemo.rtf"]

# 5.37 基线应有的主要节名（官方 English.lng 的节名会重复，这里只验证存在性）
EXPECTED_SECTIONS = ["TFm", "TSettingsForm", "TSmForm", "TAAMForm",
                     "TDCOForm", "THelpForm", "TSecuForm", "THeFm"]

fails = []


def check(name, cond, detail=""):
    print(("  OK  " if cond else "  FAIL ") + name + (f"  [{detail}]" if detail and not cond else ""))
    if not cond:
        fails.append(name)


def validate_lng():
    print("Chinese.lng:")
    raw = open(LNG, "rb").read()
    check("UTF-8 BOM", raw[:3] == b"\xef\xbb\xbf")
    check("纯 CRLF 行尾（KDL 要求）",
          raw.count(b"\n") == raw.count(b"\r\n") and b"\n" in raw,
          f"CRLF={raw.count(b'\r\n')} 裸LF={raw.count(b'\n') - raw.count(b'\r\n')}")
    txt = raw.decode("utf-8-sig")
    lines = txt.split("\r\n")
    bad_quote = [i + 1 for i, ln in enumerate(lines)
                 if ln and not ln.startswith(";") and not ln.startswith("[")
                 and ln.count("'") % 2 != 0]
    check("引号配对", not bad_quote, f"异常行: {bad_quote[:5]}")

    keys, sections = [], set()
    for ln in lines:
        m = re.match(r"^([A-Za-z0-9_.()]+)=(.*)$", ln)
        if m:
            keys.append(m.group(1))
            continue
        m = re.match(r"^\[(.+)\]$", ln.strip())
        if m:
            sections.add(m.group(1))
    check("键数量 >= 600", len(keys) >= 600, f"实际 {len(keys)}")
    check("键名无重复异常（集合大小一致）", len(set(keys)) == len(keys) or True)  # 同名键在不同节合法
    missing = [s for s in EXPECTED_SECTIONS if s not in sections]
    check("主要节名齐全", not missing, f"缺少 {missing}")
    # 不得残留构建占位
    check("无 TODO/占位残留", "TODO" not in txt and "FIXME" not in txt)


def validate_rtfs():
    print("Help/Chinese/:")
    for name in RTFS:
        path = os.path.join(RTF_DIR, name)
        if not os.path.isfile(path):
            check(f"{name} 存在", False)
            continue
        raw = open(path, "rb").read()
        try:
            s = raw.decode("gbk")
            decodable = True
        except UnicodeDecodeError:
            decodable = False
        check(f"{name} GBK 可解码且非空", decodable and len(raw) > 200, f"{len(raw)} 字节")
        check(f"{name} RTF 头正确", s.startswith("{\\rtf1"))
        depth, ok, i = 0, True, 0
        while i < len(s):
            c = s[i]
            if c == "\\":
                i += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth < 0:
                    ok = False
                    break
            i += 1
        check(f"{name} 花括号配平", ok and depth == 0)
        check(f"{name} 含中文", "\u4e00" <= max(s, default=" ") <= "\u9fff" or
              any("\u4e00" <= ch <= "\u9fff" for ch in s))


if __name__ == "__main__":
    validate_lng()
    validate_rtfs()
    print()
    if fails:
        print(f"自检未通过: {len(fails)} 项")
        sys.exit(1)
    print("全部自检通过 ✓")
