#!/usr/bin/env python3
# gui_sql_psycopg2.py
# Требует: psycopg2, tkinter (в стандартной библиотеке)
# Установить psycopg2: pip install psycopg2-binary

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2
import threading
import traceback

# ---------- Настройки подключения: заполни свои данные ----------
DB_CONFIG = {
    "dbname": "newdb",
    "user": "simafrus",
    "password": "8bzm61K"
}
# ----------------------------------------------------------------

class SQLGui:
    def __init__(self, root):
        self.root = root
        root.title("SQL Runner (psycopg2 + tkinter)")

        # Верх: подключение (инфо)
        conn_frame = ttk.Frame(root, padding=6)
        conn_frame.pack(fill="x")
        ttk.Label(conn_frame, text="Postgres host:port/db (из DB_CONFIG)").pack(side="left")

        # SQL ввод
        input_frame = ttk.LabelFrame(root, text="SQL запрос", padding=6)
        input_frame.pack(fill="both", expand=False, padx=6, pady=(4,6))

        self.sql_text = scrolledtext.ScrolledText(input_frame, height=6, wrap="none")
        self.sql_text.pack(fill="both", expand=True)
        # пример запроса
        self.sql_text.insert("1.0", "SELECT * FROM sensors LIMIT 100;")

        # Кнопка выполнить
        btn_frame = ttk.Frame(root, padding=6)
        btn_frame.pack(fill="x")
        self.exec_btn = ttk.Button(btn_frame, text="Выполнить SQL", command=self.on_execute)
        self.exec_btn.pack(side="left")
        self.clear_btn = ttk.Button(btn_frame, text="Очистить результаты", command=self.clear_results)
        self.clear_btn.pack(side="left", padx=(6,0))
        self.status_label = ttk.Label(btn_frame, text="", foreground="blue")
        self.status_label.pack(side="left", padx=(10,0))

        # Разделитель результатов
        panes = ttk.Panedwindow(root, orient="vertical")
        panes.pack(fill="both", expand=True, padx=6, pady=6)

        # Результат запроса (Treeview)
        result_frame = ttk.LabelFrame(panes, text="Результат запроса", padding=6)
        panes.add(result_frame, weight=3)

        self.tree = ttk.Treeview(result_frame, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll_y = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_y.pack(side="left", fill="y")
        self.tree.configure(yscrollcommand=tree_scroll_y.set)
        tree_scroll_x = ttk.Scrollbar(result_frame, orient="horizontal", command=self.tree.xview)
        tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=tree_scroll_x.set)

        # EXPLAIN ANALYZE вывод
        explain_frame = ttk.LabelFrame(panes, text="EXPLAIN ANALYZE", padding=6)
        panes.add(explain_frame, weight=1)

        self.explain_text = scrolledtext.ScrolledText(explain_frame, height=12, wrap="word")
        self.explain_text.pack(fill="both", expand=True)

    def clear_results(self):
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()
        self.explain_text.delete("1.0", tk.END)
        self.status_label.config(text="")

    def on_execute(self):
        sql = self.sql_text.get("1.0", tk.END).strip()
        if not sql:
            messagebox.showinfo("Info", "Введите SQL-запрос.")
            return

        # Блокируем кнопку и запускаем выполнение в потоке
        self.exec_btn.config(state="disabled")
        self.clear_btn.config(state="disabled")
        self.status_label.config(text="Выполняется...")
        thread = threading.Thread(target=self._execute_worker, args=(sql,), daemon=True)
        thread.start()

    def _execute_worker(self, sql):
        """
        Выполняет запрос и EXPLAIN ANALYZE, затем обновляет GUI через root.after.
        Всё взаимодействие с tkinter должно идти через root.after.
        """
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
        except Exception as e:
            tb = traceback.format_exc()
            self.root.after(0, self._on_error, "Ошибка подключения: " + str(e), tb)
            return

        try:
            # Попытка выполнить основной запрос:
            # Если запрос возвращает строки -> fetchall и отобразить
            # И затем выполнить EXPLAIN ANALYZE <query>
            # Для простоты: определяем тип по первому слову
            first_word = sql.strip().split()[0].lower()
            is_select = first_word == "select" or sql.strip().lower().startswith("with ")

            if is_select:
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description] if cur.description else []
                # prepare result for GUI
                result = {"type": "select", "columns": columns, "rows": rows}
            else:
                # DDL/DML
                cur.execute(sql)
                conn.commit()
                rowcount = cur.rowcount
                result = {"type": "nonselect", "rowcount": rowcount}

            # EXPLAIN ANALYZE (выполняется отдельно) — мы хотим показать план и время.
            # Оборачиваем запрос в EXPLAIN ANALYZE. Для безопасности, если запрос содержит
            # символы конца транзакции или т.д. — всё равно выполняем напрямую.
            explain_sql = "EXPLAIN (ANALYZE, BUFFERS, VERBOSE) " + sql
            try:
                cur.execute(explain_sql)
                explain_rows = cur.fetchall()
                explain_text = "\n".join(r[0] for r in explain_rows)
            except Exception as e:
                # Если EXPLAIN не сработал (например для некоторых команд), сохранить ошибку
                explain_text = f"Не удалось выполнить EXPLAIN ANALYZE: {e}"

            cur.close()
            conn.close()

            # Передаём результаты в GUI-поток
            self.root.after(0, self._on_success, result, explain_text)

        except Exception as e:
            tb = traceback.format_exc()
            self.root.after(0, self._on_error, "Ошибка выполнения запроса: " + str(e), tb)
        finally:
            # разблокировка кнопок будет в _on_success/_on_error
            pass

    def _on_success(self, result, explain_text):
        # обновляем GUI
        self.clear_results()
        if result["type"] == "select":
            cols = result["columns"]
            rows = result["rows"]
            self.tree["columns"] = cols
            # Устанавливаем ширину столбцов динамически
            for c in cols:
                self.tree.heading(c, text=c)
                self.tree.column(c, width=120, anchor="w")

            # вставляем данные (обрезаем большие строки)
            for r in rows:
                display_row = []
                for v in r:
                    if v is None:
                        display_row.append("NULL")
                    else:
                        s = str(v)
                        # лимит длины ячейки для удобства отображения
                        if len(s) > 500:
                            s = s[:500] + " ...(truncated)"
                        display_row.append(s)
                self.tree.insert("", "end", values=display_row)

            self.status_label.config(text=f"Строк: {len(rows)}")
        else:
            rc = result.get("rowcount", -1)
            self.status_label.config(text=f"Affected rows: {rc}")
            # Для немедленных команд покажем маленькую таблицу с одной колонкой
            self.tree["columns"] = ("info",)
            self.tree.heading("info", text="Info")
            self.tree.column("info", width=500, anchor="w")
            self.tree.insert("", "end", values=(f"Affected rows: {rc}",))

        # explain
        self.explain_text.insert("1.0", explain_text)
        self.exec_btn.config(state="normal")
        self.clear_btn.config(state="normal")

    def _on_error(self, message, tb):
        self.exec_btn.config(state="normal")
        self.clear_btn.config(state="normal")
        self.status_label.config(text="Ошибка")
        messagebox.showerror("Ошибка", f"{message}\n\nПодробности в консоли.")
        print("Traceback:\n", tb)


def main():
    root = tk.Tk()
    app = SQLGui(root)
    root.geometry("1000x700")
    root.mainloop()

if __name__ == "__main__":
    main()

