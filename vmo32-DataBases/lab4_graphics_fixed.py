db_config = {'database' : "myfirstdb",
                               'user' : "simafrus",
                               'password' : "8bzm61K",
                               #'host' : "localhost",
                               'port' : 5432
        }

import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

class PostgresGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PostgreSQL Users Management")
        self.root.geometry("750x550")
        
        # Параметры подключения к БД - ЗАМЕНИТЕ НА СВОИ
        self.db_config = db_config
        
        self.create_widgets()
        self.connect_to_db()
        self.load_data()

    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Фрейм для поиска
        search_frame = ttk.LabelFrame(main_frame, text="Search Users")
        search_frame.pack(fill="x", pady=(0, 10))
        
        # Поле поиска и кнопка
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_data).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search).grid(row=0, column=3, padx=5, pady=5)
        
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(main_frame, text="User Information")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Создаем сетку для полей ввода
        ttk.Label(input_frame, text="First Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.first_name_entry = ttk.Entry(input_frame, width=20)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Last Name:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.last_name_entry = ttk.Entry(input_frame, width=20)
        self.last_name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Gender:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.gender_combobox = ttk.Combobox(input_frame, values=["Male", "Female", "Other"], width=18)
        self.gender_combobox.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Email:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.email_entry = ttk.Entry(input_frame, width=20)
        self.email_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add User", command=self.add_record).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Update User", command=self.update_record).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete User", command=self.delete_record).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Fields", command=self.clear_entries).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh Data", command=self.load_data).pack(side="left", padx=5)
        
        # Таблица для отображения данных
        table_frame = ttk.LabelFrame(main_frame, text="Users Table")
        table_frame.pack(fill="both", expand=True)
        
        # Создаем Treeview с нужными колонками
        columns = ('ID', 'First Name', 'Last Name', 'Gender', 'Email')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Настраиваем заголовки колонок
        self.tree.heading('ID', text='ID')
        self.tree.heading('First Name', text='First Name')
        self.tree.heading('Last Name', text='Last Name')
        self.tree.heading('Gender', text='Gender')
        self.tree.heading('Email', text='Email')
        
        # Настраиваем ширину колонок
        self.tree.column('ID', width=50)
        self.tree.column('First Name', width=120)
        self.tree.column('Last Name', width=120)
        self.tree.column('Gender', width=80)
        self.tree.column('Email', width=200)
        
        # Добавляем scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещаем элементы
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Привязка события выбора элемента в таблице
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Привязка события нажатия Enter в поле поиска
        self.search_entry.bind('<Return>', lambda event: self.search_data())

    def connect_to_db(self):
        """Установка соединения с базой данных"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            # Создаем таблицу если она не существует
            self.create_table_if_not_exists()
        except Exception as e:
            messagebox.showerror("Database Error", f"Connection failed: {str(e)}")

    def create_table_if_not_exists(self):
        """Создание таблицы если она не существует"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            gender VARCHAR(10),
            email VARCHAR(100) UNIQUE
        );
        """
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Table creation failed: {str(e)}")

    def load_data(self):
        """Загрузка всех данных из базы в таблицу"""
        try:
            self.cursor.execute("SELECT id, first_name, last_name, gender, email FROM users ORDER BY id")
            rows = self.cursor.fetchall()
            
            self.update_treeview(rows)
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load data: {str(e)}")

    def search_data(self):
        """Поиск данных по всем полям"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.load_data()
            return
            
        try:
            # Поиск по всем полям с использованием ILIKE для регистронезависимого поиска
            query = """
            SELECT id, first_name, last_name, gender, email 
            FROM users 
            WHERE first_name ILIKE %s 
               OR last_name ILIKE %s 
               OR gender ILIKE %s 
               OR email ILIKE %s 
               OR CAST(id AS TEXT) ILIKE %s
            ORDER BY id
            """
            
            search_pattern = f"%{search_term}%"
            self.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            rows = self.cursor.fetchall()
            
            if not rows:
                messagebox.showinfo("Search Result", "No users found matching your search criteria.")
                return
                
            self.update_treeview(rows)
            messagebox.showinfo("Search Result", f"Found {len(rows)} user(s) matching '{search_term}'")
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search data: {str(e)}")

    def update_treeview(self, rows):
        """Обновление данных в Treeview"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение данными
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def clear_search(self):
        """Очистка поля поиска и загрузка всех данных"""
        self.search_entry.delete(0, tk.END)
        self.load_data()

    def validate_input(self):
        """Проверка корректности введенных данных"""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        
        if not first_name or not last_name:
            messagebox.showwarning("Validation Error", "First Name and Last Name are required!")
            return False
                
        return True

    def add_record(self):
        """Добавление новой записи"""
        if not self.validate_input():
            return
            
        try:
            first_name = self.first_name_entry.get().strip()
            last_name = self.last_name_entry.get().strip()
            gender = self.gender_combobox.get().strip()
            email = self.email_entry.get().strip() or None
            
            self.cursor.execute(
                "INSERT INTO users (first_name, last_name, gender, email) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, gender, email)
            )
            self.conn.commit()
            self.load_data()
            self.clear_entries()
            messagebox.showinfo("Success", "User added successfully!")
            
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", "Email already exists!")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to add user: {str(e)}")

    def update_record(self):
        """Обновление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a user to update!")
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
                """UPDATE users 
                SET first_name=%s, last_name=%s, gender=%s, email=%s 
                WHERE id=%s""",
                (first_name, last_name, gender, email, record_id)
            )
            self.conn.commit()
            self.load_data()
            self.clear_entries()
            messagebox.showinfo("Success", "User updated successfully!")
            
        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", "Email already exists!")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to update user: {str(e)}")

    def delete_record(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a user to delete!")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            return

        try:
            record_id = self.tree.item(selected[0])['values'][0]
            self.cursor.execute("DELETE FROM users WHERE id=%s", (record_id,))
            self.conn.commit()
            self.load_data()
            self.clear_entries()
            messagebox.showinfo("Success", "User deleted successfully!")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to delete user: {str(e)}")

    def on_select(self, event):
        """Заполнение полей ввода при выборе записи в таблице"""
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.clear_entries()
            
            # Заполняем поля данными из выбранной строки
            self.first_name_entry.insert(0, values[1] if len(values) > 1 else "")
            self.last_name_entry.insert(0, values[2] if len(values) > 2 else "")
            self.gender_combobox.set(values[3] if len(values) > 3 else "")
            self.email_entry.insert(0, values[4] if len(values) > 4 else "")

    def clear_entries(self):
        """Очистка всех полей ввода"""
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.gender_combobox.set('')
        self.email_entry.delete(0, tk.END)

    def __del__(self):
        """Закрытие соединения с БД при уничтожении объекта"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PostgresGUI(root)
    root.mainloop()
