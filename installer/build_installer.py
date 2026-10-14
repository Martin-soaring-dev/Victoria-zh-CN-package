#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建 Victoria 中文包安装程序（自解压 exe）与唯一发布包。

产物行为（对最终用户）：
  双击 Install-ZhCN.exe，先检测同目录有没有 Victoria.exe：
    · 没有 -> 弹窗提示把程序放到 Victoria 根目录，退出码 1，不落任何文件；
    · 有   -> 解压内嵌 payload 覆盖安装 LNG\\Chinese.lng + Help\\Chinese\\*.rtf，
             并把 Victoria.ini 的 [Setup] Language 写成 1（0=内置，1..N=LNG 内 .lng
             按文件名字母序，Chinese.lng 恒定第一）；字节级改写只动该行，
             Chinese.lng 非字母序第一、或 Victoria 正在运行（会覆写 ini）时跳过；
             最后弹窗汇报结果。

为什么用 PyInstaller 而不是 .cmd / SFX 工具：
  · .cmd 受 cmd.exe 的编码与引号怪癖拖累（chcp 竞态、全角括号、echo 空格都会拆行）；
  · 本机 IExpress 静默失败、WinRAR 的 SFX 受试用版限制、csc 被安全策略挡；
  · Python 打包出的 exe 用原生 Unicode 弹窗（Win32 MessageBoxW），零编码问题，
    且在 CI（windows-latest + pip install pyinstaller）可完全复现。

产物：
  installer/payload.zip              内嵌 payload（LNG\\ + Help\\Chinese\\）
  installer/dist/Install-ZhCN.exe   单文件自解压安装程序（PyInstaller onefile）
  installer/Victoria-zhCN-package.zip  唯一发布包（exe + 4 个语言文件 + 安装说明）
"""
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAYLOAD_ZIP = os.path.join(HERE, "payload.zip")
DIST_DIR = os.path.join(HERE, "dist")
EXE = os.path.join(DIST_DIR, "Install-ZhCN.exe")
PKG_OUT = os.path.join(HERE, "Victoria-zhCN-package.zip")

# (仓库内源文件, zip 内路径)
PAYLOAD = [
    ("Chinese.lng", "LNG/Chinese.lng"),
    ("Help/Chinese/vichlp.rtf", "Help/Chinese/vichlp.rtf"),
    ("Help/Chinese/whatsnew.rtf", "Help/Chinese/whatsnew.rtf"),
    ("Help/Chinese/dcomemo.rtf", "Help/Chinese/dcomemo.rtf"),
]

PKG_README = """Victoria 简体中文语言包 —— 安装说明
========================================

本包内含：
  Install-ZhCN.exe        自解压安装程序（推荐，双击即装）
  LNG\\Chinese.lng         中文语言包
  Help\\Chinese\\*.rtf     中文帮助（F1 手册 / 更新日志 / DCO 说明）
  安装说明.txt             本文件

【安装方法一：一键安装（推荐）】
  1. 把本包整个解压到 Victoria 程序根目录
     （也就是和 Victoria.exe 同一个文件夹）
  2. 双击 Install-ZhCN.exe
  3. 程序会先检测 Victoria.exe：找不到会提示你把程序放对位置（不会乱装）；
     找到则覆盖安装语言包与帮助，并把语言自动切换为中文
  4. 重启 Victoria 即为中文界面；按 F1 是中文帮助

【安装方法二：手动】
  本包解压后目录结构就是安装结构（LNG\\、Help\\Chinese\\）。
  已放进 Victoria 根目录的话，直接重启 Victoria，
  菜单 Language -> Chinese 选一次即可（不需要运行安装程序）。

【注意】
  · 建议先关闭 Victoria 再安装（否则语言设置会被它退出时覆写）
  · 卸载：删掉 LNG\\Chinese.lng 和 Help\\Chinese\\ 即可恢复原状
  · 本包只做本地化；Write / Erase / Remap 会破坏数据，动手前务必先备份

非官方粉丝翻译，与 Victoria 作者及 hdd.by 无隶属关系。
"""


def check_payload_file(src):
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


def make_payload():
    with zipfile.ZipFile(PAYLOAD_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in PAYLOAD:
            z.writestr(arc, check_payload_file(src))
    print(f"OK {PAYLOAD_ZIP} ({os.path.getsize(PAYLOAD_ZIP)} 字节)")


def build_exe():
    for d in (DIST_DIR, os.path.join(HERE, "build")):
        shutil.rmtree(d, ignore_errors=True)
    for f in ("Install-ZhCN.spec",):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            os.remove(p)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--noconsole", "--clean", "--noconfirm",
        "--name", "Install-ZhCN",
        "--add-data", f"{PAYLOAD_ZIP}{os.pathsep}.",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(HERE, "build"),
        "--specpath", HERE,
        os.path.join(HERE, "installer_gui.py"),
    ]
    print("$ " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0 or not os.path.isfile(EXE):
        raise SystemExit("[构建失败] PyInstaller 打包失败（是否已 pip install pyinstaller？）")
    print(f"OK {EXE} ({round(os.path.getsize(EXE) / 1024 / 1024, 1)} MB)")


def make_package():
    with zipfile.ZipFile(PKG_OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in PAYLOAD:
            z.writestr(arc, check_payload_file(src))
        z.writestr("Install-ZhCN.exe", open(EXE, "rb").read())
        z.writestr("安装说明.txt", PKG_README.replace("\n", "\r\n").encode("utf-8-sig"))
    # 自检：包内齐备且 exe 与刚构建的一致
    with zipfile.ZipFile(PKG_OUT) as z:
        names = set(z.namelist())
        need = {arc for _s, arc in PAYLOAD} | {"Install-ZhCN.exe", "安装说明.txt"}
        if not need <= names:
            raise SystemExit(f"[自检失败] 发布包缺少: {need - names}")
        if z.getinfo("Install-ZhCN.exe").file_size != os.path.getsize(EXE):
            raise SystemExit("[自检失败] 发布包内 exe 大小与构建产物不符")
    print(f"OK {PKG_OUT} ({round(os.path.getsize(PKG_OUT) / 1024 / 1024, 1)} MB，唯一发布包)")


if __name__ == "__main__":
    make_payload()
    build_exe()
    make_package()
    print("\n构建完成：把 installer/Victoria-zhCN-package.zip 作为 Release 资产发布即可。")
