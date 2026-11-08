import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2
from psycopg2 import sql
from datetime import datetime
import threading
import re

class TablePartitioner:
    def __init__(self, root):
        self.root = root
        self.root.title("PostgreSQL Table Partitioner")
        self.root.geometry("1100x750")
        
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
        self.password_entry.insert(0, "8bzm61K")
        
        # Название таблицы
        ttk.Label(conn_frame, text="Таблица:").grid(row=2, column=2, padx=5, pady=5)
        self.table_entry = ttk.Entry(conn_frame, width=20)
        self.table_entry.grid(row=2, column=3, padx=5, pady=5)
        self.table_entry.insert(0, "orders")
        
        # Кнопки подключения/отключения
        self.connect_btn = ttk.Button(conn_frame, text="Подключиться", command=self.connect_db)
        self.connect_btn.grid(row=3, column=2, padx=5, pady=5)
        
        self.disconnect_btn = ttk.Button(conn_frame, text="Отключиться", command=self.disconnect_db, state="disabled")
        self.disconnect_btn.grid(row=3, column=3, padx=5, pady=5)
        
        # Фрейм для выбора метода партиционирования
        method_frame = ttk.LabelFrame(self.root, text="Метод партиционирования", padding=10)
        method_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Переменные для выбора
        self.partition_method = tk.StringVar(value="range")
        self.partition_column = tk.StringVar()
        
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
        
        ttk.Label(self.range_frame, text="Тип диапазона:").grid(row=0, column=0, padx=5, pady=5)
        self.range_type = ttk.Combobox(self.range_frame, values=["Числовой", "Дата", "Дата и время"], 
                                      state="readonly", width=15)
        self.range_type.grid(row=0, column=1, padx=5, pady=5)
        self.range_type.set("Числовой")
        self.range_type.bind("<<ComboboxSelected>>", self.on_range_type_change)
        
        # Числовой диапазон
        self.num_range_frame = ttk.Frame(self.range_frame)
        self.num_range_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.num_range_frame, text="От:").grid(row=0, column=0, padx=5, pady=5)
        self.range_num_from = ttk.Entry(self.num_range_frame, width=15)
        self.range_num_from.grid(row=0, column=1, padx=5, pady=5)
        self.range_num_from.insert(0, "1")
        
        ttk.Label(self.num_range_frame, text="До:").grid(row=0, column=2, padx=5, pady=5)
        self.range_num_to = ttk.Entry(self.num_range_frame, width=15)
        self.range_num_to.grid(row=0, column=3, padx=5, pady=5)
        self.range_num_to.insert(0, "10000")
        
        ttk.Label(self.num_range_frame, text="Интервал:").grid(row=1, column=0, padx=5, pady=5)
        self.range_num_interval = ttk.Entry(self.num_range_frame, width=15)
        self.range_num_interval.grid(row=1, column=1, padx=5, pady=5)
        self.range_num_interval.insert(0, "1000")
        
        # Диапазон дат
        self.date_range_frame = ttk.Frame(self.range_frame)
        self.date_range_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.date_range_frame, text="От:").grid(row=0, column=0, padx=5, pady=5)
        self.range_date_from = ttk.Entry(self.date_range_frame, width=15)
        self.range_date_from.grid(row=0, column=1, padx=5, pady=5)
        self.range_date_from.insert(0, "2024-01-01")
        
        ttk.Label(self.date_range_frame, text="До:").grid(row=0, column=2, padx=5, pady=5)
        self.range_date_to = ttk.Entry(self.date_range_frame, width=15)
        self.range_date_to.grid(row=0, column=3, padx=5, pady=5)
        self.range_date_to.insert(0, "2024-12-31")
        
        ttk.Label(self.date_range_frame, text="Интервал (дней):").grid(row=1, column=0, padx=5, pady=5)
        self.range_date_interval = ttk.Entry(self.date_range_frame, width=15)
        self.range_date_interval.grid(row=1, column=1, padx=5, pady=5)
        self.range_date_interval.insert(0, "30")
        
        # Параметры для LIST партиционирования
        self.list_frame = ttk.LabelFrame(method_frame, text="Параметры LIST партиционирования", padding=5)
        self.list_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=10)
        
        self.list_type = tk.StringVar(value="manual")
        
        ttk.Radiobutton(self.list_frame, text="Ручной ввод значений", 
                       variable=self.list_type, value="manual").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(self.list_frame, text="Автоматически из данных", 
                       variable=self.list_type, value="auto").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        self.list_manual_frame = ttk.Frame(self.list_frame)
        self.list_manual_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.list_manual_frame, text="Значения (через запятую):").grid(row=0, column=0, padx=5, pady=5)
        self.list_values = scrolledtext.ScrolledText(self.list_manual_frame, width=40, height=3)
        self.list_values.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        self.list_auto_frame = ttk.Frame(self.list_frame)
        self.list_auto_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.list_auto_frame, text="Лимит уникальных значений:").grid(row=0, column=0, padx=5, pady=5)
        self.list_auto_limit = ttk.Entry(self.list_auto_frame, width=10)
        self.list_auto_limit.grid(row=0, column=1, padx=5, pady=5)
        self.list_auto_limit.insert(0, "20")
        
        # Параметры для HASH партиционирования
        self.hash_frame = ttk.LabelFrame(method_frame, text="Параметры HASH партиционирования", padding=5)
        self.hash_frame.grid(row=7, column=0, sticky="ew", padx=5, pady=10)
        
        ttk.Label(self.hash_frame, text="Количество партиций:").grid(row=0, column=0, padx=5, pady=5)
        self.hash_count = ttk.Entry(self.hash_frame, width=15)
        self.hash_count.grid(row=0, column=1, padx=5, pady=5)
        self.hash_count.insert(0, "4")
        
        # Скрываем все фреймы параметров изначально
        self.hide_all_param_frames()
        
        # Фрейм для рекомендаций по партиционированию
        self.recommend_frame = ttk.LabelFrame(method_frame, text="Рекомендации", padding=5)
        self.recommend_frame.grid(row=8, column=0, sticky="ew", padx=5, pady=10)
        
        self.recommend_text = tk.Text(self.recommend_frame, height=4, width=40)
        self.recommend_text.grid(row=0, column=0, padx=5, pady=5)
        self.recommend_scroll = ttk.Scrollbar(self.recommend_frame, command=self.recommend_text.yview)
        self.recommend_scroll.grid(row=0, column=1, sticky="ns")
        self.recommend_text.config(yscrollcommand=self.recommend_scroll.set)
        
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
        
        # Композитное партиционирование
        self.composite_var = tk.BooleanVar(value=False)
        self.composite_check = ttk.Checkbutton(options_frame, text="Композитное партиционирование", 
                                              variable=self.composite_var, command=self.toggle_composite)
        self.composite_check.grid(row=3, column=0, sticky="w", pady=5)
        
        # Второй столбец для композитного партиционирования
        self.composite_frame = ttk.Frame(options_frame)
        
        ttk.Label(self.composite_frame, text="Второй столбец:").grid(row=0, column=0, padx=5, pady=5)
        self.composite_column = ttk.Combobox(self.composite_frame, state="readonly", width=15)
        self.composite_column.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.composite_frame, text="Метод:").grid(row=1, column=0, padx=5, pady=5)
        self.composite_method = ttk.Combobox(self.composite_frame, values=["range", "list", "hash"], 
                                           state="readonly", width=15)
        self.composite_method.grid(row=1, column=1, padx=5, pady=5)
        self.composite_method.set("range")
        
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
        
        # Кнопка для тестирования запросов
        self.test_btn = ttk.Button(control_frame, text="Тест производительности", 
                                  command=self.test_performance, state="disabled")
        self.test_btn.pack(fill="x", pady=5)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(control_frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=10)
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Не подключено к базе данных", relief="sunken")
        self.status_bar.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        # Привязка события изменения метода партиционирования
        self.partition_method.trace("w", self.on_method_change)
        self.partition_column.trace("w", self.on_column_change)
        
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
        self.date_range_frame.grid_remove()
        
    def on_range_type_change(self, event=None):
        """Обработчик изменения типа диапазона"""
        range_type = self.range_type.get()
        if range_type == "Числовой":
            self.num_range_frame.grid()
            self.date_range_frame.grid_remove()
        else:
            self.num_range_frame.grid_remove()
            self.date_range_frame.grid()
            
    def on_method_change(self, *args):
        """Обработчик изменения метода партиционирования"""
        method = self.partition_method.get()
        self.hide_all_param_frames()
        
        if method == "range":
            self.range_frame.grid()
            self.on_range_type_change()
        elif method == "list":
            self.list_frame.grid()
        elif method == "hash":
            self.hash_frame.grid()
        
        self.recommend_frame.grid()
        self.update_recommendations()
            
    def on_column_change(self, *args):
        """Обработчик изменения столбца"""
        self.update_recommendations()
        
    def toggle_composite(self):
        """Включение/выключение композитного партиционирования"""
        if self.composite_var.get():
            self.composite_frame.grid(row=4, column=0, sticky="w", padx=5, pady=10)
            # Обновляем доступные столбцы для второго уровня
            current_col = self.partition_column.get()
            all_cols = list(self.column_combo['values'])
            other_cols = [col for col in all_cols if col != current_col]
            self.composite_column['values'] = other_cols
            if other_cols:
                self.composite_column.set(other_cols[0])
        else:
            self.composite_frame.grid_remove()
            
    def update_recommendations(self):
        """Обновление рекомендаций по партиционированию"""
        column = self.partition_column.get()
        if not column:
            return
            
        method = self.partition_method.get()
        recommendations = ""
        
        # Рекомендации в зависимости от столбца
        if column == "id":
            recommendations += "ID - уникальный идентификатор\n"
            recommendations += "✓ RANGE: оптимально для последовательных ID\n"
            recommendations += "✓ HASH: для равномерного распределения\n"
            recommendations += "✗ LIST: не рекомендуется (слишком много значений)\n"
            
        elif column in ["order_date", "session_date"]:
            recommendations += f"{column} - временная метка\n"
            recommendations += "✓ RANGE: оптимально для временных рядов\n"
            recommendations += "✓ LIST: по дням недели, месяцам и т.д.\n"
            recommendations += "✓ HASH: если нужен равномерный доступ\n"
            
        elif column == "customer":
            recommendations += "customer - клиент\n"
            recommendations += "✓ LIST: по группам клиентов\n"
            recommendations += "✓ HASH: для равномерного распределения\n"
            recommendations += "✗ RANGE: не рекомендуется для текста\n"
            
        elif column == "movie":
            recommendations += "movie - название фильма\n"
            recommendations += "✓ LIST: по жанрам/категориям\n"
            recommendations += "✓ HASH: для равномерного распределения\n"
            recommendations += "✗ RANGE: не рекомендуется для текста\n"
            
        elif column == "quantity":
            recommendations += "quantity - количество билетов\n"
            recommendations += "✓ RANGE: по диапазонам количества\n"
            recommendations += "✓ LIST: по фиксированным значениям\n"
            recommendations += "✓ HASH: для равномерного распределения\n"
            
        elif column == "price":
            recommendations += "price - цена\n"
            recommendations += "✓ RANGE: по ценовым диапазонам\n"
            recommendations += "✓ LIST: по категориям цен\n"
            recommendations += "✓ HASH: для равномерного распределения\n"
        
        self.recommend_text.delete(1.0, tk.END)
        self.recommend_text.insert(1.0, recommendations)
            
    def connect_db(self):
        """Подключение к базе данных"""
        try:
            self.db_params = {
                'database': self.db_entry.get(),
                'user': self.user_entry.get(),
                'password': self.password_entry.get()
            }
            
            table_name = self.table_entry.get()
            
            self.conn = psycopg2.connect(**self.db_params)
            self.cur = self.conn.cursor()
            
            # Проверяем существование таблицы
            self.cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            
            if not self.cur.fetchone()[0]:
                messagebox.showwarning("Внимание", f"Таблица '{table_name}' не найдена в базе данных")
                self.disconnect_db()
                return
            
            # Получаем список столбцов таблицы
            self.cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = self.cur.fetchall()
            column_names = [col[0] for col in columns]
            
            self.column_combo['values'] = column_names
            if column_names:
                self.partition_column.set(column_names[0])
            
            # Обновляем статус
            self.status_bar.config(text=f"Подключено к {self.db_params['database']}")#@{self.db_params['host']}, таблица: {table_name}")
            
            # Активируем кнопки
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.info_btn.config(state="normal")
            self.preview_btn.config(state="normal")
            self.execute_btn.config(state="normal")
            self.test_btn.config(state="normal")
            
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
            self.test_btn.config(state="disabled")
            
            messagebox.showinfo("Отключено", "Соединение с базой данных закрыто")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при отключении:\n{str(e)}")
            
    def get_table_info(self):
        """Получение информации о таблице"""
        try:
            table_name = self.table_entry.get()
            
            # Получаем информацию о таблице
            self.cur.execute(sql.SQL("""
                SELECT 
                    COUNT(*) as total_rows,
                    MIN(order_date) as min_order_date,
                    MAX(order_date) as max_order_date,
                    MIN(session_date) as min_session_date,
                    MAX(session_date) as max_session_date,
                    MIN(id) as min_id,
                    MAX(id) as max_id,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    AVG(price) as avg_price,
                    COUNT(DISTINCT customer) as unique_customers,
                    COUNT(DISTINCT movie) as unique_movies,
                    COUNT(DISTINCT quantity) as unique_quantities
                FROM {}
            """).format(sql.Identifier(table_name)))
            
            stats = self.cur.fetchone()
            
            # Получаем информацию о столбцах
            self.cur.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = self.cur.fetchall()
            
            # Формируем вывод
            info_text = "="*70 + "\n"
            info_text += f"СТАТИСТИКА ТАБЛИЦЫ {table_name}\n"
            info_text += "="*70 + "\n"
            info_text += f"Всего строк: {stats[0]:,}\n"
            info_text += f"Диапазон order_date: от {stats[1]} до {stats[2]}\n"
            info_text += f"Диапазон session_date: от {stats[3]} до {stats[4]}\n"
            info_text += f"Диапазон id: от {stats[5]} до {stats[6]}\n"
            info_text += f"Диапазон price: от {stats[7]:.2f} до {stats[8]:.2f} (среднее: {stats[9]:.2f})\n"
            info_text += f"Уникальных клиентов: {stats[10]}\n"
            info_text += f"Уникальных фильмов: {stats[11]}\n"
            info_text += f"Уникальных количеств: {stats[12]}\n\n"
            
            info_text += "СТОЛБЦЫ ТАБЛИЦЫ:\n"
            info_text += "-"*70 + "\n"
            info_text += f"{'Имя столбца':<15} {'Тип данных':<20} {'NULL?':<10} {'Макс. длина':<15} {'Рекомендация'}\n"
            info_text += "-"*70 + "\n"
            
            for col in columns:
                col_name = col[0]
                recommendation = self.get_column_recommendation(col_name, col[1])
                info_text += f"{col_name:<15} {col[1]:<20} {col[2]:<10} {str(col[3] or 'N/A'):<15} {recommendation}\n"
            
            self.table_info.delete(1.0, tk.END)
            self.table_info.insert(1.0, info_text)
            
            self.status_bar.config(text="Информация о таблице получена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию о таблице:\n{str(e)}")
            
    def get_column_recommendation(self, column_name, data_type):
        """Получение рекомендаций для столбца"""
        if column_name == "id":
            return "RANGE/HASH (лучше RANGE)"
        elif column_name in ["order_date", "session_date"]:
            return "RANGE (временные ряды)"
        elif column_name == "customer":
            return "LIST/HASH (по группам)"
        elif column_name == "movie":
            return "LIST (по категориям)"
        elif column_name == "quantity":
            return "RANGE/LIST"
        elif column_name == "price":
            return "RANGE (ценовые группы)"
        else:
            return "HASH (универсально)"
            
    def preview_sql(self):
        """Предварительный просмотр SQL запросов для партиционирования"""
        try:
            method = self.partition_method.get()
            column = self.partition_column.get()
            table_name = self.table_entry.get()
            
            if not column:
                messagebox.showwarning("Внимание", "Выберите столбец для партиционирования")
                return
            
            # Получаем информацию о типе данных столбца
            self.cur.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, (table_name, column))
            
            col_type = self.cur.fetchone()[0]
            
            sql_queries = []
            
            # Создаем родительскую таблицу
            parent_table = f"{table_name}_partitioned_{column}"
            
            # Определяем метод партиционирования для SQL
            partition_sql = self.generate_partition_sql(method, column, col_type, table_name)
            
            if not partition_sql:
                return
            
            sql_queries.append(f"-- Создание партиционированной таблицы\n")
            sql_queries.append(f"CREATE TABLE {parent_table} (\n")
            sql_queries.append(f"    LIKE {table_name} INCLUDING ALL\n")
            
            if self.composite_var.get():
                second_col = self.composite_column.get()
                second_method = self.composite_method.get()
                second_sql = self.generate_subpartition_sql(second_method, second_col, table_name)
                sql_queries.append(f") PARTITION BY {partition_sql}\n")
                sql_queries.append(f"SUBPARTITION BY {second_sql};\n")
            else:
                sql_queries.append(f") PARTITION BY {partition_sql};\n")
            
            # Генерируем партиции
            partitions_sql = self.generate_partitions(method, column, col_type, parent_table, table_name)
            sql_queries.extend(partitions_sql)
            
            # Запрос для переноса данных
            sql_queries.append(f"\n-- Перенос данных из исходной таблицы\n")
            sql_queries.append(f"INSERT INTO {parent_table} SELECT * FROM {table_name};\n")
            
            # Если не нужно сохранять исходную таблицу
            if not self.keep_original.get():
                sql_queries.append(f"\n-- Удаление исходной таблицы\n")
                sql_queries.append(f"DROP TABLE {table_name} CASCADE;\n")
                sql_queries.append(f"\n-- Переименование партиционированной таблицы\n")
                sql_queries.append(f"ALTER TABLE {parent_table} RENAME TO {table_name};\n")
            
            self.sql_output.delete(1.0, tk.END)
            self.sql_output.insert(1.0, "".join(sql_queries))
            
            method_name = method.upper()
            if self.composite_var.get():
                method_name += f" + {self.composite_method.get().upper()}"
            
            self.status_bar.config(text=f"SQL запросы сгенерированы для {method_name} партиционирования по столбцу {column}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать SQL:\n{str(e)}")
            
    def generate_partition_sql(self, method, column, col_type, table_name):
        """Генерация SQL для метода партиционирования"""
        if method == "range":
            return f"RANGE ({column})"
        elif method == "list":
            return f"LIST ({column})"
        elif method == "hash":
            count = self.hash_count.get()
            if not count.isdigit() or int(count) <= 0:
                messagebox.showwarning("Внимание", "Введите корректное количество партиций для HASH")
                return None
            return f"HASH ({column})"
        return None
        
    def generate_subpartition_sql(self, method, column, table_name):
        """Генерация SQL для субпартиционирования"""
        if method == "range":
            return f"RANGE ({column})"
        elif method == "list":
            return f"LIST ({column})"
        elif method == "hash":
            return f"HASH ({column})"
        return ""
        
    def generate_partitions(self, method, column, col_type, parent_table, table_name):
        """Генерация SQL для создания партиций"""
        sql_parts = []
        
        if method == "range":
            range_type = self.range_type.get()
            
            if range_type == "Числовой":
                try:
                    start = int(self.range_num_from.get())
                    end = int(self.range_num_to.get())
                    interval = int(self.range_num_interval.get())
                    
                    current = start
                    partition_num = 1
                    
                    while current < end:
                        next_val = min(current + interval, end)
                        partition_name = f"{parent_table}_range_{current}_{next_val}"
                        
                        sql_parts.append(f"\n-- Партиция {partition_num} (значения от {current} до {next_val})\n")
                        sql_parts.append(f"CREATE TABLE {partition_name}\n")
                        sql_parts.append(f"PARTITION OF {parent_table}\n")
                        sql_parts.append(f"FOR VALUES FROM ({current}) TO ({next_val});\n")
                        
                        current = next_val
                        partition_num += 1
                        
                except ValueError:
                    messagebox.showwarning("Внимание", "Введите корректные числовые значения для диапазона")
                    return []
                    
            else:  # Дата или дата и время
                try:
                    start_date = self.range_date_from.get()
                    end_date = self.range_date_to.get()
                    interval_days = int(self.range_date_interval.get())
                    
                    # Создаем партиции по месяцам/интервалам
                    sql_parts.append(f"\n-- Партиции по датам (от {start_date} до {end_date}, интервал {interval_days} дней)\n")
                    
                    # В реальном приложении здесь была бы сложная логика создания дат
                    # Для примера создаем 4 партиции
                    for i in range(4):
                        partition_name = f"{parent_table}_date_part_{i+1}"
                        sql_parts.append(f"\nCREATE TABLE {partition_name}\n")
                        sql_parts.append(f"PARTITION OF {parent_table}\n")
                        sql_parts.append(f"FOR VALUES FROM ('2024-{i*3+1:02d}-01') TO ('2024-{(i+1)*3+1:02d}-01');\n")
                        
                except ValueError:
                    messagebox.showwarning("Внимание", "Введите корректные даты и интервал")
                    return []
                    
        elif method == "list":
            list_type = self.list_type.get()
            
            if list_type == "manual":
                values_text = self.list_values.get(1.0, tk.END).strip()
                values_list = [v.strip() for v in values_text.split(',') if v.strip()]
                
                if not values_list:
                    messagebox.showwarning("Внимание", "Введите значения для LIST партиционирования")
                    return []
                    
                for i, value in enumerate(values_list):
                    # Определяем, нужно ли заключать в кавычки
                    if col_type in ['character varying', 'text', 'varchar'] or not value.isdigit():
                        if "'" not in value and '"' not in value:
                            formatted_value = f"'{value}'"
                        else:
                            formatted_value = value
                    else:
                        formatted_value = value
                    
                    safe_value = re.sub(r'[^a-zA-Z0-9_]', '_', str(value))
                    partition_name = f"{parent_table}_list_{safe_value}"
                    
                    sql_parts.append(f"\n-- Партиция для значения {value}\n")
                    sql_parts.append(f"CREATE TABLE {partition_name}\n")
                    sql_parts.append(f"PARTITION OF {parent_table}\n")
                    sql_parts.append(f"FOR VALUES IN ({formatted_value});\n")
                    
            else:  # auto
                limit = int(self.list_auto_limit.get())
                
                # Получаем уникальные значения из таблицы
                self.cur.execute(sql.SQL("""
                    SELECT DISTINCT {} 
                    FROM {} 
                    LIMIT %s
                """).format(sql.Identifier(column), sql.Identifier(table_name)), (limit,))
                
                values = [row[0] for row in self.cur.fetchall()]
                
                if not values:
                    messagebox.showwarning("Внимание", "Не найдено уникальных значений в столбце")
                    return []
                
                sql_parts.append(f"\n-- Автоматические партиции по уникальным значениям (первые {limit})\n")
                
                for i, value in enumerate(values):
                    if value is None:
                        continue
                        
                    if col_type in ['character varying', 'text', 'varchar']:
                        formatted_value = f"'{value}'"
                    else:
                        formatted_value = str(value)
                    
                    safe_value = re.sub(r'[^a-zA-Z0-9_]', '_', str(value))[:20]
                    partition_name = f"{parent_table}_auto_{safe_value}"
                    
                    sql_parts.append(f"\n-- Партиция для значения: {value}\n")
                    sql_parts.append(f"CREATE TABLE {partition_name}\n")
                    sql_parts.append(f"PARTITION OF {parent_table}\n")
                    sql_parts.append(f"FOR VALUES IN ({formatted_value});\n")
                    
        elif method == "hash":
            count = int(self.hash_count.get())
            
            sql_parts.append(f"\n-- HASH партиции (всего {count})\n")
            
            for i in range(count):
                partition_name = f"{parent_table}_hash_{i}"
                
                sql_parts.append(f"\n-- HASH партиция {i+1}\n")
                sql_parts.append(f"CREATE TABLE {partition_name}\n")
                sql_parts.append(f"PARTITION OF {parent_table}\n")
                sql_parts.append(f"FOR VALUES WITH (MODULUS {count}, REMAINDER {i});\n")
        
        return sql_parts
        
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
            queries = []
            current_query = ""
            in_string = False
            string_char = None
            
            for char in sql_script:
                current_query += char
                if char in ("'", '"') and (not in_string or string_char == char):
                    in_string = not in_string
                    string_char = char if in_string else None
                elif char == ';' and not in_string:
                    queries.append(current_query.strip())
                    current_query = ""
            
            if current_query.strip():
                queries.append(current_query.strip())
            
            for i, query in enumerate(queries):
                if not query.strip():
                    continue
                    
                self.status_bar.config(text=f"Выполнение запроса {i+1}/{len(queries)}...")
                try:
                    self.cur.execute(query)
                except Exception as e:
                    raise Exception(f"Ошибка в запросе {i+1}:\n{query}\n\nОшибка: {str(e)}")
            
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
            
    def test_performance(self):
        """Тестирование производительности запросов"""
        try:
            table_name = self.table_entry.get()
            column = self.partition_column.get()
            
            test_queries = [
                f"SELECT COUNT(*) FROM {table_name} WHERE {column} = (SELECT MIN({column}) FROM {table_name})",
                f"SELECT AVG(price) FROM {table_name} GROUP BY {column}",
                f"EXPLAIN ANALYZE SELECT * FROM {table_name} WHERE {column} IS NOT NULL LIMIT 1000"
            ]
            
            results = []
            
            for i, query in enumerate(test_queries):
                self.cur.execute("EXPLAIN ANALYZE " + query)
                explain_result = self.cur.fetchall()
                execution_time = None
                
                for line in explain_result:
                    line_text = line[0]
                    if "Execution Time:" in line_text:
                        execution_time = float(line_text.split(":")[1].split()[0])
                        break
                
                results.append(f"Запрос {i+1}: {execution_time:.2f} мс")
            
            messagebox.showinfo("Результаты теста", 
                              "Время выполнения тестовых запросов:\n\n" + 
                              "\n".join(results) + 
                              "\n\nМеньше = лучше")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить тест производительности:\n{str(e)}")

def main():
    root = tk.Tk()
    app = TablePartitioner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
