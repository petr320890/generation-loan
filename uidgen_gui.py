# uidgen_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from uidlib import generate_uid, validate_uid, checksum_char_from_uuid, UUID_RE

APP_TITLE = "UID Generator (ГОСТ UUID + контрольный символ)"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(720, 420)

        # --- Top actions
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")

        ttk.Label(top, text="Количество:").pack(side="left")
        self.count_var = tk.StringVar(value="1")
        self.count_entry = ttk.Entry(top, width=6, textvariable=self.count_var)
        self.count_entry.pack(side="left", padx=(6, 12))

        ttk.Button(top, text="Сгенерировать", command=self.on_generate).pack(side="left")
        ttk.Button(top, text="Скопировать", command=self.on_copy).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Очистить", command=self.on_clear).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Сохранить в файл…", command=self.on_save).pack(side="left", padx=(8, 0))

        # --- Output box
        mid = ttk.Frame(self, padding=(12, 0, 12, 12))
        mid.pack(fill="both", expand=True)

        ttk.Label(mid, text="Результаты:").pack(anchor="w", pady=(8, 4))

        self.text = tk.Text(mid, wrap="none", height=12)
        self.text.pack(fill="both", expand=True)

        # scrollbars
        yscroll = ttk.Scrollbar(self.text, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")

        xscroll = ttk.Scrollbar(mid, orient="horizontal", command=self.text.xview)
        self.text.configure(xscrollcommand=xscroll.set)
        xscroll.pack(fill="x")

        # --- Validation area
        bottom = ttk.LabelFrame(self, text="Проверка / расчёт", padding=12)
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Label(bottom, text="Вставьте УИд (…-C) или UUID (36):").grid(row=0, column=0, sticky="w")

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(bottom, textvariable=self.input_var)
        self.input_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        btns = ttk.Frame(bottom)
        btns.grid(row=1, column=1, sticky="e", padx=(10, 0), pady=(6, 0))

        ttk.Button(btns, text="Проверить", command=self.on_check).pack(side="left")
        ttk.Button(btns, text="Посчитать C для UUID", command=self.on_calc_c).pack(side="left", padx=(8, 0))

        bottom.columnconfigure(0, weight=1)

        # status
        self.status_var = tk.StringVar(value="Готово.")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(12, 0, 12, 10))
        status.pack(fill="x")

        self.bind("<Control-Return>", lambda e: self.on_generate())
        self.bind("<Command-Return>", lambda e: self.on_generate())  # mac

    def _set_status(self, s: str):
        self.status_var.set(s)

    def on_generate(self):
        raw = self.count_var.get().strip()
        try:
            n = int(raw)
            if n < 1 or n > 5000:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть числом от 1 до 5000.")
            return

        lines = [generate_uid() for _ in range(n)]
        if self.text.get("1.0", "end").strip():
            self.text.insert("end", "\n")
        self.text.insert("end", "\n".join(lines))
        self.text.see("end")
        self._set_status(f"Сгенерировано: {n}")

    def on_copy(self):
        content = self.text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Копирование", "Нечего копировать.")
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        self._set_status("Скопировано в буфер обмена.")

    def on_clear(self):
        self.text.delete("1.0", "end")
        self._set_status("Очищено.")

    def on_save(self):
        content = self.text.get("1.0", "end").strip()
        if not content:
            messagebox.showinfo("Сохранение", "Нечего сохранять.")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"uids_{ts}.txt"
        path = filedialog.asksaveasfilename(
            title="Сохранить результаты",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        self._set_status(f"Сохранено: {path}")

    def on_check(self):
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("Проверка", "Введите значение для проверки.")
            return

        ok = validate_uid(s)
        if ok:
            messagebox.showinfo("Проверка", "OK — контрольный символ корректен.")
            self._set_status("Проверка: OK")
        else:
            messagebox.showwarning("Проверка", "FAIL — неверный формат или контрольный символ.")
            self._set_status("Проверка: FAIL")

    def on_calc_c(self):
        s = self.input_var.get().strip()
        if not s:
            messagebox.showinfo("Расчёт", "Введите UUID (36 символов) для расчёта контрольного символа.")
            return
        if not UUID_RE.match(s):
            messagebox.showerror("Ошибка", "Ожидается UUID формата 8-4-4-4-12 (36 символов).")
            return

        c = checksum_char_from_uuid(s.lower())
        messagebox.showinfo("Контрольный символ", f"C = {c}\nПолный УИд:\n{s.lower()}-{c}")
        self._set_status(f"Расчитан C={c}")

if __name__ == "__main__":
    App().mainloop()