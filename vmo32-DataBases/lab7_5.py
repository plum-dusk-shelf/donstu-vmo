import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2
from psycopg2 import sql
from datetime import datetime
import threading

class TablePartitioner:
    def __init__(self, root):
        self.root = root
        self.root.title("PostgreSQL Table Partitioner")
        self.root.geometry("1000x700")
        
        # Параметры подключения
        self.db_params = {}
        
        # Создаем интерфейс
        self.create_widgets()
        
    def create_widgets(self):
        # Фрейм для подключения к БД
        conn_frame = ttk.LabelFrame(self.root, text="Подключение к базе данных", padding=10)
        conn_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        ttk.Label(conn_frame, text="База данных:").grid(row=1, column=0, padx=5, pady=5)
        self.db_entry = ttk.Entry(conn_frame, width=20)
        self.db_entry.grid(row=1, column=1, padx=5, pady=5)
        self.db_entry.insert(0, "myfirstdb")
        
        ttk.Label(conn_frame, text="Пользователь:").grid(row=1, column=2, padx=5, pady=5)
        self.user_entry = ttk.Entry(conn_frame, width=20)
        self.user_entry.grid(row=1, column=3, padx=5, pady=5)
        self.user_entry.insert(0, "simafrus")
        
        ttk.Label(conn_frame, text="Пароль:").grid(row=2, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(conn_frame, width=20, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        self.password_entry.insert(0, "simafrus")
        
        # Кнопки подключения/отключения
        self.connect_btn = ttk.Button(conn_frame, text="Подключиться", command=self.connect_db)
        self.connect_btn.grid(row=2, column=2, padx=5, pady=5)
        
        self.disconnect_btn = ttk.Button(conn_frame, text="Отключиться", command=self.disconnect_db, state="disabled")
        self.disconnect_btn.grid(row=2, column=3, padx=5, pady=5)
        
        # Фрейм для выбора метода партиционирования
        method_frame = ttk.LabelFrame(self.root, text="Метод партиционирования", padding=10)
        method_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Переменные для выбора
        self.partition_method = tk.StringVar(value="range")
        self.partition_column = tk.StringVar()
        self.partition_count = tk.IntVar(value=4)
        
        # Радиокнопки для методов партиционирования
        methods = [
            ("RANGE (по диапазону значений)", "range"),
            ("LIST (по списку значений)", "list"),
            ("HASH (хэш-партиционирование)", "hash")
        ]
        
        for i, (text, value) in enumerate(methods):
            ttk.Radiobutton(method_frame, text=text, variable=self.partition_method, 
                           value=value).grid(row=i, column=0, sticky="w", padx=5, pady=5)
        
        # Выбор столбца для партиционирования
        ttk.Label(method_frame, text="Столбец для партиционирования:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        self.column_combo = ttk.Combobox(method_frame, textvariable=self.partition_column, 
                                        state="readonly", width=30)
        self.column_combo.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        
        # Параметры для RANGE партиционирования
        self.range_frame = ttk.LabelFrame(method_frame, text="Параметры RANGE партиционирования", padding=5)
        self.range_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=10)
        
        ttk.Label(self.range_frame, text="Начальное значение:").grid(row=0, column=0, padx=5, pady=5)
        self.range_start = ttk.Entry(self.range_frame, width=15)
        self.range_start.grid(row=0, column=1, padx=5, pady=5)
        self.range_start.insert(0, "1")
        
        ttk.Label(self.range_frame, text="Шаг интервала:").grid(row=0, column=2, padx=5, pady=5)
        self.range_step = ttk.Entry(self.range_frame, width=15)
        self.range_step.grid(row=0, column=3, padx=5, pady=5)
        self.range_step.insert(0, "1000")
        
        ttk.Label(self.range_frame, text="Количество партиций:").grid(row=1, column=0, padx=5, pady=5)
        self.range_count = ttk.Entry(self.range_frame, width=15)
        self.range_count.grid(row=1, column=1, padx=5, pady=5)
        self.range_count.insert(0, "4")
        
        # Параметры для LIST партиционирования
        self.list_frame = ttk.LabelFrame(method_frame, text="Параметры LIST партиционирования", padding=5)
        self.list_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=10)
        
        ttk.Label(self.list_frame, text="Значения для партиций (через запятую):").grid(row=0, column=0, padx=5, pady=5)
        self.list_values = scrolledtext.ScrolledText(self.list_frame, width=40, height=4)
        self.list_values.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Параметры для HASH партиционирования
        self.hash_frame = ttk.LabelFrame(method_frame, text="Параметры HASH партиционирования", padding=5)
        self.hash_frame.grid(row=7, column=0, sticky="ew", padx=5, pady=10)
        
        ttk.Label(self.hash_frame, text="Количество партиций:").grid(row=0, column=0, padx=5, pady=5)
        self.hash_count = ttk.Entry(self.hash_frame, width=15)
        self.hash_count.grid(row=0, column=1, padx=5, pady=5)
        self.hash_count.insert(0, "4")
        
        # Скрываем все фреймы параметров изначально
        self.hide_all_param_frames()
        
        # Фрейм для дополнительных опций
        options_frame = ttk.LabelFrame(self.root, text="Дополнительные опции", padding=10)
        options_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        # Чекбоксы
        self.keep_original = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Сохранить исходную таблицу", 
                       variable=self.keep_original).grid(row=0, column=0, sticky="w", pady=5)
        
        self.include_indexes = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Включить индексы", 
                       variable=self.include_indexes).grid(row=1, column=0, sticky="w", pady=5)
        
        self.include_constraints = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Включить ограничения", 
                       variable=self.include_constraints).grid(row=2, column=0, sticky="w", pady=5)
        
        # Фрейм для информации о таблице
        info_frame = ttk.LabelFrame(self.root, text="Информация о таблице", padding=10)
        info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.table_info = scrolledtext.ScrolledText(info_frame, width=80, height=8)
        self.table_info.grid(row=0, column=0, sticky="ew")
        
        # Фрейм для SQL запросов
        sql_frame = ttk.LabelFrame(self.root, text="SQL запросы", padding=10)
        sql_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        self.sql_output = scrolledtext.ScrolledText(sql_frame, width=80, height=10)
        self.sql_output.grid(row=0, column=0, sticky="ew")
        
        # Фрейм для управления
        control_frame = ttk.Frame(self.root)
        control_frame.grid(row=1, column=2, rowspan=3, sticky="nsew", padx=10, pady=10)
        
        # Кнопка для получения информации о таблице
        self.info_btn = ttk.Button(control_frame, text="Получить информацию о таблице", 
                                  command=self.get_table_info, state="disabled")
        self.info_btn.pack(fill="x", pady=5)
        
        # Кнопка для предварительного просмотра SQL
        self.preview_btn = ttk.Button(control_frame, text="Предварительный просмотр SQL", 
                                     command=self.preview_sql, state="disabled")
        self.preview_btn.pack(fill="x", pady=5)
        
        # Кнопка для выполнения партиционирования
        self.execute_btn = ttk.Button(control_frame, text="Выполнить партиционирование", 
                                     command=self.execute_partitioning, state="disabled")
        self.execute_btn.pack(fill="x", pady=5)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(control_frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=10)
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Не подключено к базе данных", relief="sunken")
        self.status_bar.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        # Привязка события изменения метода партиционирования
        self.partition_method.trace("w", self.on_method_change)
        
        # Настройка весов строк и столбцов
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
    def hide_all_param_frames(self):
        """Скрыть все фреймы параметров"""
        self.range_frame.grid_remove()
        self.list_frame.grid_remove()
        self.hash_frame.grid_remove()
        
    def on_method_change(self, *args):
        """Обработчик изменения метода партиционирования"""
        method = self.partition_method.get()
        self.hide_all_param_frames()
        
        if method == "range":
            self.range_frame.grid()
        elif method == "list":
            self.list_frame.grid()
        elif method == "hash":
            self.hash_frame.grid()
            
    def connect_db(self):
        """Подключение к базе данных"""
        try:
            self.db_params = {
                'database': self.db_entry.get(),
                'user': self.user_entry.get(),
                'password': self.password_entry.get()
            }
            
            self.conn = psycopg2.connect(**self.db_params)
            self.cur = self.conn.cursor()
            
            # Получаем список столбцов таблицы orders
            self.cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'orders' 
                ORDER BY ordinal_position
            """)
            
            columns = self.cur.fetchall()
            column_names = [col[0] for col in columns]
            
            self.column_combo['values'] = column_names
            if column_names:
                self.partition_column.set(column_names[0])
            
            # Обновляем статус
            self.status_bar.config(text=f"Подключено к {self.db_params['database']}")#@{self.db_params['host']}")
            
            # Активируем кнопки
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.info_btn.config(state="normal")
            self.preview_btn.config(state="normal")
            self.execute_btn.config(state="normal")
            
            messagebox.showinfo("Успех", "Подключение к базе данных установлено!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к базе данных:\n{str(e)}")
            
    def disconnect_db(self):
        """Отключение от базы данных"""
        try:
            if hasattr(self, 'cur'):
                self.cur.close()
            if hasattr(self, 'conn'):
                self.conn.close()
            
            self.status_bar.config(text="Не подключено к базе данных")
            
            # Деактивируем кнопки
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.info_btn.config(state="disabled")
            self.preview_btn.config(state="disabled")
            self.execute_btn.config(state="disabled")
            
            messagebox.showinfo("Отключено", "Соединение с базой данных закрыто")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при отключении:\n{str(e)}")
            
    def get_table_info(self):
        """Получение информации о таблице"""
        try:
            # Получаем информацию о таблице
            self.cur.execute("""
                SELECT 
                    COUNT(*) as total_rows,
                    MIN(session_date) as min_date,
                    MAX(session_date) as max_date,
                    MIN(price) as min_ticket,
                    MAX(price) as max_ticket,
                    COUNT(DISTINCT id) as unique_shows,
                    COUNT(DISTINCT movie) as unique_films
                FROM orders
            """)
            
            stats = self.cur.fetchone()
            
            # Получаем информацию о столбцах
            self.cur.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = 'orders' 
                ORDER BY ordinal_position
            """)
            
            columns = self.cur.fetchall()
            
            # Формируем вывод
            info_text = "="*60 + "\n"
            info_text += "СТАТИСТИКА ТАБЛИЦЫ orders\n"
            info_text += "="*60 + "\n"
            info_text += f"Всего строк: {stats[0]:,}\n"
            info_text += f"Диапазон дат: от {stats[1]} до {stats[2]}\n"
            info_text += f"Диапазон ticket_id: от {stats[3]} до {stats[4]}\n"
            info_text += f"Уникальных шоу: {stats[5]}\n"
            info_text += f"Уникальных фильмов: {stats[6]}\n\n"
            
            info_text += "СТОЛБЦЫ ТАБЛИЦЫ:\n"
            info_text += "-"*60 + "\n"
            info_text += f"{'Имя столбца':<15} {'Тип данных':<20} {'NULL?':<10} {'Макс. длина'}\n"
            info_text += "-"*60 + "\n"
            
            for col in columns:
                info_text += f"{col[0]:<15} {col[1]:<20} {col[2]:<10} {col[3] or 'N/A'}\n"
            
            self.table_info.delete(1.0, tk.END)
            self.table_info.insert(1.0, info_text)
            
            self.status_bar.config(text="Информация о таблице получена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию о таблице:\n{str(e)}")
            
    def preview_sql(self):
        """Предварительный просмотр SQL запросов для партиционирования"""
        try:
            method = self.partition_method.get()
            column = self.partition_column.get()
            
            if not column:
                messagebox.showwarning("Внимание", "Выберите столбец для партиционирования")
                return
            
            # Получаем информацию о типе данных столбца
            self.cur.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'orders' AND column_name = %s
            """, (column,))
            
            col_type = self.cur.fetchone()[0]
            
            sql_queries = []
            
            # Создаем родительскую таблицу
            parent_table = f"orders_partitioned_{column}"
            sql_queries.append(f"-- Создание родительской таблицы\n")
            sql_queries.append(f"CREATE TABLE {parent_table} (\n")
            sql_queries.append(f"    LIKE orders INCLUDING ALL\n")
            sql_queries.append(f") PARTITION BY {method.upper()} ({column});\n")
            
            # Генерируем партиции в зависимости от метода
            if method == "range":
                start = int(self.range_start.get())
                step = int(self.range_step.get())
                count = int(self.range_count.get())
                
                for i in range(count):
                    from_val = start + (i * step)
                    to_val = start + ((i + 1) * step)
                    partition_name = f"{parent_table}_{from_val}_{to_val}"
                    
                    sql_queries.append(f"\n-- Партиция {i+1}\n")
                    sql_queries.append(f"CREATE TABLE {partition_name}\n")
                    sql_queries.append(f"PARTITION OF {parent_table}\n")
                    sql_queries.append(f"FOR VALUES FROM ({from_val}) TO ({to_val});\n")
            
            elif method == "list":
                values_text = self.list_values.get(1.0, tk.END).strip()
                values_list = [v.strip() for v in values_text.split(',') if v.strip()]
                
                for i, value in enumerate(values_list):
                    if "'" in value:
                        formatted_value = value
                    else:
                        formatted_value = f"'{value}'"
                    
                    partition_name = f"{parent_table}_{value.replace(' ', '_').replace('-', '_')}"
                    
                    sql_queries.append(f"\n-- Партиция для значения {value}\n")
                    sql_queries.append(f"CREATE TABLE {partition_name}\n")
                    sql_queries.append(f"PARTITION OF {parent_table}\n")
                    sql_queries.append(f"FOR VALUES IN ({formatted_value});\n")
            
            elif method == "hash":
                count = int(self.hash_count.get())
                
                for i in range(count):
                    partition_name = f"{parent_table}_part_{i}"
                    
                    sql_queries.append(f"\n-- Хэш-партиция {i+1}\n")
                    sql_queries.append(f"CREATE TABLE {partition_name}\n")
                    sql_queries.append(f"PARTITION OF {parent_table}\n")
                    sql_queries.append(f"FOR VALUES WITH (MODULUS {count}, REMAINDER {i});\n")
            
            # Запрос для переноса данных
            sql_queries.append(f"\n-- Перенос данных из исходной таблицы\n")
            sql_queries.append(f"INSERT INTO {parent_table} SELECT * FROM orders;\n")
            
            # Если не нужно сохранять исходную таблицу
            if not self.keep_original.get():
                sql_queries.append(f"\n-- Удаление исходной таблицы\n")
                sql_queries.append(f"DROP TABLE orders CASCADE;\n")
                sql_queries.append(f"\n-- Переименование партиционированной таблицы\n")
                sql_queries.append(f"ALTER TABLE {parent_table} RENAME TO orders;\n")
            
            self.sql_output.delete(1.0, tk.END)
            self.sql_output.insert(1.0, "".join(sql_queries))
            
            self.status_bar.config(text=f"SQL запросы сгенерированы для {method.upper()} партиционирования по столбцу {column}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать SQL:\n{str(e)}")
            
    def execute_partitioning(self):
        """Выполнение партиционирования в отдельном потоке"""
        if not messagebox.askyesno("Подтверждение", 
                                  "Выполнить партиционирование таблицы?\nЭта операция может занять некоторое время."):
            return
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=self._execute_partitioning_thread)
        thread.daemon = True
        thread.start()
        
    def _execute_partitioning_thread(self):
        """Поток для выполнения партиционирования"""
        try:
            self.progress.start()
            self.status_bar.config(text="Выполнение партиционирования...")
            
            # Получаем SQL из текстового поля
            sql_script = self.sql_output.get(1.0, tk.END)
            
            # Выполняем SQL в транзакции
            self.cur.execute("BEGIN;")
            
            # Разделяем скрипт на отдельные запросы
            queries = [q.strip() for q in sql_script.split(';') if q.strip()]
            
            for i, query in enumerate(queries):
                self.status_bar.config(text=f"Выполнение запроса {i+1}/{len(queries)}...")
                self.cur.execute(query)
            
            self.conn.commit()
            
            self.progress.stop()
            self.status_bar.config(text="Партиционирование успешно завершено!")
            
            messagebox.showinfo("Успех", "Партиционирование таблицы успешно выполнено!")
            
            # Обновляем информацию о таблице
            self.get_table_info()
            
        except Exception as e:
            self.conn.rollback()
            self.progress.stop()
            self.status_bar.config(text="Ошибка при партиционировании")
            messagebox.showerror("Ошибка", f"Не удалось выполнить партиционирование:\n{str(e)}")

def main():
    root = tk.Tk()
    app = TablePartitioner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
