# 技能：Victoria .lng 汉化与校验

## 适用
为 Victoria 磁盘工具生成 / 维护简体中文语言文件（目标 `Chinese.lng` / `简体中文.lng`）。

## 关键事实
- 格式：Kryvich's Delphi Localizer Language File
  - `; 开头` = 注释
  - `[FormName]` = 段（窗体 / 模块）
  - `控件名.属性='值'` = 一条字符串，如 `Button2.Caption='Start'`
- 转义规则（必须保留）：
  - `&&` → 字面 `&`（菜单 / 按钮加速键，显示时变单个 &）
  - `''` → 字面 `'`
  - 行内单个 `&` 表示加速键（界面下划线），翻译时尽量保留原位置
- 编码：**UTF-8 带 BOM**（与原版一致；缺 BOM 可能乱码 / 不被识别）
- 键名须覆盖对应版本全部控件；`Items.Strings` 数组段序须与 5.37 超集对齐（5.23 为子集，索引 0–173 两版一致）；**行数不强制等于原版**（5.37 官方 English.lng 为 674 行）
  - 用 `reference/Victoria523/LNG/English.lng` 作基准校验

## 流程
1. 以某版本 `English.lng` 为模板复制为新中文文件（保留全部注释、段、键名，仅替换值）。
2. 逐条翻译 `Caption / Hint / Text / Items.Strings` 等属性值；保留 `&&`、`'` 转义与加速键 `&`。
3. 术语一致性：参考 `reference/unique_values.json` 去重字符串与已译条目，建立术语表。
4. 语言菜单直接读取 `.lng` 文件名并作为显示项，**无需改 `Victoria.ini`**（菜单项是文件名本身，故用 `Chinese.lng` 这类 ASCII 名最稳）。

## 验证（可验证交付）
- 键覆盖（两版并集）：合并版键集合须 ⊇ 5.23 与 5.37 英文版键集合（0 缺失）。
- 数组段序（防越界）：所有 `*.Items.Strings` 段数须 ≥ 5.37（超集），且 5.23 范围（索引 0–173）内译文按 5.37 基线对齐。
- 格式：`file 中文.lng` 应报告 UTF-8 Unicode (with BOM)；`CRLF` 换行、0 裸 `LF`；引号全部配对；`configparser` 以 `strict=False` 可解析（官方 English.lng 节名会重复）。
- 未译检查：非技术符号的条目 0 未译。
- 转义抽检：确认无意外丢失的 `&&` / `'`。

## 常见坑
- 误删 BOM → 程序识别失败 / 乱码
- 漏翻 `Hint`（提示）只翻 `Caption` → 半成品
- 行数不对 → 多半是误增 / 删了空行或注释
- 加速键 `&` 错位移 → 界面下划线位置变
