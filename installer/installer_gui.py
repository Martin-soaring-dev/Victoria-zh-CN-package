# -*- coding: utf-8 -*-
"""Victoria 简体中文语言包 —— 自解压安装程序（GUI，tkinter）。

打包为单文件 exe：pyinstaller --onefile --noconsole --add-data "payload.zip;." installer_gui.py
行为：
  1. 检测自身所在目录有没有 Victoria.exe；没有 -> 弹窗提示把程序放到 Victoria 根目录，退出码 1；
  2. 有 -> 把内嵌 payload（LNG\\Chinese.lng + Help\\Chinese\\*.rtf）解压覆盖到该目录；
  3. 自动切换语言：[Setup] Language=1（0=内置，1..N=LNG 内 .lng 按文件名字母序，Chinese.lng 恒定第一），
     字节级改写只动该行；Chinese.lng 非字母序第一、或 Victoria 正在运行（会覆写 ini）时跳过并提示；
  4. 弹窗汇报结果。
tkinter 是原生 Unicode，无需任何 codepage 处理。
"""
import os
import re
import subprocess
import sys
import zipfile

PAYLOAD = "payload.zip"


def base_dir():
    """被 PyInstaller 冻结时返回 exe 所在目录，否则返回脚本所在目录。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def payload_path():
    """内嵌资源目录（onefile 解包到 sys._MEIPASS）。"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, PAYLOAD)


def victoria_running():
    """Victoria.exe 是否在运行（它退出时会覆写 ini，此时不能改语言设置）。"""
    if os.name != "nt":
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Victoria.exe", "/NH"],
            capture_output=True, creationflags=0x08000000, timeout=15,
        ).stdout.decode("gbk", errors="replace")
        return "victoria.exe" in out.lower()
    except Exception:
        return False


def switch_language(root):
    """把 Victoria.ini 的 [Setup] Language 写成 1。返回给用户看的说明文字。"""
    ini = os.path.join(root, "Victoria.ini")
    if not os.path.isfile(ini):
        return "未找到 Victoria.ini：首次运行后将默认使用第一个语言文件。"
    lng_dir = os.path.join(root, "LNG")
    try:
        lngs = sorted(
            (n for n in os.listdir(lng_dir) if n.lower().endswith(".lng")),
            key=lambda s: s.lower(),
        )
    except OSError:
        lngs = []
    if lngs and lngs[0].lower() != "chinese.lng":
        return "LNG 目录下 Chinese.lng 不是第一个语言文件，已跳过自动切换，请在菜单里手动选择。"
    if victoria_running():
        return "检测到 Victoria 正在运行，已跳过自动切换语言（它退出时会覆写 ini）。\n请关闭 Victoria 后重跑本程序，或手动切换。"
    try:
        with open(ini, "rb") as f:
            raw = f.read()
        text = raw.decode("latin-1")           # 字节级往返，避免破坏非 UTF-8 内容
        if re.search(r"(?m)^Language=\d", text):
            new = re.sub(r"(?m)^Language=\d+", "Language=1", text, count=1)
        else:
            new = re.sub(r"(?m)^\[Setup\]", "[Setup]\r\nLanguage=1", text, count=1)
        if new == text:
            return "语言已是中文，无需切换。"
        with open(ini, "wb") as f:
            f.write(new.encode("latin-1"))
        return "已自动切换语言为中文。"
    except Exception as e:                      # 语言切换失败不阻断安装
        return "自动切换语言失败（不影响安装）：%s" % e


def extract(root):
    with zipfile.ZipFile(payload_path()) as z:
        z.extractall(root)


def main():
    # --silent：无界面模式（供自动化测试 / 脚本调用），只打印结果并用退出码表示成败
    silent = "--silent" in sys.argv[1:]

    dst = base_dir()
    if not os.path.isfile(os.path.join(dst, "Victoria.exe")):
        report(silent, "error", "未找到 Victoria.exe",
               "没有在所在目录找到 Victoria.exe。\n\n"
               "请把本程序放到 Victoria 程序根目录\n"
               "（也就是和 Victoria.exe 同一个文件夹），然后再运行。")
        return 1

    try:
        extract(dst)
    except Exception as e:
        report(silent, "error", "安装失败", "解压失败：\n%s" % e)
        return 1

    note = switch_language(dst)
    report(silent, "info", "安装完成",
           "中文语言包与中文帮助已安装到：\n%s\n\n%s\n\n"
           "重启 Victoria 即为中文界面；按 F1 为中文帮助。" % (dst, note))
    return 0


def report(silent, kind, title, message):
    if silent:
        # 无界面模式：写日志文件（供自动化验证），不弹窗
        try:
            with open(os.path.join(base_dir(), "install-log.txt"), "w", encoding="utf-8") as f:
                f.write("%s\n%s\n" % (title, message))
        except OSError:
            pass
        print("[%s] %s" % (title, message.replace("\n", " ")))
        return
    # 原生 Win32 弹窗：零依赖、原生 Unicode（不依赖 tkinter）
    import ctypes
    flags = 0x10 if kind == "error" else 0x40    # MB_ICONERROR / MB_ICONINFORMATION
    ctypes.windll.user32.MessageBoxW(None, message, title, flags)


if __name__ == "__main__":
    sys.exit(main())
