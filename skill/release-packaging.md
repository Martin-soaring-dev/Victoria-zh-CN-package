# 技能：安装程序构建与发布打包

## 适用
构建一键安装程序 `installer/Install-ZhCN.cmd`、跑交付物自检、走 GitHub 发布流程。

## 关键事实
- 用户只下载**一个包**：`Victoria-zhCN-package.zip`（内为 Install-ZhCN.cmd + LNG\Chinese.lng + Help\Chinese\*.rtf + 安装说明.txt，解压目录即安装结构）。仓库内的 `Chinese.lng` 与 `Help/Chinese/` 是构建用源文件。
- 安装程序是**单文件自解压 .cmd**：payload 为 base64 内嵌 zip，以 `::PAYLOAD=` 注释行写入文件（每行 100 字符）；运行时由 PS 引擎回读自身、解码、`Expand-Archive`、`Copy-Item -Force` 覆盖到 `LNG\` 与 `Help\Chinese\`。
- **编码必须 GBK(cp936)**：中文 Windows 控制台原生码页，cmd 按此设计、解析稳定。**不要**用 UTF-8 + `chcp 65001`——codepage 切换与 cmd 逐行解析存在竞态，会随机把行拆碎（今天实测：同一文件连跑两次一次报错一次正常）。
- 语言自动切换：安装后把 `Victoria.ini` 的 `[Setup] Language` 写成 `1`（0=内置，1..N=LNG 文件夹内 `.lng` 按文件名字母序，`Chinese.lng` 恒定第一）。用 Latin1(28591) 字节级读写，只换 `Language=` 行，不动其余内容；若 `Chinese.lng` 不是字母序第一个则跳过并提示手动选择。
- `.gitattributes` 里 `*.lng/*.rtf/*.cmd` 是 `-text` 原样存储：`text eol=crlf` 会让 blob 存 LF，GitHub raw 下载 / Download ZIP 拿到 LF 版，`.cmd` 会直接跑不动。

## 流程
1. 改完 `Chinese.lng` / `Help/Chinese/` 后，先自检：`python installer/validate_pack.py`（BOM、纯 CRLF、引号、INI 节名、RTF GBK 可解码、括号配平；不依赖 `reference/`）。
2. 构建：`python installer/build_installer.py` → 生成 `Install-ZhCN.cmd`（单文件自解压）与**唯一发布包** `Victoria-zhCN-package.zip`（含安装程序 + LNG\ + Help\Chinese\ + 安装说明.txt；已 gitignore，仅随 Release 上传）。两者都自带自检（payload 回读 + 包内容齐备校验）。
3. 实测两个场景（必须做，cmd 解析很脆）：
   - 有 `Victoria.exe` + `Language=3` 的 ini → 应退出码 0、ini 变 1、四个文件逐字节一致；
   - 无 `Victoria.exe` → 应提示并退出码 1、不产生任何文件。
   - 判据：输出里**不得出现** "is not recognized / 不是内部或外部命令"（解析被拆碎的标志）。
4. 提交（单独 commit）：交付物改动 → `fix/feat`；脚本与文档 → `chore/docs`。
5. 发布：`git push` → 打 tag（如 `v1.0`）→ GitHub 建 Release 并发布 → `release.yml` 自动构建并上传**唯一一个**发布包（`Victoria-zhCN-package.zip`）。**无需本地打包**。

## 常见坑（cmd.exe，全部实测踩过）
- **全角括号**：执行路径上的任何行（`if` 块内、`::` 注释内、echo 行内）出现 `（）` 都会让**后续行**被拆碎。块外 echo 行也躲不过。→ 一律不用全角括号。
- **echo 后空格**：`echo` 与中文之间空格 ≤2 个；8 个空格会触发字节错位拆行。
- **混杂行尾**：生成的 .cmd 必须全文件统一 CRLF（构建时断言无裸 LF）。
- 中文放进 `powershell -Command "..."` 引号内在某些上下文会被拆——保险做法是合并成**一次** PS 调用，且中文只用于 `Write-Host` 输出（输出本身正常）。
- PowerShell 改 ini 要用 `[Text.Encoding]::GetEncoding(28591)` 做字节级往返，直接 ReadAllText/WriteAllText 遇上非 UTF-8 内容会毁文件。
