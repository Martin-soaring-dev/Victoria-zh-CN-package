#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建自解压安装程序 installer/Install-ZhCN.cmd。

产物行为（对最终用户）：
  1. 双击运行后先检测所在目录有没有 Victoria.exe；
  2. 没有 -> 提示把本文件放到 Victoria 根目录（与 Victoria.exe 同级）再运行；
  3. 有   -> 解压内嵌 payload 并覆盖安装：
             LNG\\Chinese.lng
             Help\\Chinese\\{vichlp,whatsnew,dcomemo}.rtf

构建产物自带自检：生成后回读 payload 解码，与源文件逐字节比对。
CI 在发布 release 时自动调用本脚本（见 .github/workflows/release.yml）。
"""
import base64
import io
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "Install-ZhCN.cmd")
ZIP_OUT = os.path.join(HERE, "Victoria-zhCN-files.zip")  # 手动安装用（不打进自解压程序）

# (仓库内源文件, zip 内路径)
PAYLOAD = [
    ("Chinese.lng", "LNG/Chinese.lng"),
    ("Help/Chinese/vichlp.rtf", "Help/Chinese/vichlp.rtf"),
    ("Help/Chinese/whatsnew.rtf", "Help/Chinese/whatsnew.rtf"),
    ("Help/Chinese/dcomemo.rtf", "Help/Chinese/dcomemo.rtf"),
]

CHUNK = 100  # 每行 base64 字符数

TEMPLATE = r'''@echo off
chcp 65001 >nul
setlocal EnableExtensions
set "ROOT=%~dp0"
if /i not "%~1"=="-q" set "PAUSE=pause"

if not exist "%ROOT%Victoria.exe" (
    echo.
    echo  [x] 没有在所在目录找到 Victoria.exe
    echo.
    echo  请把本文件放到 Victoria 程序根目录，
    echo  也就是和 Victoria.exe 同一个文件夹，然后再双击运行。
    echo.
    if defined PAUSE pause
    exit /b 1
)

echo.
echo  正在解压中文语言包到：
echo    %ROOT%
echo.

set "ZHCN_SELF=%~f0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $lines=[IO.File]::ReadAllLines($env:ZHCN_SELF) | Where-Object { $_.StartsWith('::PAYLOAD=') }; if(-not $lines){throw 'payload missing'}; $b64=($lines | ForEach-Object { $_.Substring(10) }) -join ''; $zip=Join-Path $env:TEMP 'victoria-zhcn.zip'; [IO.File]::WriteAllBytes($zip,[Convert]::FromBase64String($b64)); $dir=Join-Path $env:TEMP 'victoria-zhcn-x'; if(Test-Path $dir){Remove-Item $dir -Recurse -Force}; Expand-Archive -LiteralPath $zip -DestinationPath $dir -Force; $root=Split-Path -Parent $env:ZHCN_SELF; New-Item -ItemType Directory -Force -Path (Join-Path $root 'LNG') | Out-Null; New-Item -ItemType Directory -Force -Path (Join-Path $root 'Help\Chinese') | Out-Null; Copy-Item -LiteralPath (Join-Path $dir 'LNG\Chinese.lng') -Destination (Join-Path $root 'LNG\Chinese.lng') -Force; Get-ChildItem -LiteralPath (Join-Path $dir 'Help\Chinese') -Filter *.rtf | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $root 'Help\Chinese') -Force }; Remove-Item $zip -Force -ErrorAction SilentlyContinue; Remove-Item $dir -Recurse -Force -ErrorAction SilentlyContinue; Write-Host '  OK'"

if errorlevel 1 (
    echo.
    echo  [x] 解压失败，请把上方错误信息反馈给仓库 issue。
    if defined PAUSE pause
    exit /b 1
)

echo.
echo  完成，已安装：
echo    LNG\Chinese.lng
echo    Help\Chinese\vichlp.rtf
echo    Help\Chinese\whatsnew.rtf
echo    Help\Chinese\dcomemo.rtf
echo.
echo  下一步：重启 Victoria，菜单 Language -^> Chinese 即可切换到中文；F1 为中文帮助。
if defined PAUSE pause
exit /b 0

:: ===== 以下为内嵌 payload（构建产物，请勿手动编辑；重新生成：python installer/build_installer.py）=====
'''


def check_payload_file(src, arc):
    path = os.path.join(ROOT, src)
    if not os.path.isfile(path):
        raise SystemExit(f"[构建失败] 缺少文件: {src}")
    data = open(path, "rb").read()
    if src.endswith(".lng"):
        # KDL 硬性要求：UTF-8 BOM + 纯 CRLF
        if not data.startswith(b"\xef\xbb\xbf"):
            raise SystemExit(f"[构建失败] {src} 缺少 UTF-8 BOM")
        if data.count(b"\n") != data.count(b"\r\n"):
            raise SystemExit(f"[构建失败] {src} 不是纯 CRLF 行尾")
    return data


def build():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in PAYLOAD:
            z.writestr(arc, check_payload_file(src, arc))
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    # 模板内部换行统一成 CRLF（cmd.exe 对混杂行尾会解析错乱）
    tmpl = TEMPLATE.replace("\r\n", "\n").replace("\n", "\r\n").rstrip("\r\n")
    lines = [tmpl]
    for i in range(0, len(b64), CHUNK):
        lines.append("::PAYLOAD=" + b64[i:i + CHUNK])
    blob = ("\r\n".join(lines) + "\r\n").encode("utf-8")
    # 自检：整个文件不得出现裸 LF
    assert blob.count(b"\n") == blob.count(b"\r\n"), "生成文件存在裸 LF"
    with open(OUT, "wb") as f:
        f.write(blob)

    # ---- 自检：回读生成的 .cmd，解码 payload 与源文件逐字节比对 ----
    text = blob.decode("utf-8")
    payload_lines = [ln for ln in text.split("\r\n") if ln.startswith("::PAYLOAD=")]
    got = base64.b64decode("".join(ln[10:] for ln in payload_lines))
    with zipfile.ZipFile(io.BytesIO(got)) as z:
        names = z.namelist()
        for src, arc in PAYLOAD:
            if arc not in names:
                raise SystemExit(f"[自检失败] payload 缺少 {arc}")
            if z.read(arc) != check_payload_file(src, arc):
                raise SystemExit(f"[自检失败] payload 中 {arc} 与源文件不一致")
    print(f"OK {OUT}")
    print(f"  payload: {len(names)} 个文件, zip {len(got)} 字节 -> base64 {len(b64)} 字符 ({len(payload_lines)} 行)")
    print(f"  安装程序总大小: {len(blob)} 字节")
    print("  自检通过: payload 解码后与源文件逐字节一致")

    # 手动安装用的普通 zip（与自解压程序内容一致）
    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in PAYLOAD:
            z.writestr(arc, check_payload_file(src, arc))
    print(f"OK {ZIP_OUT} ({os.path.getsize(ZIP_OUT)} 字节，手动安装用)")


if __name__ == "__main__":
    build()
