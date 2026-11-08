import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

class PostgresGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PostgreSQL GUI")
        
        # Параметры подключения к БД
        self.db_config = {'database' : "myfirstdb",
                               'user' : "simafrus",
                               'password' : "8bzm61K",
                               #host = "localhost",
                               'port' : 5432
        }
        
        self.create_widgets()
        self.connect_to_db()
        self.load_data()

    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=10)

        ttk.Label(input_frame, text="Name:").grid(row=0, column=0)
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1)

        ttk.Label(input_frame, text="Email:").grid(row=1, column=0)
        self.email_entry = ttk.Entry(input_frame)
        self.email_entry.grid(row=1, column=1)

        # Кнопки операций
        ttk.Button(input_frame, text="Add", command=self.add_record).grid(row=2, column=0, pady=5)
        ttk.Button(input_frame, text="Update", command=self.update_record).grid(row=2, column=1)
        ttk.Button(input_frame, text="Delete", command=self.delete_record).grid(row=2, column=2)

        # Таблица для отображения данных
        self.tree = ttk.Treeview(self.root, columns=('ID', 'Name', 'Email'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Email', text='Email')
        self.tree.pack(padx=10, pady=10)

        # Привязка события выбора элемента в таблице
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def connect_to_db(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Error", f"Database connection failed: {str(e)}")

    def load_data(self):
        try:
            self.cursor.execute("SELECT * FROM users")
            rows = self.cursor.fetchall()
            
            # Очистка таблицы
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Заполнение данными
            for row in rows:
                self.tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def add_record(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        
        if not name or not email:
            messagebox.showwarning("Warning", "Please fill all fields")
            return

        try:
            self.cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                (name, email)
            )
            self.conn.commit()
            self.load_data()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add record: {str(e)}")

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to update")
            return

        name = self.name_entry.get()
        email = self.email_entry.get()
        record_id = self.tree.item(selected[0])['values'][0]

        try:
            self.cursor.execute(
                "UPDATE users SET name=%s, email=%s WHERE id=%s",
                (name, email, record_id)
            )
            self.conn.commit()
            self.load_data()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update record: {str(e)}")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a record to delete")
            return

        record_id = self.tree.item(selected[0])['values'][0]

        try:
            self.cursor.execute("DELETE FROM users WHERE id=%s", (record_id,))
            self.conn.commit()
            self.load_data()
            self.clear_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {str(e)}")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])['values']
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, values[2])

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PostgresGUI(root)
    root.mainloop()
