from lab4_graphics_fixed import db_config

import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2 import sql

# === Настройки подключения ===
DB_CONFIG = db_config

# === Глобальные параметры ===
PARTITION_COLUMNS = ['id', 'order_date', 'session_date', 'customer', 'movie', 'quantity', 'price']
PARTITION_TYPES = ['RANGE', 'LIST', 'HASH']

class PartitioningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PostgreSQL Partitioning GUI")
        self.root.geometry("800x600")

        # Переменные для выбора
        self.selected_column = tk.StringVar()
        self.selected_type = tk.StringVar()
        self.selected_partition = tk.StringVar()

        # === Интерфейс ===
        # === Настройка партиционирования ===
        setup_frame = ttk.LabelFrame(root, text="Создание партиционированной таблицы")
        setup_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(setup_frame, text="Выберите столбец для партиционирования:").pack(pady=5)
        self.column_combo = ttk.Combobox(setup_frame, textvariable=self.selected_column, values=PARTITION_COLUMNS, state="readonly")
        self.column_combo.pack(pady=5)

        ttk.Label(setup_frame, text="Выберите тип партиционирования:").pack(pady=5)
        self.type_combo = ttk.Combobox(setup_frame, textvariable=self.selected_type, values=PARTITION_TYPES, state="readonly")
        self.type_combo.pack(pady=5)

        self.details_frame = ttk.Frame(setup_frame)
        self.details_frame.pack(pady=10, fill='x', padx=20)

        self.params_widgets = []

        self.selected_column.trace('w', self.on_column_change)
        self.selected_type.trace('w', self.on_type_change)

        self.apply_btn = ttk.Button(setup_frame, text="Создать партиционированную таблицу", command=self.create_partitioned_table)
        self.apply_btn.pack(pady=20)

        # === Отображение данных из партиции ===
        data_frame = ttk.LabelFrame(root, text="Просмотр данных партиции")
        data_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(data_frame, text="Выберите партицию:").pack(pady=5)
        self.partition_combo = ttk.Combobox(data_frame, textvariable=self.selected_partition, state="readonly", width=50)
        self.partition_combo.pack(pady=5)

        refresh_btn = ttk.Button(data_frame, text="Обновить список партиций", command=self.refresh_partitions)
        refresh_btn.pack(pady=5)

        show_btn = ttk.Button(data_frame, text="Показать данные", command=self.show_partition_data)
        show_btn.pack(pady=5)

        # === Treeview для отображения данных ===
        tree_frame = ttk.Frame(root)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, show='headings')
        self.tree.pack(side='left', fill='both', expand=True)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')

    def clear_params(self):
        for widget in self.params_widgets:
            widget.destroy()
        self.params_widgets.clear()

    def on_column_change(self, *args):
        self.update_params_ui()

    def on_type_change(self, *args):
        self.update_params_ui()

    def update_params_ui(self):
        self.clear_params()
        col = self.selected_column.get()
        ptype = self.selected_type.get()

        if not col or not ptype:
            return

        if ptype == 'RANGE':
            if col in ['order_date', 'session_date']:
                ttk.Label(self.details_frame, text="Введите диапазоны дат (через запятую, например: '2024-01-01,2024-07-01,2025-01-01')").pack(anchor='w')
                self.range_entry = ttk.Entry(self.details_frame, width=60)
                self.range_entry.pack(pady=5)
                self.params_widgets.extend([self.details_frame.winfo_children()[-2], self.details_frame.winfo_children()[-1]])
            elif col in ['id', 'quantity', 'price']:
                ttk.Label(self.details_frame, text="Введите числовые границы (через запятую, например: '0,100,200')").pack(anchor='w')
                self.range_entry = ttk.Entry(self.details_frame, width=60)
                self.range_entry.pack(pady=5)
                self.params_widgets.extend([self.details_frame.winfo_children()[-2], self.details_frame.winfo_children()[-1]])
            else:
                messagebox.showerror("Ошибка", "Для этого столбца нельзя использовать RANGE-партиционирование.")
        elif ptype == 'LIST':
            if col in ['customer', 'movie']:
                ttk.Label(self.details_frame, text="Введите значения через запятую (например: 'Avatar, Titanic, Inception')").pack(anchor='w')
                self.list_entry = ttk.Entry(self.details_frame, width=60)
                self.list_entry.pack(pady=5)
                self.params_widgets.extend([self.details_frame.winfo_children()[-2], self.details_frame.winfo_children()[-1]])
            else:
                messagebox.showerror("Ошибка", "Для этого столбца нельзя использовать LIST-партиционирование.")
        elif ptype == 'HASH':
            ttk.Label(self.details_frame, text="Введите количество партиций (например: 4)").pack(anchor='w')
            self.hash_entry = ttk.Entry(self.details_frame, width=20)
            self.hash_entry.pack(pady=5)
            self.params_widgets.extend([self.details_frame.winfo_children()[-2], self.details_frame.winfo_children()[-1]])

    def create_partitioned_table(self):
        col = self.selected_column.get()
        ptype = self.selected_type.get()

        if not col or not ptype:
            messagebox.showerror("Ошибка", "Выберите столбец и тип партиционирования.")
            return

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            # Удаляем старую таблицу (осторожно!)
            cur.execute("DROP TABLE IF EXISTS orders CASCADE;")

            # Создаём партиционированную таблицу
            partition_by_clause = ""
            if ptype == 'RANGE':
                partition_by_clause = f"PARTITION BY RANGE ({col})"
            elif ptype == 'LIST':
                partition_by_clause = f"PARTITION BY LIST ({col})"
            elif ptype == 'HASH':
                partition_by_clause = f"PARTITION BY HASH ({col})"

            create_table_sql = f"""
            CREATE TABLE orders (
                id INTEGER,
                order_date DATE,
                session_date DATE,
                customer TEXT,
                movie TEXT,
                quantity INTEGER,
                price NUMERIC(10,2)
            ) {partition_by_clause};
            """
            cur.execute(create_table_sql)

            # Создание партиций
            if ptype == 'RANGE':
                bounds = self.range_entry.get().strip().split(',')
                bounds = [b.strip() for b in bounds if b.strip()]
                if len(bounds) < 2:
                    messagebox.showerror("Ошибка", "Нужно минимум две границы для RANGE.")
                    return
                for i in range(len(bounds) - 1):
                    start = bounds[i]
                    end = bounds[i + 1]
                    part_name = f"orders_{col}_{i}"
                    if 'date' in col:
                        cur.execute(sql.SQL("""
                            CREATE TABLE {} PARTITION OF orders
                            FOR VALUES FROM (%s) TO (%s);
                        """).format(sql.Identifier(part_name)), (start, end))
                    else:
                        cur.execute(sql.SQL("""
                            CREATE TABLE {} PARTITION OF orders
                            FOR VALUES FROM (%s) TO (%s);
                        """).format(sql.Identifier(part_name)), (int(start), int(end)))
            elif ptype == 'LIST':
                values = [v.strip() for v in self.list_entry.get().split(',') if v.strip()]
                for i, val in enumerate(values):
                    part_name = f"orders_{col}_{i}"
                    cur.execute(sql.SQL("""
                        CREATE TABLE {} PARTITION OF orders
                        FOR VALUES IN (%s);
                    """).format(sql.Identifier(part_name)), (val,))
            elif ptype == 'HASH':
                try:
                    num_partitions = int(self.hash_entry.get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректное число партиций.")
                    return
                for i in range(num_partitions):
                    part_name = f"orders_{col}_hash_{i}"
                    cur.execute(sql.SQL("""
                        CREATE TABLE {} PARTITION OF orders
                        FOR VALUES WITH (MODULUS %s, REMAINDER %s);
                    """).format(sql.Identifier(part_name)), (num_partitions, i))

            conn.commit()
            messagebox.showinfo("Успех", f"Таблица orders успешно партиционирована по {col} ({ptype})!")
            self.refresh_partitions()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать партиции:\n{e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def refresh_partitions(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            # Запрос на получение списка партиций
            cur.execute("""
                SELECT partitiontablename
                FROM pg_partitions
                WHERE schemaname = 'public' AND tablename = 'orders';
            """)
            partitions = [row[0] for row in cur.fetchall()]

            self.partition_combo['values'] = partitions
            if partitions:
                self.selected_partition.set(partitions[0])
            else:
                self.selected_partition.set("")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список партиций:\n{e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def show_partition_data(self):
        partition_name = self.selected_partition.get()
        if not partition_name:
            messagebox.showwarning("Предупреждение", "Выберите партицию для отображения.")
            return

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()

            # Очищаем Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Получаем структуру таблицы (столбцы)
            cur.execute(f"SELECT * FROM {partition_name} LIMIT 0;")
            colnames = [desc[0] for desc in cur.description]

            # Обновляем заголовки Treeview
            self.tree['columns'] = colnames
            for col in colnames:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, anchor='center')

            # Выполняем запрос на получение данных
            cur.execute(f"SELECT * FROM {partition_name};")
            rows = cur.fetchall()

            # Вставляем данные в Treeview
            for row in rows:
                self.tree.insert('', 'end', values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные из партиции:\n{e}")
        finally:
            if 'conn' in locals():
                conn.close()

# === Запуск приложения ===
if __name__ == "__main__":
    root = tk.Tk()
    app = PartitioningApp(root)
    root.mainloop()
