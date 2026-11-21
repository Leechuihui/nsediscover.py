[English](README.md) | **简体中文**

# 🔍 NSE Script Discoverer

[![Python](https://img.shields.io/badge/Python-3-3fb950?logo=python&logoColor=white)](https://python.org)
[![Nmap NSE](https://img.shields.io/badge/Built_for-Nmap_NSE-58a6ff?logo=nmap&logoColor=white)](https://nmap.org/book/nse.html)
[![GUI](https://img.shields.io/badge/UI-Tkinter-d29922)](#)

一款桌面 GUI 工具，用于浏览和检查本机已安装的 [Nmap NSE](https://nmap.org/book/nse.html) 脚本。选中某个脚本即可查看其描述、分类、用法说明、示例命令，以及可选的 `nmap --script-help` 输出。

基于 Python 3，支持 Linux 和 macOS。

由原始 Kali 2.0 Tkinter 版本现代化改造而来，
修复来自 [Hacker Fantastic](https://github.com/HackerFantastic)。
由 Leechuihui 于 2026525 更新。

```bash
python3 nsediscover.py
```

## 功能特性

- 自动检测 NSE 脚本目录（`nmap --datadir`、常见路径，或 `NSE_SCRIPTS_DIR`）
- 按脚本名称、作者、描述或关键词搜索
- 按 NSE 分类筛选
- 丰富的详情：描述、作者、许可证、分类、`--@usage`、示例 `nmap` 命令
- 一键辅助：在浏览器中打开所选脚本的 nmap.org NSE 官方文档，或将示例 `nmap` 命令复制到剪贴板

## 环境要求

- Python 3.9+（使用了 `list[str]` 类型标注；推荐 3.10+）
- 已安装 [Nmap](https://nmap.org/) 且带有 NSE 脚本
- Tkinter（通常随 Python 自带；Debian/Ubuntu 上为 `python3-tk`）

## 安装

```bash
git clone https://github.com/Leechuihui/nsediscover.py.git
cd nsediscover.py
python3 nsediscover.py
```

> 如果无法自动找到 NSE 脚本目录，请设置环境变量：
>
> ```bash
> NSE_SCRIPTS_DIR=/path/to/nmap/scripts python3 nsediscover.py
> ```

## 使用说明

- 在 **Search** 框中输入即可按脚本名称、作者、描述、用法或关键词筛选（`Ctrl+F` / `Cmd+F` 聚焦搜索框）
- 从 **Category** 下拉框中选择分类以缩小列表范围
- 选中脚本即可在右侧面板查看详情：名称、分类、作者、许可证、路径、文档 URL、描述、`--@usage` 代码块以及示例 `nmap` 命令
- **Open docs** 在浏览器中打开该脚本在 nmap.org 上的 NSE 官方文档页面
- **Copy nmap cmd** 将示例命令 `nmap --script <name> <target>` 复制到剪贴板
- **Reload** 重新扫描 NSE 脚本目录

工具还会在后台对所选脚本运行 `nmap --script-help`（带缓存），并将其输出追加到详情面板。
