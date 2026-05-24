#!/usr/bin/env python3
"""
NSE Script Discoverer — browse and inspect installed Nmap NSE scripts.

Built by leechuihui · Updated 2026525
Modernized for Python 3 and current Nmap layouts (2026).
Original concept: Hacker Fantastic (Kali 2.0 Tkinter fix).
"""

from __future__ import annotations

BUILD_AUTHOR = "leechuihui"
BUILD_DATE = "2026525"
APP_TITLE = f"NSE Script Discoverer — {BUILD_AUTHOR} (build {BUILD_DATE})"

import os
import re
import shutil
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import END, BOTH, LEFT, RIGHT, VERTICAL, X, Y, StringVar, Tk, ttk
from tkinter import scrolledtext
from tkinter import messagebox

# Common Nmap script directories (Linux, macOS/Homebrew, Nix, custom prefix)
_SCRIPT_SEARCH_PATHS: tuple[Path, ...] = (
    Path("/usr/share/nmap/scripts"),
    Path("/usr/local/share/nmap/scripts"),
    Path("/opt/homebrew/share/nmap/scripts"),
    Path("/opt/local/share/nmap/scripts"),
    Path(os.environ.get("NMAP_DATADIR", "")) / "scripts" if os.environ.get("NMAP_DATADIR") else Path(),
)


@dataclass
class NseScript:
    name: str
    path: Path
    description: str = ""
    author: str = ""
    license_text: str = ""
    categories: list[str] = field(default_factory=list)
    usage: str = ""
    nsedoc_url: str = ""

    @property
    def stem(self) -> str:
        return self.path.stem


