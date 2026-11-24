"""
virtual_disk.py - Operating System part of the project.

Creates REAL text files inside the "virtual_disk" folder and simulates disk
block allocation (contiguous / linked / indexed) and file load times.
"""
import os
from math import ceil
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DISK_ROOT = APP_DIR / "virtual_disk"
BLOCK_SIZE = 1024
TOTAL_BLOCKS = 2048


class VirtualDisk:
    def __init__(self):
        DISK_ROOT.mkdir(exist_ok=True)
        self.used = set()
        self.entries = {}
        self.directories = {"/"}
        self._load_existing()

    def _load_existing(self):
        # Restore app-created files after restart; allocation is rebuilt in path order.
        for folder, dirs, filenames in os.walk(DISK_ROOT):
            rel_folder = Path(folder).relative_to(DISK_ROOT)
            virt_folder = "/" if str(rel_folder) == "." else "/" + rel_folder.as_posix()
            self.mkdir(virt_folder)
            for name in filenames:
                if name.startswith("."):
                    continue
                full = Path(folder) / name
                virt = self.normalize((virt_folder.rstrip("/") + "/" + name))
                try:
                    size = full.stat().st_size
                    self._allocate_entry(virt, size, "indexed", persist=False)
                except (OSError, ValueError):
                    pass

    @staticmethod
    def normalize(path):
        parts = [p for p in str(path).replace("\\", "/").split("/") if p and p != "."]
        if any(p == ".." for p in parts):
            raise ValueError("Parent-directory '..' paths are not allowed.")
        return "/" + "/".join(parts) if parts else "/"

    def real_path(self, virtual_path):
        virtual_path = self.normalize(virtual_path)
        return DISK_ROOT.joinpath(*virtual_path.strip("/").split("/"))

    def mkdir(self, path):
        path = self.normalize(path)
        current = ""
        for part in path.strip("/").split("/") if path != "/" else []:
            current += "/" + part
            self.directories.add(current)
        self.real_path(path).mkdir(parents=True, exist_ok=True)
        return path

    def _free(self):
        return [b for b in range(TOTAL_BLOCKS) if b not in self.used]

    def _allocate_entry(self, path, size, method, persist=True):
        needed = max(1, ceil(size / BLOCK_SIZE))
        free = self._free()
        if len(free) < needed:
            raise ValueError("Virtual disk is full.")
        if method == "contiguous":
            run_start = None
            run_len = 0
            prev = None
            start = None
            for block in free:
                if prev is None or block != prev + 1:
                    run_start, run_len = block, 1
                else:
                    run_len += 1
                if run_len >= needed:
                    start = run_start
                    break
                prev = block
            if start is None:
                raise ValueError("Not enough consecutive free blocks for contiguous allocation.")
            blocks = list(range(start, start + needed))
        elif method in ("linked", "indexed"):
            blocks = free[:needed]
        else:
            raise ValueError("Choose contiguous, linked, or indexed.")
        self.used.update(blocks)
        self.entries[path] = {"size": size, "method": method, "blocks": blocks}
        return blocks

    def create_file(self, path, content, method):
        path = self.normalize(path)
        if path == "/" or path in self.entries or self.real_path(path).exists():
            raise ValueError("That file already exists.")
        parent = path.rsplit("/", 1)[0] or "/"
        if parent not in self.directories:
            raise ValueError(f"Folder {parent} does not exist. Create it first.")
        if method not in ("contiguous", "linked", "indexed"):
            raise ValueError("Invalid allocation strategy.")
        encoded = content.encode("utf-8")
        # Check/allocate before writing so allocation errors do not leave a file behind.
        blocks = self._allocate_entry(path, len(encoded), method)
        try:
            target = self.real_path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except Exception:
            self.used.difference_update(blocks)
            self.entries.pop(path, None)
            raise
        return path, len(encoded), blocks

    def list_paths(self):
        result = []
        for d in sorted(self.directories):
            if d != "/":
                result.append(("Folder", d, ""))
        for p, info in sorted(self.entries.items()):
            result.append(("File", p, f'{info["size"]} bytes | {info["method"]}'))
        return result

    def load_ms(self, path):
        entry = self.entries.get(path)
        blocks = len(entry["blocks"]) if entry else 1
        return 5.0 + blocks * 0.15
