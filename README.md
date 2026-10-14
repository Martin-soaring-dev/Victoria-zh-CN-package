# Victoria 简体中文语言包

为 Windows 磁盘检测 / 坏道扫描工具 **Victoria**（hdd.by，Sergey Kazansky）提供**官方外挂式**中文界面与中文帮助——只放文本文件，不改 exe。

<p align="center">
  <img src="https://img.shields.io/github/v/release/Martin-soaring-dev/Victoria-zh-CN-package?style=for-the-badge&label=release" alt="release">
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="platform Windows">
  <img src="https://img.shields.io/badge/Victoria-5.23%20/%205.37-blue?style=for-the-badge" alt="Victoria 5.23 / 5.37">
  <img src="https://img.shields.io/badge/%E6%B1%89%E5%8C%96-635%20%E9%94%AE%20100%25-success?style=for-the-badge" alt="汉化 635 键 100%">
  <img src="https://img.shields.io/badge/F1%20%E5%B8%AE%E5%8A%A9-%E4%B8%AD%E6%96%87-success?style=for-the-badge" alt="F1 帮助 中文">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="license MIT">
  <img src="https://github.com/Martin-soaring-dev/Victoria-zh-CN-package/actions/workflows/ci.yml/badge.svg?style=for-the-badge" alt="CI">
</p>

> ⚠️ 非官方粉丝翻译，与 Victoria 作者及 hdd.by 无任何隶属关系。权利声明见 [NOTICE](NOTICE.md)。

## ✨ 特性

- **官方外挂式 `.lng`**：一个文本文件，零捆绑、零破解，删掉即恢复原版
- **单文件兼容 5.23 / 5.37**：两版字符串已合并，自动适配
- **界面汉化 635 键全覆盖**：菜单、按钮、提示、设置项、SMART 测试表
- **F1 中文帮助**：完整翻译使用手册、更新日志与 DCO 说明（译自官方俄文帮助）
- **一键安装程序**：放对位置双击即用，自动检测、自动覆盖

## 📦 安装

**从 [Releases](../../releases) 下载唯一的一个包 `Victoria-zhCN-package.zip`**，解压到 Victoria 程序根目录（与 `Victoria.exe` 同级）。包内就三样东西：

```
Victoria-zhCN-package.zip
├── Install-ZhCN.cmd      ← 一键安装程序（双击即装）
├── 安装说明.txt
├── LNG\Chinese.lng       ← 中文语言包
└── Help\Chinese\*.rtf    ← 中文帮助
```

### 方式一：一键安装（推荐）

双击 `Install-ZhCN.cmd`。它先检测同目录有没有 `Victoria.exe`：

- **有** → 自动覆盖安装 `LNG\Chinese.lng` 与 `Help\Chinese\*.rtf`，并把语言切换为中文
- **没有** → 提示你把包解压到 Victoria 根目录，不做任何操作

### 方式二：解压即用

包内结构就是 Victoria 的安装结构（`LNG\`、`Help\Chinese\`）。解压到程序根目录后直接重启 Victoria，菜单 **Language → Chinese** 选一次即可——不需要运行任何程序。

### 安装之后

1. **重启 Victoria** 即为中文界面（用一键安装的话 ini 已自动写好）
2. 若语言未生效：菜单 **Language → Chinese** 手动选一次
3. 按 **F1** 即是中文帮助；菜单「新增功能？」为中文更新日志

## ⚠️ 已知限制

- **少量英文是 `Victoria.exe` 硬编码**，任何官方语言包（含俄语原版）也同样显示英文，`.lng` 机制无法翻译：扫描按钮 `Scan` / `QUICK`、SMART 自检对话框的 `Current internal LBA`、SMART 测试表的 5 行描述、事件日志中 `SMART status = …` 等几条消息。
- 用 **5.23** 加载时，日志可能提示缺少若干字符串（5.37 新增键），属正常，不影响功能。
- 语言菜单里显示的项目名是文件名 `Chinese`（ASCII 文件名兼容性最佳）。
- 本包只做本地化；**Write / Erase / Remap 会破坏数据**，动手前务必先备份。

## 🗂 仓库结构

| 路径 | 说明 |
|---|---|
| `Chinese.lng` | 中文语言包（交付物，5.23 + 5.37 合并版） |
| `Help/Chinese/` | 中文帮助（`vichlp.rtf` 使用手册 / `whatsnew.rtf` 更新日志 / `dcomemo.rtf` DCO 说明） |
| `installer/` | 构建脚本与产物（`Install-ZhCN.cmd` 单文件安装程序；发布时另打包为 `Victoria-zhCN-package.zip`） |
| `.github/workflows/` | CI 校验 + 发布自动打包 |
| `skill/`、`soul.md` | 汉化工艺与项目维护文档 |
| `reference/` | 本地开发用（官方基线、翻译表、RTF 管线），**按设计不进库** |

## 🔧 开发者

```bash
python installer/validate_pack.py     # 自检交付物（CI 同款，提交前跑一遍）
python installer/build_installer.py   # 构建 Install-ZhCN.cmd + 唯一发布包 Victoria-zhCN-package.zip（含回读自检）
```

- **发布流程**：打 tag → GitHub 建 Release 并发布 → `release.yml` 自动构建并上传**唯一一个**发布包，无需本地打包。
- **CI**：每次 push / PR 跑 `ci.yml`，自检 + 试构建安装程序。
- 语言包的完整重建管线（翻译表 → `Chinese.lng`）与帮助文档管线依赖本地 `reference/`，不在库内。

## 📄 许可

中文翻译文本以 [MIT](LICENSE) 发布。Victoria 本身为闭源软件，版权归原作者，请从[官网](https://hdd.by/)获取原程序并遵守其许可。
