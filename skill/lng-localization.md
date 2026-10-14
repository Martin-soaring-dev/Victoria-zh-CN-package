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
4. 语言菜单直接读取 `.lng` 文件名并作为显示项（故用 `Chinese.lng` 这类 ASCII 名最稳）。**语言选择本身存在 `Victoria.ini` 的 `[Setup] Language=`**：0=内置，1..N 为 LNG 文件夹内 `.lng` 按文件名字母序，`Chinese.lng` 恒定第一——一键安装程序据此自动写 1；手动安装的用户需在菜单里选一次（加入新 `.lng` 后索引会移位）。

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
- **Caption 变长导致按钮换行**：Delphi/Raize 按钮不自适应文本。实测容量：SMART 对话框按钮可用约 43px、主窗口右侧按钮列可用约 53px（9pt 下 CJK ≈ 14.5px/字）。改短Caption 前先扫「中文显示宽 > 英文宽」的条目（比对时**剥掉 `&`**——加速键不占显示宽度；且 CJK 上的 `&` 在 Windows 无加速功能），最终以实机截图像素测量为准。已修：SmartOnBtn→启用、SmartOFFBtn→禁用、TSmForm SmartBtn→读 SMART、RecBtn→重校准、SmIgnCrcChk→忽略 CS、SetWdTimerBtn/ReadWdTimBtn→设置/读取、DftSmartInitBtn→初始化、ResizeFormChk 缩至 24 字、ResetBtn→复位(&R)。

## 术语（已定论，勿再改）
- **Passport = 通行证**（2026-10-14 由「护照」改定：中文「护照」仅指旅行证件；官方俄语包 паспорт 有「设备技术证件」引申义但中文没有；「通行证」是中文维修圈对该按钮的既有叫法）。`WD Passport` 是产品名保留英文；`Passport USB` 是「USB 通行证」变体标签（排在 Drive ATA passport 与 SCSI Drive passport 之间），不是产品名。
- Scan=表面扫描；Verify=校验；Read=读取；Write=写入；Erase=擦除；Remap=重映射；Ignore=忽略；Refresh=刷新；Block=块；Sector=扇区；BAD=坏扇区；Defect=缺陷；timeout=超时；Grid=网格；Command=命令（NCQ=原生命令队列）；Pattern file=图案文件。
