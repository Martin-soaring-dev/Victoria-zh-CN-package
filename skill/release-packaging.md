# 技能：安装程序构建与发布打包

## 适用
构建自解压安装程序 `Install-ZhCN.exe`、组装唯一发布包、跑交付物自检、走 GitHub 发布流程。

## 交付形态（用户视角）
- **唯一发布物**：`Victoria-zhCN-package.zip`（约 7 MB）
  = `Install-ZhCN.exe`（自解压安装程序）+ `LNG\Chinese.lng` + `Help\Chinese\*.rtf` + `安装说明.txt`
  解压目录即安装结构：可双击 exe 一键装，也可直接复制文件手动装。
- 安装程序行为：先检测同目录 `Victoria.exe` → 无则弹窗提示放对位置（不落文件，退出码 1）；
  有则解压覆盖 payload，并把 `Victoria.ini` 的 `[Setup] Language` 写成 1（0=内置，1..N=LNG 内
  `.lng` 按文件名字母序，`Chinese.lng` 恒定第一）；字节级改写只动该行；`Chinese.lng` 非字母序第一
  或 Victoria 正在运行（会覆写 ini）时跳过并提示。

## 为什么是 PyInstaller（技术选型结论，别重复踩）
本机/CI 可用于「产出 exe」的路子全部试过：
- **`.cmd` 自解压**：受 cmd.exe 编码怪癖拖累——`chcp 65001` 与逐行解析存在竞态（同一文件连跑两次
  一次报错一次正常）、执行路径任何行不能有全角括号、`echo` 后空格 ≤2、混杂行尾会拆行。**已弃用。**
- **IExpress**（Windows 自带）：在本机静默失败（GUI 子系统无交互桌面），无法验证。
- **WinRAR SFX**：`-sfxWinCon.SFX` 生成的其实是普通 unrar，SFX 脚本指令（`Setup=`）不生效
  （试用版限制），且 CI 无 WinRAR。
- **csc.exe / Add-Type 编译 C#**：被安全策略阻止（任意代码编译）。
- → **PyInstaller**：本机与 CI 均可复现，Python 侧用原生 Unicode，零编码问题。

## 关键实现细节
- 安装器源码 `installer/installer_gui.py`：
  - 弹窗用 **`ctypes.windll.user32.MessageBoxW`**（原生 Unicode），**不要用 tkinter**——
    托管 Python 是精简版、没有 tkinter，打包后会运行时 `ModuleNotFoundError`。
  - `--silent` 无界面模式：写 `install-log.txt` 并打印，供自动化验证（否则 --noconsole 无从测试）。
  - `base_dir()` = 冻结时 `sys.executable` 所在目录；payload 从 `sys._MEIPASS` 取。
  - ini 用 **latin-1 字节级往返**改写，避免破坏非 UTF-8 内容。
- 构建 `installer/build_installer.py`：生成 `payload.zip` → `python -m PyInstaller --onefile
  --noconsole --add-data "<绝对路径>/payload.zip;." ...` → 组装发布包 + 自检。
  **注意**：`--add-data` 与 `--distpath/--workpath/--specpath` 一律用**绝对路径**，
  否则 `--specpath` 会改变相对路径基准导致找不到 payload。
- 入库策略：`payload.zip`、`dist/`、`build/`、`*.spec`、发布包 zip 全部 gitignore；
  仓库只保留源码与脚本，exe 由 CI 在发布时构建。

## 流程
1. 改完 `Chinese.lng` / `Help/Chinese/` 后先自检：`python installer/validate_pack.py`
   （BOM、纯 CRLF、引号、INI 节名、RTF GBK 可解码、括号配平；不依赖 `reference/`）。
2. 构建：`pip install pyinstaller` → `python installer/build_installer.py`。
3. 实测（必须做，至少三场景）：
   - 有 `Victoria.exe` + `Language=3` 的 ini：`Install-ZhCN.exe --silent` → 退出码 0、
     文件逐字节一致、ini 变为 `Language=1`（若本机 Victoria 正在运行则会跳过，属预期）；
   - 无 `Victoria.exe`：退出码 1、不落任何文件；
   - 把 `LNG\` 里放一个字母序更靠前的 `.lng`：跳过自动切语言，ini 不变。
   - 读 `install-log.txt` 核对文案；文件级校验用 `cmp` 与 `Chinese.lng` 逐字节比对。
4. 提交（单独 commit）：交付物改动 → `fix/feat`；脚本与文档 → `chore/docs`。
5. 发布：`git push` → 打 tag（如 `v1.0`）→ GitHub 建 Release 并发布 →
   `release.yml`（windows-latest）自动 `pip install pyinstaller` → 构建 → 上传唯一发布包。
   **无需本地打包**。CI 里 `ci.yml` 同样试构建并留存 artifact 供实测。

## 其它约定
- `.gitattributes`：`*.lng/*.rtf/*.cmd/*.bat/*.ps1` 用 `-text` 原样存储（`text eol=crlf` 会让 blob
  存 LF，GitHub raw/zip 下载拿到 LF 版），`*.py/*.md/*.yml/*.tsv` 用 LF。
- Release 资产只挂**一个**包；不要额外挂散文件或第二个 zip。
