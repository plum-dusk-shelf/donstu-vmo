db_config = {'database' : "myfirstdb",
                               'user' : "simafrus",
                               'password' : "8bzm61K",
                               'port' : 5432
        }

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import psycopg2
from psycopg2 import sql
import os

class PostgresGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("управление пользователями postgresql с транзакциями")
        self.root.geometry("800x900")
        
        self.db_config = db_config
        self.transaction_active = False
        self.savepoints = []
        self.current_image_data = None
        self.current_doc_data = None
        
        self.create_widgets()
        self.connect_to_db()
        self.load_data()

        self.last_savepoint = 0

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        transaction_frame = ttk.LabelFrame(main_frame, text="управление транзакциями")
        transaction_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(transaction_frame, text="начать транзакцию", 
                  command=self.start_transaction).pack(side="left", padx=5, pady=5)
        ttk.Button(transaction_frame, text="закончить транзакцию", 
                  command=self.end_transaction).pack(side="left", padx=5, pady=5)
        ttk.Button(transaction_frame, text="откатить транзакцию", 
                  command=self.rollback_transaction).pack(side="left", padx=5, pady=5)
        
        savepoint_frame = ttk.LabelFrame(main_frame, text="операции с точками сохранения")
        savepoint_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(savepoint_frame, text="создать точку сохранения", 
                  command=self.create_savepoint).pack(side="left", padx=5, pady=5)
        ttk.Button(savepoint_frame, text="откат к точке сохранения", 
                  command=self.rollback_to_savepoint).pack(side="left", padx=5, pady=5)
        ttk.Button(savepoint_frame, text="освободить точку сохранения", 
                  command=self.release_savepoint).pack(side="left", padx=5, pady=5)
        ttk.Button(savepoint_frame, text="список точек сохранения", 
                  command=self.list_savepoints).pack(side="left", padx=5, pady=5)
        
        search_frame = ttk.LabelFrame(main_frame, text="поиск пользователей")
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="поиск:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(search_frame, text="найти", command=self.search_data).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="очистить поиск", command=self.clear_search).grid(row=0, column=3, padx=5, pady=5)
        
        input_frame = ttk.LabelFrame(main_frame, text="информация о пользователе")
        input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(input_frame, text="id:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_entry = ttk.Entry(input_frame, width=10, state='readonly')
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="имя:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.first_name_entry = ttk.Entry(input_frame, width=20)
        self.first_name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="фамилия:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.last_name_entry = ttk.Entry(input_frame, width=20)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="пол:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.gender_combobox = ttk.Combobox(input_frame, values=["мужской", "женский", "другой"], width=18)
        self.gender_combobox.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="email:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.email_entry = ttk.Entry(input_frame, width=20)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Фрейм для работы с изображением
        image_frame = ttk.Frame(input_frame)
        image_frame.grid(row=3, column=0, columnspan=4, sticky="we", padx=5, pady=5)


        doc_frame = ttk.Frame(input_frame)
        doc_frame.grid(row=3, column=0, columnspan=4, sticky="we", padx=5, pady=5)
        
        ttk.Label(image_frame, text="изображение:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(image_frame, text="выбрать файл", 
                  command=self.select_image_file).grid(row=0, column=1, padx=5, pady=5)
        self.image_filename_label = ttk.Label(image_frame, text="файл не выбран")
        self.image_filename_label.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(image_frame, text="очистить", 
                  command=self.clear_image).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(doc_frame, text="doc:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Button(doc_frame, text="выбрать файл", 
                  command=self.select_doc_file).grid(row=0, column=1, padx=5, pady=5)
        self.doc_filename_label = ttk.Label(doc_frame, text="файл не выбран")
        self.doc_filename_label.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(doc_frame, text="очистить", 
                  command=self.clear_doc).grid(row=0, column=3, padx=5, pady=5)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="добавить пользователя", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(button_frame, text="обновить пользователя", command=self.update_record).pack(side="left", padx=5)
        ttk.Button(button_frame, text="удалить пользователя", command=self.delete_record).pack(side="left", padx=5)
        ttk.Button(button_frame, text="очистить поля", command=self.clear_entries).pack(side="left", padx=5)
        ttk.Button(button_frame, text="обновить данные", command=self.load_data).pack(side="left", padx=5)
        
        # Фрейм для восстановления изображения
        restore_frame = ttk.LabelFrame(main_frame, text="восстановление изображения")
        restore_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(restore_frame, text="id пользователя:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.restore_id_entry = ttk.Entry(restore_frame, width=10)
        self.restore_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(restore_frame, text="восстановить по id", 
                  command=self.restore_image_by_id).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(restore_frame, text="показать по id", 
                  command=self.show_image_by_id).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(restore_frame, text="восстановить выбранного", 
                  command=self.restore_selected_image).grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        ttk.Button(restore_frame, text="показать выбранного", 
                  command=self.show_selected_image).grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        ttk.Button(restore_frame, text="восстановить doc выбранного", 
                  command=self.restore_selected_doc).grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        table_frame = ttk.LabelFrame(main_frame, text="таблица пользователей")
        table_frame.pack(fill="both", expand=True)
        
        columns = ('id', 'имя', 'фамилия', 'пол', 'email', 'изображение', 'файл')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        self.tree.heading('id', text='id')
        self.tree.heading('имя', text='имя')
        self.tree.heading('фамилия', text='фамилия')
        self.tree.heading('пол', text='пол')
        self.tree.heading('email', text='email')
        self.tree.heading('изображение', text='изображение')
        self.tree.heading('файл', text='файл')
        
        self.tree.column('id', width=50)
        self.tree.column('имя', width=120)
        self.tree.column('фамилия', width=120)
        self.tree.column('пол', width=80)
        self.tree.column('email', width=200)
        self.tree.column('изображение', width=100)
        self.tree.column('файл', width=100)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        self.search_entry.bind('<Return>', lambda event: self.search_data())

    def connect_to_db(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
            self.cursor = self.conn.cursor()
            self.create_table_if_not_exists()
        except Exception as e:
            messagebox.showerror("ошибка базы данных", f"ошибка подключения: {str(e)}")

    def create_table_if_not_exists(self):
        create_table_query = """
        create table if not exists users (
            id serial primary key,
            first_name varchar(50) not null,
            last_name varchar(50) not null,
            gender varchar(10),
            email varchar(100) unique,
            image bytea,
            doc bytea
        );
        """
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("ошибка базы данных", f"ошибка создания таблицы: {str(e)}")


    def select_doc_file(self):
        filename = filedialog.askopenfilename(
            title="выберите файл изображения",
            filetypes=[("Все файлы", "*.*"), ("Изображения", "*.jpg;*.png;*.gif;*.bmp")]
        )
        if filename:
            try:
                with open(filename, 'rb') as file:
                    self.current_doc_data = file.read()
                self.doc_filename_label.config(text=os.path.basename(filename))
            except Exception as e:
                messagebox.showerror("ошибка", f"не удалось загрузить файл: {str(e)}")

    def clear_doc(self):
        self.current_doc_data = None
        self.doc_filename_label.config(text="файл не выбран")

    def restore_doc_by_id(self):
        user_id = self.restore_id_entry.get().strip()
        if not user_id:
            messagebox.showwarning("ошибка", "введите id пользователя")
            return
        
        self.restore_doc(user_id)


    def select_image_file(self):
        filename = filedialog.askopenfilename(
            title="выберите файл изображения",
            filetypes=[("Все файлы", "*.*"), ("Изображения", "*.jpg;*.png;*.gif;*.bmp")]
        )
        if filename:
            try:
                with open(filename, 'rb') as file:
                    self.current_image_data = file.read()
                self.image_filename_label.config(text=os.path.basename(filename))
            except Exception as e:
                messagebox.showerror("ошибка", f"не удалось загрузить файл: {str(e)}")

    def clear_image(self):
        self.current_image_data = None
        self.image_filename_label.config(text="файл не выбран")

    def restore_image_by_id(self):
        user_id = self.restore_id_entry.get().strip()
        if not user_id:
            messagebox.showwarning("ошибка", "введите id пользователя")
            return
        
        self.restore_image(user_id)

    def show_image_by_id(self):
        user_id = self.restore_id_entry.get().strip()
        if not user_id:
            messagebox.showwarning("ошибка", "введите id пользователя")
            return
        
        self.show_image(user_id)

    def restore_selected_image(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("ошибка", "выберите пользователя в таблице")
            return
        
        user_id = self.tree.item(selected[0])['values'][0]
        self.restore_image(user_id)

    def restore_selected_doc(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("ошибка", "выберите пользователя в таблице")
            return
        
        user_id = self.tree.item(selected[0])['values'][0]
        self.restore_doc(user_id)

    def show_selected_image(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("ошибка", "выберите пользователя в таблице")
            return
        
        user_id = self.tree.item(selected[0])['values'][0]
        self.show_image(user_id)

    def restore_image(self, user_id):
        try:
            self.cursor.execute("SELECT image FROM users WHERE id = %s", (user_id,))
            result = self.cursor.fetchone()
            
            if not result or not result[0]:
                messagebox.showinfo("результат", "у пользователя нет изображения")
                return
            
            image_data = result[0]
            filename = filedialog.asksaveasfilename(
                title="сохранить изображение как",
                defaultextension=".jpg",
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("Все файлы", "*.*")]
            )
            
            if filename:
                with open(filename, 'wb') as file:
                    file.write(image_data)
                messagebox.showinfo("успех", f"изображение сохранено в файл: {filename}")
                
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка восстановления изображения: {str(e)}")

    def show_image(self, user_id):
        try:
            self.cursor.execute("SELECT image FROM users WHERE id = %s", (user_id,))
            result = self.cursor.fetchone()
            
            if not result or not result[0]:
                messagebox.showinfo("результат", "у пользователя нет изображения")
                return
            
            image_data = result[0]
            
            # Создаем временный файл для отображения
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                temp_filename = temp_file.name
            
            # Открываем изображение с помощью стандартного приложения
            import subprocess
            import platform
            import os
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', temp_filename))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(temp_filename)
            else:  # linux variants
                subprocess.call(('xdg-open', temp_filename))
                
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка отображения изображения: {str(e)}")

    def start_transaction(self):
        if self.transaction_active:
            messagebox.showwarning("транзакция", "транзакция уже активна")
            return
        
        try:
            self.transaction_active = True
            self.savepoints = []
            messagebox.showinfo("транзакция", "транзакция начата")
        except Exception as e:
            messagebox.showerror("ошибка транзакции", f"ошибка начала транзакции: {str(e)}")
            self.transaction_active = False

    def end_transaction(self):
        if not self.transaction_active:
            messagebox.showwarning("транзакция", "нет активной транзакции")
            return
        
        try:
            self.conn.commit()
            self.transaction_active = False
            self.savepoints = []
            messagebox.showinfo("транзакция", "транзакция успешно завершена")
            self.load_data()
        except Exception as e:
            messagebox.showerror("ошибка транзакции", f"ошибка завершения транзакции: {str(e)}")
            self.conn.rollback()
            self.transaction_active = False

    def rollback_transaction(self):
        if not self.transaction_active:
            messagebox.showwarning("транзакция", "нет активной транзакции")
            return
        
        try:
            self.conn.rollback()
            self.transaction_active = False
            self.savepoints = []
            messagebox.showinfo("транзакция", "транзакция откачена")
            self.load_data()
        except Exception as e:
            messagebox.showerror("ошибка транзакции", f"ошибка отката транзакции: {str(e)}")
            self.transaction_active = False

    def create_savepoint(self):
        if not self.transaction_active:
        
            messagebox.showwarning("точка сохранения", "нет активной транзакции")
            return
            
        self.last_savepoint += 1
        savepoint_name = 'save_' + str(self.last_savepoint)
        '''
        savepoint_name = simpledialog.askstring("создать точку сохранения", "введите имя точки сохранения:")
        if not savepoint_name:
            return
            '''
            
        try:
            self.cursor.execute(f"savepoint {savepoint_name}")
            self.savepoints.append(savepoint_name)
            messagebox.showinfo("точка сохранения создана", 
                              f"точка сохранения '{savepoint_name}' создана успешно.\n"
                              f"активные точки сохранения: {', '.join(self.savepoints)}")
        except Exception as e:
            messagebox.showerror("ошибка точки сохранения", f"ошибка создания точки сохранения: {str(e)}")

    def rollback_to_savepoint(self):
        if not self.transaction_active:
            messagebox.showwarning("откат к точке сохранения", "нет активной транзакции")
            return
            
        if not self.savepoints:
            messagebox.showwarning("откат к точке сохранения", "нет активных точек сохранения")
            return
            
        savepoint_name = simpledialog.askstring("откат к точке сохранения", 
                                               f"введите имя точки сохранения для отката:\nактивные точки сохранения: {', '.join(self.savepoints)}")
        if not savepoint_name:
            return
            
        if savepoint_name not in self.savepoints:
            messagebox.showerror("точка сохранения не найдена", 
                               f"точка сохранения '{savepoint_name}' не найдена.\nактивные точки сохранения: {', '.join(self.savepoints)}")
            return
            
        try:
            self.cursor.execute(f"rollback to savepoint {savepoint_name}")
            
            index = self.savepoints.index(savepoint_name)
            self.savepoints = self.savepoints[:index + 1]
            
            messagebox.showinfo("откат выполнен успешно", 
                              f"успешный откат к точке сохранения '{savepoint_name}'")
            self.load_data()
        except Exception as e:
            messagebox.showerror("ошибка отката", f"ошибка отката к точке сохранения: {str(e)}")

    def release_savepoint(self):
        if not self.transaction_active:
            messagebox.showwarning("освободить точку сохранения", "нет активной транзакции")
            return
            
        if not self.savepoints:
            messagebox.showwarning("освободить точку сохранения", "нет активных точек сохранения")
            return
            
        savepoint_name = simpledialog.askstring("освободить точку сохранения", 
                                               f"введите имя точки сохранения для освобождения:\nактивные точки сохранения: {', '.join(self.savepoints)}")
        if not savepoint_name:
            return
            
        if savepoint_name not in self.savepoints:
            messagebox.showerror("точка сохранения не найдена", 
                               f"точка сохранения '{savepoint_name}' не найдена.\nактивные точки сохранения: {', '.join(self.savepoints)}")
            return
            
        try:
            self.cursor.execute(f"release savepoint {savepoint_name}")
            self.savepoints.remove(savepoint_name)
            messagebox.showinfo("точка сохранения освобождена", 
                              f"точка сохранения '{savepoint_name}' освобождена успешно.\n"
                              f"оставшиеся точки сохранения: {', '.join(self.savepoints)}")
        except Exception as e:
            messagebox.showerror("ошибка освобождения", f"ошибка освобождения точки сохранения: {str(e)}")

    def list_savepoints(self):
        if not self.transaction_active:
            messagebox.showinfo("точки сохранения", "нет активной транзакции")
        elif not self.savepoints:
            messagebox.showinfo("точки сохранения", "нет активных точек сохранения")
        else:
            messagebox.showinfo("активные точки сохранения", 
                              f"активные точки сохранения:\n{', '.join(self.savepoints)}")

    def load_data(self):
        try:
            self.cursor.execute("select id, first_name, last_name, gender, email, image, doc from users order by id")
            rows = self.cursor.fetchall()
            
            self.update_treeview(rows)
                
        except Exception as e:
            messagebox.showerror("ошибка базы данных", f"ошибка загрузки данных: {str(e)}")

    def search_data(self):
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.load_data()
            return
            
        try:
            query = """
            select id, first_name, last_name, gender, email, image, doc
            from users 
            where first_name ilike %s 
               or last_name ilike %s 
               or gender ilike %s 
               or email ilike %s 
               or cast(id as text) ilike %s
            order by id
            """
            
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            rows = self.cursor.fetchall()
            
            if not rows:
                messagebox.showinfo("результаты поиска", "пользователи по вашему запросу не найдены.")
                return
                
            self.update_treeview(rows)
            messagebox.showinfo("результаты поиска", f"найдено {len(rows)} пользователей по запросу '{search_term}'")
            
        except Exception as e:
            messagebox.showerror("ошибка поиска", f"ошибка поиска данных: {str(e)}")

    def update_treeview(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in rows:
            # Преобразуем данные для отображения
            display_row = list(row)
            # Заменяем поле image на текст "есть" или "нет"
            display_row[5] = "есть" if row[5] else "нет"
            display_row[6] = "есть" if row[6] else "нет"
            self.tree.insert('', 'end', values=display_row)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_data()

    def validate_input(self):
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        
        if not first_name or not last_name:
            messagebox.showwarning("ошибка проверки", "имя и фамилия обязательны для заполнения!")
            return False
                
        return True

    def add_record(self):
        if not self.validate_input():
            return
            
        try:
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()
            gender = self.gender_combobox.get().strip()
            email = self.email_entry.get().strip() or None
            
            self.cursor.execute(
                "insert into users (first_name, last_name, gender, email, image, doc) values (%s, %s, %s, %s, %s)",
                (first_name, last_name, gender, email, self.current_image_data, self.current_doc_data)
            )
            
            if not self.transaction_active:
                self.conn.commit()
                messagebox.showinfo("успех", "пользователь успешно добавлен!")
            else:
                messagebox.showinfo("успех", "пользователь добавлен в транзакцию!")
            
            self.load_data()
            self.clear_entries()
            
        except psycopg2.IntegrityError as e:
            if not self.transaction_active:
                self.conn.rollback()
            messagebox.showerror("ошибка базы данных", "email уже существует!")
        except Exception as e:
            if not self.transaction_active:
                self.conn.rollback()
            messagebox.showerror("ошибка базы данных", f"ошибка добавления пользователя: {str(e)}")

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("ошибка выбора", "пожалуйста, выберите пользователя для обновления!")
            return
            
        if not self.validate_input():
            return
            
        try:
            record_id = self.tree.item(selected[0])['values'][0]
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()
            gender = self.gender_combobox.get().strip()
            email = self.email_entry.get().strip() or None

            self.cursor.execute(
                """update users 
                set first_name=%s, last_name=%s, gender=%s, email=%s, image=%s, doc=%s
                where id=%s""",
                (first_name, last_name, gender, email, self.current_image_data, self.current_doc_data, record_id)
            )
            
            if not self.transaction_active:
                self.conn.commit()
                messagebox.showinfo("успех", "пользователь успешно обновлен!")
            else:
                messagebox.showinfo("успех", "пользователь обновлен в транзакции!")
            
            self.load_data()
            self.clear_entries()
            
        except psycopg2.IntegrityError as e:
            if not self.transaction_active:
                self.conn.rollback()
            messagebox.showerror("ошибка базы данных", "email уже существует!")
        except Exception as e:
            if not self.transaction_active:
                self.conn.rollback()
            messagebox.showerror("ошибка базы данных", f"ошибка обновления пользователя: {str(e)}")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("ошибка выбора", "пожалуйста, выберите пользователя для удаления!")
            return

        if not messagebox.askyesno("подтверждение удаления", "вы уверены, что хотите удалить этого пользователя?"):
            return

        try:
            record_id = self.tree.item(selected[0])['values'][0]
            self.cursor.execute("delete from users where id=%s", (record_id,))
            
            if not self.transaction_active:
                self.conn.commit()
                messagebox.showinfo("успех", "пользователь успешно удален!")
            else:
                messagebox.showinfo("успех", "пользователь удален в транзакции!")
            
            self.load_data()
            self.clear_entries()
            
        except Exception as e:
            if not self.transaction_active:
                self.conn.rollback()
            messagebox.showerror("ошибка базы данных", f"ошибка удаления пользователя: {str(e)}")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.clear_entries()
            
            # Заполняем поля данными из выбранной строки
            self.id_entry.config(state='normal')
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, values[0] if len(values) > 0 else "")
            self.id_entry.config(state='readonly')
            
            self.first_name_entry.insert(0, values[1] if len(values) > 1 else "")
            self.last_name_entry.insert(0, values[2] if len(values) > 2 else "")
            self.gender_combobox.set(values[3] if len(values) > 3 else "")
            self.email_entry.insert(0, values[4] if len(values) > 4 else "")
            
            # Получаем полные данные пользователя для получения изображения
            try:
                record_id = values[0]
                self.cursor.execute("SELECT image FROM users WHERE id = %s", (record_id,))
                result = self.cursor.fetchone()
                if result and result[0]:
                    self.current_image_data = result[0]
                    self.image_filename_label.config(text="из базы данных")
                else:
                    self.current_image_data = None
                    self.image_filename_label.config(text="файл не выбран")
            except Exception as e:
                messagebox.showerror("ошибка", f"ошибка загрузки изображения: {str(e)}")


            try:
                record_id = values[0]
                self.cursor.execute("SELECT doc FROM users WHERE id = %s", (record_id,))
                result = self.cursor.fetchone()
                if result and result[0]:
                    self.current_doc_data = result[0]
                    self.doc_filename_label.config(text="из базы данных")
                else:
                    self.current_doc_data = None
                    self.doc_filename_label.config(text="файл не выбран")
            except Exception as e:
                messagebox.showerror("ошибка", f"ошибка загрузки изображения: {str(e)}")

    def clear_entries(self):
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.id_entry.config(state='readonly')
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.gender_combobox.set('')
        self.email_entry.delete(0, tk.END)
        self.current_image_data = None
        self.current_doc_data = None
        self.image_filename_label.config(text="файл не выбран")
        self.doc_filename_label.config(text="файл не выбран")

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PostgresGUI(root)
    root.mainloop()
