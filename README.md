**English** | [简体中文](README.zh-CN.md)

# 🔍 NSE Script Discoverer

[![Python](https://img.shields.io/badge/Python-3-3fb950?logo=python&logoColor=white)](https://python.org)
[![Nmap NSE](https://img.shields.io/badge/Built_for-Nmap_NSE-58a6ff?logo=nmap&logoColor=white)](https://nmap.org/book/nse.html)
[![GUI](https://img.shields.io/badge/UI-Tkinter-d29922)](#)

A desktop GUI tool to browse and inspect installed [Nmap NSE](https://nmap.org/book/nse.html) scripts. Select a script to view its description, categories, usage notes, example commands, and optional output from `nmap --script-help`.

Built for Python 3 on Linux and macOS.

Modernized from the original Kali 2.0 Tkinter
fix by [Hacker Fantastic](https://github.com/HackerFantastic).
Updated by Leechuihui 2026525.

```bash
python3 nsediscover.py
```

## Features

- Auto-detect NSE scripts directory (`nmap --datadir`, common paths, or `NSE_SCRIPTS_DIR`)
- Search by script name, author, description, or keywords
- Filter by NSE category
- Rich details: description, author, license, categories, `--@usage`, example `nmap` commands
- One-click helpers: open the official nmap.org NSE docs for the selected script, or copy an example `nmap` command to the clipboard

## Requirements

- Python 3.9+ (uses `list[str]` type hints; 3.10+ recommended)
- [Nmap](https://nmap.org/) installed with NSE scripts
- Tkinter (usually included with Python; on Debian/Ubuntu: `python3-tk`)

## Installation

```bash
git clone https://github.com/Leechuihui/nsediscover.py.git
cd nsediscover.py
python3 nsediscover.py
```

> If the NSE scripts directory cannot be found automatically, set the environment variable:
>
> ```bash
> NSE_SCRIPTS_DIR=/path/to/nmap/scripts python3 nsediscover.py
> ```

## Usage

- Type in the **Search** box to filter scripts by name, author, description, usage or keywords (`Ctrl+F` / `Cmd+F` focuses the search box)
- Pick a category from the **Category** dropdown to narrow the list
- Select a script to see its details in the right pane: name, categories, author, license, path, docs URL, description, `--@usage` block and example `nmap` commands
- **Open docs** opens the script's official nmap.org NSE documentation page in your browser
- **Copy nmap cmd** copies an example `nmap --script <name> <target>` command to the clipboard
- **Reload** re-scans the NSE scripts directory

The tool also runs `nmap --script-help` in the background for the selected script (cached) and appends its output to the details pane.
