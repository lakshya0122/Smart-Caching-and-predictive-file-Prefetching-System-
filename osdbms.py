"""
Predictive File System - PBL Demo
Python 3.10+
GUI: Tkinter (included with most Python installations)
Database: SQLite (included with Python)

main.py - user interface and program entry point.
Run this file:   python main.py

It connects the other three files:
    database.py         -> Store            (file metadata + access log)
    virtual_disk.py     -> VirtualDisk      (real files + simulated block allocation)
    prediction_cache.py -> Predictor, Cache (Markov prediction + LRU cache)
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from database import Store, DB_PATH, now_text
from virtual_disk import VirtualDisk, DISK_ROOT
from prediction_cache import Predictor, Cache, CACHE_CAPACITY


class PredictiveFileSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Predictive File System | PBL Project")
        self.root.geometry("1120x720")
        self.root.minsize(920, 600)
        self.store = Store()
        self.disk = VirtualDisk()
        self.predictor = Predictor()
        self.cache = Cache()
        self._style()
        self._build_ui()
        self.refresh_all()
        self.status.set(f"Ready. Files are stored inside: {DISK_ROOT}")

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", rowheight=25)
        style.configure("Accent.TButton", padding=6)

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=(16, 12))
        header.pack(fill="x")
        ttk.Label(header, text="Predictive File System", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="File-system simulation • Access logging • Markov prediction • LRU cache").pack(anchor="w", pady=(3, 0))

        body = ttk.Panedwindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        left = ttk.Frame(body, padding=8)
        right = ttk.Frame(body, padding=8)
        body.add(left, weight=3)
        body.add(right, weight=4)

        ttk.Label(left, text="Virtual Directory", style="Section.TLabel").pack(anchor="w")
        self.file_tree = ttk.Treeview(left, columns=("type", "details"), show="tree headings", height=18)
        self.file_tree.heading("#0", text="Path")
        self.file_tree.heading("type", text="Type")
        self.file_tree.heading("details", text="Details")
        self.file_tree.column("#0", width=240)
        self.file_tree.column("type", width=65)
        self.file_tree.column("details", width=145)
        self.file_tree.pack(fill="both", expand=True, pady=(6, 8))

        btns = ttk.Frame(left)
        btns.pack(fill="x")
        ttk.Button(btns, text="Create Folder", command=self.create_folder).pack(fill="x", pady=2)
        ttk.Button(btns, text="Create Text File", command=self.create_file).pack(fill="x", pady=2)
        ttk.Button(btns, text="Open Selected File", command=self.open_selected).pack(fill="x", pady=2)
        ttk.Button(btns, text="Refresh", command=self.refresh_all).pack(fill="x", pady=2)

        ttk.Label(right, text="Prediction & Cache Status", style="Section.TLabel").pack(anchor="w")
        self.status = tk.StringVar(value="Starting...")
        ttk.Label(right, textvariable=self.status, wraplength=570).pack(anchor="w", pady=(5, 8))

        metric_frame = ttk.LabelFrame(right, text="Live Cache Metrics", padding=8)
        metric_frame.pack(fill="x", pady=(0, 10))
        self.metric_vars = {}
        metric_names = [
            ("hits", "Cache hits"), ("misses", "Cache misses"),
            ("hit_rate", "Hit rate"), ("prefetches", "Prefetches"),
            ("useful", "Useful prefetches"), ("wasted", "Wasted prefetches"),
            ("load", "Simulated demand load")
        ]
        for i, (key, label) in enumerate(metric_names):
            r, c = divmod(i, 2)
            cell = ttk.Frame(metric_frame)
            cell.grid(row=r, column=c, sticky="ew", padx=6, pady=3)
            ttk.Label(cell, text=label + ":").pack(side="left")
            var = tk.StringVar(value="0")
            ttk.Label(cell, textvariable=var, font=("Segoe UI", 10, "bold")).pack(side="left", padx=4)
            self.metric_vars[key] = var
        metric_frame.columnconfigure(0, weight=1)
        metric_frame.columnconfigure(1, weight=1)

        tabs = ttk.Notebook(right)
        tabs.pack(fill="both", expand=True)
        pred_tab = ttk.Frame(tabs, padding=6)
        logs_tab = ttk.Frame(tabs, padding=6)
        tabs.add(pred_tab, text="Learned Transitions")
        tabs.add(logs_tab, text="Access History")

        self.pred_tree = ttk.Treeview(pred_tab, columns=("next", "prob", "count"), show="headings")
        for col, title, width in [("next", "Predicted next file", 260), ("prob", "Probability", 90), ("count", "Count", 70)]:
            self.pred_tree.heading(col, text=title)
            self.pred_tree.column(col, width=width)
        self.pred_tree.pack(fill="both", expand=True)

        self.log_tree = ttk.Treeview(logs_tab, columns=("seq", "path", "time"), show="headings")
        for col, title, width in [("seq", "Seq.", 55), ("path", "Opened file", 230), ("time", "Timestamp", 160)]:
            self.log_tree.heading(col, text=title)
            self.log_tree.column(col, width=width)
        self.log_tree.pack(fill="both", expand=True)

        footer = ttk.Frame(self.root, padding=(12, 0, 12, 10))
        footer.pack(fill="x")
        ttk.Button(footer, text="Run LRU vs Predictive Benchmark", command=self.benchmark, style="Accent.TButton").pack(side="left")
        ttk.Button(footer, text="Open Data Folder", command=self.show_data_folder).pack(side="left", padx=8)
        ttk.Label(footer, text="Allocation blocks and load times are simulated.", foreground="#555").pack(side="right")

    def selected_path(self):
        selection = self.file_tree.selection()
        return self.file_tree.item(selection[0], "values")[0] if selection else None

    def create_folder(self):
        path = simpledialog.askstring("Create Folder", "Enter folder path (example: /study):", parent=self.root)
        if not path:
            return
        try:
            result = self.disk.mkdir(path)
            self.status.set(f"Folder created: {result}")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Cannot create folder", str(exc))

    def create_file(self):
        path = simpledialog.askstring("Create Text File", "Enter file path (example: /study/OS.txt):", parent=self.root)
        if not path:
            return
        content = simpledialog.askstring("File Content", "Enter text content for this file:", parent=self.root)
        if content is None:
            return
        method = simpledialog.askstring(
            "Disk Allocation", "Choose: contiguous, linked, or indexed", initialvalue="indexed", parent=self.root
        )
        if not method:
            return
        method = method.strip().lower()
        try:
            virt_path, size, blocks = self.disk.create_file(path, content, method)
            entry = self.disk.entries[virt_path]
            self.store.save_file(virt_path, size, method, blocks, now_text())
            self.status.set(f"Created real text file {virt_path} ({size} bytes), allocation={method}, blocks={blocks}")
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Cannot create file", str(exc))

    def open_selected(self):
        path = self.selected_path()
        if not path:
            messagebox.showinfo("Select a file", "Select a file row in the directory tree first.")
            return
        if path not in self.disk.entries:
            messagebox.showinfo("Folder selected", "Select a file, not a folder.")
            return
        real = self.disk.real_path(path)
        try:
            content = real.read_text(encoding="utf-8")
        except Exception as exc:
            messagebox.showerror("Cannot open file", str(exc))
            return

        self.store.log_access(path)
        hit = self.cache.access(path, self.disk.load_ms(path))
        self.predictor.train(self.store.sequence())
        predicted, probability = self.predictor.predict(path, exclude=self.cache.items.keys())
        message = f"{'CACHE HIT' if hit else 'CACHE MISS'}: {path}"
        if predicted:
            if self.cache.prefetch(predicted):
                message += f"\nPredicted and prefetched: {predicted} ({probability:.1%})"
            else:
                message += f"\nPrediction: {predicted} ({probability:.1%}); already cached"
        else:
            message += "\nNo transition prediction yet. Open files in a repeated sequence."
        self.status.set(message)
        self.refresh_all()
        self.show_file_content(path, content)

    def show_file_content(self, path, content):
        win = tk.Toplevel(self.root)
        win.title("Opened: " + path)
        win.geometry("600x400")
        ttk.Label(win, text=path, font=("Segoe UI", 11, "bold"), padding=8).pack(anchor="w")
        box = tk.Text(win, wrap="word")
        box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        box.insert("1.0", content)
        box.configure(state="disabled")

    def refresh_all(self):
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        for kind, path, details in self.disk.list_paths():
            self.file_tree.insert("", "end", text=path, values=(path, kind, details))
        self.predictor.train(self.store.sequence())
        for item in self.pred_tree.get_children():
            self.pred_tree.delete(item)
        for src, dest, probability, count in self.predictor.table():
            self.pred_tree.insert("", "end", values=(f"{src}  →  {dest}", probability, count))
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        for seq, path, timestamp in self.store.logs():
            self.log_tree.insert("", "end", values=(seq, path, timestamp))
        c = self.cache
        self.metric_vars["hits"].set(str(c.hits))
        self.metric_vars["misses"].set(str(c.misses))
        total = c.hits + c.misses
        self.metric_vars["hit_rate"].set(f"{(100*c.hits/total if total else 0):.1f}%")
        self.metric_vars["prefetches"].set(str(c.prefetches))
        self.metric_vars["useful"].set(str(c.useful))
        self.metric_vars["wasted"].set(str(c.wasted))
        self.metric_vars["load"].set(f"{c.load_ms:.2f} ms")

    def benchmark(self):
        seq = self.store.sequence()
        if len(seq) < 5:
            messagebox.showinfo(
                "More access history needed",
                "Open files in a repeated sequence at least 5 times, then run the benchmark."
            )
            return
        split = min(max(int(len(seq) * 0.6), 2), len(seq) - 1)
        train, test = seq[:split], seq[split:]
        predictor = Predictor()
        predictor.train(train)
        baseline = Cache(CACHE_CAPACITY)
        predictive = Cache(CACHE_CAPACITY)
        for path in test:
            baseline.access(path, self.disk.load_ms(path))
        observed = list(train)
        for path in test:
            predictive.access(path, self.disk.load_ms(path))
            predictor.train(observed)
            predicted, _ = predictor.predict(path, exclude=predictive.items.keys())
            if predicted:
                predictive.prefetch(predicted)
            observed.append(path)
        baseline.finish()
        predictive.finish()

        def line(name, cache):
            total = cache.hits + cache.misses
            hit_rate = 100 * cache.hits / total if total else 0
            accuracy = 100 * cache.useful / cache.prefetches if cache.prefetches else 0
            return (f"{name}\n"
                    f"  Cache hit rate: {hit_rate:.1f}%\n"
                    f"  Hits / misses: {cache.hits} / {cache.misses}\n"
                    f"  Prefetches: {cache.prefetches}; useful: {cache.useful}; wasted: {cache.wasted}\n"
                    f"  Prefetch accuracy: {accuracy:.1f}%\n"
                    f"  Simulated demand load: {cache.load_ms:.2f} ms")
        messagebox.showinfo(
            "Benchmark Results",
            f"Chronological split: {len(train)} training accesses, {len(test)} test accesses.\n\n"
            + line("LRU baseline", baseline) + "\n\n" + line("Predictive cache", predictive)
            + "\n\nNote: timings are simulated. This small benchmark is illustrative, not a hardware performance measurement."
        )

    def show_data_folder(self):
        messagebox.showinfo(
            "Project data folder",
            f"Real text files are stored in:\n{DISK_ROOT}\n\n"
            f"SQLite database:\n{DB_PATH}\n\n"
            "You can open these folders from File Explorer."
        )

    def close(self):
        self.store.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = PredictiveFileSystemApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == "__main__":
    main()
