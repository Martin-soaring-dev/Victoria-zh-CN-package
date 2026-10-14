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

### 方式一：一键安装（推荐）

1. 从 [Releases](../../releases) 下载 `Install-ZhCN.cmd`
2. 把它放进 **Victoria 程序根目录**——也就是和 `Victoria.exe` 同一个文件夹
3. 双击运行。程序会先检测同目录有没有 `Victoria.exe`：
   - **有** → 自动解压并覆盖安装 `LNG\Chinese.lng` 和 `Help\Chinese\*.rtf`
   - **没有** → 提示你把文件放对位置，不做任何操作

### 方式二：手动安装

下载 Release 里的 `Victoria-zhCN-files.zip`，解压到 Victoria 根目录（目录结构已按 `LNG\`、`Help\Chinese\` 组织好）；或从仓库直接取 `Chinese.lng` 和 `Help/Chinese/` 分别放进对应文件夹。

### 安装之后

1. **重启 Victoria**
2. 菜单 **Language → Chinese** 切换中文（新加入 `.lng` 后 ini 的语言索引会移位，需重选一次）
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
| `installer/` | 一键安装程序的构建脚本与产物（`Install-ZhCN.cmd`） |
| `.github/workflows/` | CI 校验 + 发布自动打包 |
| `skill/`、`soul.md` | 汉化工艺与项目维护文档 |
| `reference/` | 本地开发用（官方基线、翻译表、RTF 管线），**按设计不进库** |

## 🔧 开发者

```bash
python installer/validate_pack.py     # 自检交付物（CI 同款，提交前跑一遍）
python installer/build_installer.py   # 构建 Install-ZhCN.cmd + 手动安装 zip（含 payload 回读自检）
```

- **发布流程**：打 tag → GitHub 建 Release 并发布 → `release.yml` 自动构建上述两个文件并上传为 Release 资产，无需本地打包。
- **CI**：每次 push / PR 跑 `ci.yml`，自检 + 试构建安装程序。
- 语言包的完整重建管线（翻译表 → `Chinese.lng`）与帮助文档管线依赖本地 `reference/`，不在库内。

## 📄 许可

中文翻译文本以 [MIT](LICENSE) 发布。Victoria 本身为闭源软件，版权归原作者，请从[官网](https://hdd.by/)获取原程序并遵守其许可。