def find_scripts_dir() -> Path | None:
    """Resolve the NSE scripts directory."""
    env = os.environ.get("NSE_SCRIPTS_DIR")
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p

    nmap = shutil.which("nmap")
    if nmap:
        try:
            out = subprocess.run(
                [nmap, "--datadir"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            for line in out.stdout.splitlines():
                line = line.strip()
                if line:
                    candidate = Path(line) / "scripts"
                    if candidate.is_dir():
                        return candidate
        except (OSError, subprocess.TimeoutExpired):
            pass

    for candidate in _SCRIPT_SEARCH_PATHS:
        if candidate and candidate.is_dir():
            return candidate
    return None


def _extract_bracket_block(text: str, key: str) -> str:
    """Parse description = [[ ... ]] style multiline blocks."""
    pattern = rf"{re.escape(key)}\s*=\s*\[\["
    m = re.search(pattern, text)
    if not m:
        return ""
    start = m.end()
    end = text.find("]]", start)
    if end == -1:
        return text[start:].strip()
    return text[start:end].strip()


def _extract_string_field(text: str, key: str) -> str:
    """Parse author = "..." or license = '...' fields."""
    m = re.search(
        rf'{re.escape(key)}\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|\[\[(.*?)\]\])',
        text,
        re.DOTALL,
    )
    if not m:
        return ""
    return next(g for g in m.groups() if g is not None).strip()


def _extract_categories(text: str) -> list[str]:
    m = re.search(r"categories\s*=\s*\{([^}]*)\}", text)
    if not m:
        return []
    inner = m.group(1)
    return [c.strip().strip('"').strip("'") for c in inner.split(",") if c.strip()]


def _extract_usage(text: str) -> str:
    """Pull --@usage documentation from Lua comment blocks."""
    m = re.search(r"--@usage\s*\n((?:--[^\n]*\n?)+)", text)
    if not m:
        return ""
    lines = []
    for line in m.group(1).splitlines():
        if line.startswith("--"):
            lines.append(line[2:].lstrip())
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def parse_nse_file(path: Path) -> NseScript:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return NseScript(
            name=path.name,
            path=path,
            description=f"Unable to read script: {exc}",
        )

    desc = _extract_bracket_block(raw, "description")
    if not desc:
        desc = _extract_string_field(raw, "description")

    stem = path.stem
    return NseScript(
        name=path.name,
        path=path,
        description=desc,
        author=_extract_string_field(raw, "author"),
        license_text=_extract_string_field(raw, "license"),
        categories=_extract_categories(raw),
        usage=_extract_usage(raw),
        nsedoc_url=f"https://nmap.org/nsedoc/scripts/{stem}.html",
    )


def format_script_details(script: NseScript, nmap_help: str | None = None) -> str:
    lines: list[str] = []
    lines.append(script.name)
    lines.append("=" * len(script.name))

    if script.categories:
        lines.append(f"Categories: {', '.join(script.categories)}")
    if script.author:
        lines.append(f"Author: {script.author}")
    if script.license_text:
        lines.append(f"License: {script.license_text}")
    lines.append(f"Path: {script.path}")
    lines.append(f"Docs:   {script.nsedoc_url}")
    lines.append("")

    if script.description:
        lines.append("Description")
        lines.append("-" * 11)
        lines.append(script.description)
        lines.append("")

    if script.usage:
        lines.append("Usage")
        lines.append("-" * 5)
        lines.append(script.usage)
        lines.append("")

    lines.append("Example")
    lines.append("-" * 7)
    lines.append(f"  nmap --script {script.stem} <target>")
    if script.categories:
        lines.append(f"  nmap --script '{script.stem}' -p <port> <target>")
    lines.append("")

    if nmap_help:
        lines.append("nmap --script-help")
        lines.append("-" * 17)
        # Drop Nmap banner lines from --script-help output
        help_lines = [
            ln
            for ln in nmap_help.splitlines()
            if not ln.startswith("Starting Nmap") and ln.strip() != ""
        ]
        lines.extend(help_lines)

    return "\n".join(lines)


class NseDiscoverApp:
    def __init__(self, scripts_dir: Path) -> None:
        self.scripts_dir = scripts_dir
        self.scripts: list[NseScript] = []
        self.filtered: list[NseScript] = []
        self._help_cache: dict[str, str] = {}
        self._load_task: threading.Thread | None = None

        self.root = Tk()
        self.root.title(APP_TITLE)
        self.root.minsize(900, 520)

        self.search_var = StringVar()
        self.category_var = StringVar(value="(all)")
        self.status_var = StringVar()

        self._build_ui()
        self._center_window(960, 560)
        self._load_scripts()

        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        self.category_var.trace_add("write", lambda *_: self._apply_filter())

    def _center_window(self, w: int, h: int) -> None:
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self) -> None:
        style = ttk.Style()
        if sys.platform == "darwin":
            style.theme_use("aqua")
        elif "clam" in style.theme_names():
            style.theme_use("clam")

        toolbar = ttk.Frame(self.root, padding=(8, 8, 8, 4))
        toolbar.pack(fill=X)

        ttk.Label(toolbar, text="Search:").pack(side=LEFT)
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=36)
        search_entry.pack(side=LEFT, padx=(4, 12))
        search_entry.focus_set()

        ttk.Label(toolbar, text="Category:").pack(side=LEFT)
        self.category_combo = ttk.Combobox(
            toolbar,
            textvariable=self.category_var,
            state="readonly",
            width=18,
        )
        self.category_combo.pack(side=LEFT, padx=(4, 12))

        ttk.Button(toolbar, text="Open docs", command=self._open_docs).pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="Copy nmap cmd", command=self._copy_command).pack(side=LEFT, padx=2)
        ttk.Button(toolbar, text="Reload", command=self._load_scripts).pack(side=LEFT, padx=2)

        paned = ttk.Panedwindow(self.root, orient="horizontal")
        paned.pack(fill=BOTH, expand=True, padx=8, pady=4)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        self.listbox = ttk.Treeview(
            left,
            columns=("categories",),
            show="tree headings",
            selectmode="browse",
        )
        self.listbox.heading("#0", text="Script")
        self.listbox.heading("categories", text="Categories")
        self.listbox.column("#0", width=220, stretch=True)
        self.listbox.column("categories", width=160, stretch=True)

        list_scroll = ttk.Scrollbar(left, orient=VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=list_scroll.set)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=True)
        list_scroll.pack(side=RIGHT, fill=Y)

        self.listbox.bind("<<TreeviewSelect>>", self._on_select)

        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        self.detail_text = scrolledtext.ScrolledText(
            right,
            wrap="word",
            font=("Menlo", 12) if sys.platform == "darwin" else ("Consolas", 11),
            padx=10,
            pady=10,
        )
        self.detail_text.pack(fill=BOTH, expand=True)
        self._show_welcome()

        ttk.Separator(self.root, orient="horizontal").pack(fill=X, padx=8, pady=(4, 0))
        footer = ttk.Frame(self.root, padding=(8, 4, 8, 8))
        footer.pack(fill=X)
        ttk.Label(
            footer,
            text=f"Built by {BUILD_AUTHOR} · Updated {BUILD_DATE}",
            anchor="w",
        ).pack(side=LEFT)
        ttk.Label(footer, textvariable=self.status_var, anchor="e").pack(
            side=RIGHT, fill=X, expand=True
        )

        self.root.bind("<Control-f>", lambda e: search_entry.focus_set())
        self.root.bind("<Command-f>", lambda e: search_entry.focus_set())

    def _show_welcome(self) -> None:
        welcome = (
            f"NSE Script Discoverer\n"
            f"{'=' * 22}\n\n"
            f"Built by:  {BUILD_AUTHOR}\n"
            f"Updated:   {BUILD_DATE}\n\n"
            "Select a script from the list to view its description,\n"
            "categories, usage notes, and example nmap commands.\n\n"
            "Tips:\n"
            "  • Use Search to filter by name, author, or keywords\n"
            "  • Use Category to narrow by NSE category\n"
            "  • Open docs — official nmap.org NSE documentation\n"
            "  • Copy nmap cmd — copy an example command to the clipboard\n"
        )
        self.detail_text.delete("1.0", END)
        self.detail_text.insert(END, welcome)

    def _load_scripts(self) -> None:
        self.status_var.set(f"Loading scripts from {self.scripts_dir} …")
        self.root.update_idletasks()

        paths = sorted(self.scripts_dir.glob("*.nse"))
        self.scripts = [parse_nse_file(p) for p in paths]

        cats: set[str] = set()
        for s in self.scripts:
            cats.update(s.categories)
        values = ["(all)"] + sorted(cats)
        self.category_combo["values"] = values
        self.category_var.set("(all)")

        self._apply_filter()
        self.status_var.set(
            f"{len(self.scripts)} scripts · {self.scripts_dir} · "
            f"Nmap: {shutil.which('nmap') or 'not in PATH'}"
        )

    def _apply_filter(self) -> None:
        query = self.search_var.get().strip().lower()
        cat = self.category_var.get()

        def matches(s: NseScript) -> bool:
            if cat != "(all)" and cat not in s.categories:
                return False
            if not query:
                return True
            hay = " ".join(
                [
                    s.name,
                    s.stem,
                    s.description,
                    s.author,
                    " ".join(s.categories),
                    s.usage,
                ]
            ).lower()
            return query in hay

        self.filtered = [s for s in self.scripts if matches(s)]

        self.listbox.delete(*self.listbox.get_children())
        for s in self.filtered:
            self.listbox.insert(
                "",
                END,
                iid=s.name,
                text=s.stem,
                values=(", ".join(s.categories),),
            )

        self.status_var.set(
            f"Showing {len(self.filtered)} / {len(self.scripts)} scripts"
        )

    def _selected_script(self) -> NseScript | None:
        sel = self.listbox.selection()
        if not sel:
            return None
        name = sel[0]
        for s in self.filtered:
            if s.name == name:
                return s
        return None

    def _on_select(self, _event=None) -> None:
        script = self._selected_script()
        if not script:
            return

        self.detail_text.delete("1.0", END)
        self.detail_text.insert(END, format_script_details(script))
        self._fetch_nmap_help_async(script)

    def _fetch_nmap_help_async(self, script: NseScript) -> None:
        if self._load_task and self._load_task.is_alive():
            return

        def worker() -> None:
            help_text = self._get_nmap_help(script.stem)
            if help_text is None:
                return

            def update() -> None:
                current = self._selected_script()
                if not current or current.stem != script.stem:
                    return
                self.detail_text.delete("1.0", END)
                self.detail_text.insert(
                    END, format_script_details(script, nmap_help=help_text)
                )

            self.root.after(0, update)

        self._load_task = threading.Thread(target=worker, daemon=True)
        self._load_task.start()

    def _get_nmap_help(self, stem: str) -> str | None:
        if stem in self._help_cache:
            return self._help_cache[stem]

        nmap = shutil.which("nmap")
        if not nmap:
            return None

        try:
            proc = subprocess.run(
                [nmap, "--script-help", stem],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            text = proc.stdout if proc.returncode == 0 else proc.stderr
            if text.strip():
                self._help_cache[stem] = text
                return text
        except (OSError, subprocess.TimeoutExpired):
            pass
        return None

    def _open_docs(self) -> None:
        script = self._selected_script()
        if not script:
            messagebox.showinfo(APP_TITLE, "Please select a script first.")
            return
        import webbrowser

        webbrowser.open(script.nsedoc_url)

    def _copy_command(self) -> None:
        script = self._selected_script()
        if not script:
            messagebox.showinfo(APP_TITLE, "Please select a script first.")
            return
        cmd = f"nmap --script {script.stem} <target>"
        self.root.clipboard_clear()
        self.root.clipboard_append(cmd)
        self.status_var.set(f"Copied: {cmd}")

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    scripts_dir = find_scripts_dir()
    if not scripts_dir:
        root = Tk()
        root.withdraw()
        messagebox.showerror(
            APP_TITLE,
            "Nmap NSE scripts directory not found.\n\n"
            "Install nmap, or set:\n"
            "  NSE_SCRIPTS_DIR=/path/to/nmap/scripts",
        )
        return 1

    app = NseDiscoverApp(scripts_dir)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
