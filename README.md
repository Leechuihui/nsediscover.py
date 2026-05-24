 NSE Script Discoverer

A desktop GUI tool to browse and inspect installed [Nmap NSE](https://nmap.org/book/nse.html) scripts. Select a script to view its description, categories, usage notes, example commands, and optional output from `nmap --script-help`.

Built for Python 3 on Linux and macOS
Modernized from the original Kali 2.0 Tkinter
fix by [Hacker Fantastic](https://github.com/HackerFantastic).
update by Leechuihui 2026525

## Features

Auto-detect** NSE scripts directory (`nmap --datadir`, common paths, or `NSE_SCRIPTS_DIR`)
Search by script name, author, description, or keywords
Filter by NSE category
Rich details: description, author, license, categories, `--@usage`, example `nmap` commands


 Requirements

 Python 3.9+ (uses `list[str]` type hints; use 3.10+ recommended)
[Nmap](https://nmap.org/) installed with NSE scripts
Tkinter (usually included with Python; on Debian/Ubuntu: `python3-tk`)

Installation

bash
git clone https://github.com/Leechuihui/nsediscover.py.git
cd nsediscover
