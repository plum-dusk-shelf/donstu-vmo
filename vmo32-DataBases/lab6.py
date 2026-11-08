db_config = {'database' : "lab6",
                               'user' : "simafrus",
                               'password' : "8bzm61K",
                               #host = "localhost",
                               'port' : 5432
        }

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class blob_manager:
    def __init__(self):
        self.connection = None
        self.create_database_if_not_exists()
        self.connect()
        self.create_table()

    def create_database_if_not_exists(self):
        """Создает базу данных, если она не существует"""
        try:
            # подключение к стандартной базе данных postgres
            temp_conn = psycopg2.connect(
                database="postgres",
                user=db_config["user"],
                password=db_config["password"]
            )
            temp_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with temp_conn.cursor() as cursor:
                # проверяем существование базы данных
                cursor.execute(
                    "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                    (db_config["database"],)
                )
                exists = cursor.fetchone()
                
                if not exists:
                    # создаем базу данных
                    cursor.execute(
                        sql.SQL("CREATE DATABASE {}").format(
                            sql.Identifier(db_config["database"])
                        )
                    )
                    print(f"база данных {db_config['database']} создана")
                else:
                    print(f"база данных {db_config['database']} уже существует")
            
            temp_conn.close()
            
        except Exception as e:
            messagebox.showerror("ошибка", f"не удалось создать базу данных: {str(e)}")

    def connect(self):
        try:
            self.connection = psycopg2.connect(**db_config)
            print("подключение к базе данных установлено")
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка подключения: {str(e)}")

    def create_table(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS blob_storage (
                        id SERIAL PRIMARY KEY,
                        doc_data BYTEA,
                        image_data BYTEA,
                        file_name TEXT,
                        file_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.connection.commit()
                print("таблица создана или уже существует")
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка создания таблицы: {str(e)}")

    def insert_blob(self, file_path, file_type):
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            file = file_path.split('/')[-1]
            file_name, file_type = file.split('.')
            
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO blob_storage (doc_data, file_name, file_type) VALUES (%s, %s, %s)",
                    (file_data, file_name, file_type)
                )
                
                self.connection.commit()
                messagebox.showinfo("успех", f"файл {file_name} добавлен")
                
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка вставки: {str(e)}")

    def recover_doc(self, doc_id, save_path):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT doc_data, file_name FROM blob_storage WHERE id = %s AND doc_data IS NOT NULL",
                    (doc_id,)
                )
                result = cursor.fetchone()
                
                if result and result[0]:
                    file_data, file_name = result
                    # добавляем оригинальное расширение файла
                    if '.' in file_name and not save_path.endswith(file_name.split('.')[-1]):
                        save_path = save_path.rsplit('.', 1)[0] + '.' + file_name.split('.')[-1]
                    
                    with open(save_path, 'wb') as f:
                        f.write(file_data)
                    messagebox.showinfo("успех", f"документ сохранен в {save_path}")
                else:
                    messagebox.showwarning("предупреждение", "документ не найден")
                    
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка восстановления: {str(e)}")

    def recover_image(self, image_id, save_path):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT image_data, file_name FROM blob_storage WHERE id = %s AND image_data IS NOT NULL",
                    (image_id,)
                )
                result = cursor.fetchone()
                
                if result and result[0]:
                    file_data, file_name = result
                    # добавляем оригинальное расширение файла
                    if '.' in file_name and not save_path.endswith(file_name.split('.')[-1]):
                        save_path = save_path.rsplit('.', 1)[0] + '.' + file_name.split('.')[-1]
                    
                    with open(save_path, 'wb') as f:
                        f.write(file_data)
                    messagebox.showinfo("успех", f"изображение сохранено в {save_path}")
                else:
                    messagebox.showwarning("предупреждение", "изображение не найдено")
                    
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка восстановления: {str(e)}")

    def get_all_records(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, file_name, file_type, created_at 
                    FROM blob_storage 
                    ORDER BY id
                """)
                return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка получения записей: {str(e)}")
            return []

    def delete_record(self, record_id):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM blob_storage WHERE id = %s", (record_id,))
                self.connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            messagebox.showerror("ошибка", f"ошибка удаления записи: {str(e)}")
            return False

class application:
    def __init__(self, root):
        self.root = root
        self.manager = blob_manager()
        self.setup_ui()

    def setup_ui(self):
        self.root.title("управление blob-данными")
        self.root.geometry("400x280")
        
        # фрейм для кнопок
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        # кнопки для документов
        tk.Button(button_frame, text="добавить документ", command=self.add_doc, width=20).pack(pady=5)
        tk.Button(button_frame, text="восстановить документ", command=self.recover_doc, width=20).pack(pady=5)
        
        '''
        # кнопки для изображений
        tk.Button(button_frame, text="добавить изображение", command=self.add_image, width=20).pack(pady=5)
        tk.Button(button_frame, text="восстановить изображение", command=self.recover_image, width=20).pack(pady=5)
        '''
        
        # кнопки для управления записями
        tk.Button(button_frame, text="показать все записи", command=self.show_records, width=20).pack(pady=5)
        tk.Button(button_frame, text="удалить запись", command=self.delete_record, width=20).pack(pady=5)

    def add_doc(self):
        path = filedialog.askopenfilename(
            title="выберите документ",
            filetypes=[("документы", "*.pdf *.docx *.txt *.doc *.rtf"), ("все файлы", "*.*")]
        )
        if path:
            self.manager.insert_blob(path, "doc")

    def add_image(self):
        path = filedialog.askopenfilename(
            title="выберите изображение", 
            filetypes=[("изображения", "*.png *.jpg *.jpeg *.gif *.bmp"), ("все файлы", "*.*")]
        )
        if path:
            self.manager.insert_blob(path, "image")

    def recover_doc(self):
        doc_id = simpledialog.askinteger("id документа", "введите id документа для восстановления:")
        if doc_id:
            path = filedialog.asksaveasfilename(
                title="сохранить документ как",
                defaultextension=".*",
                filetypes=[("все файлы", "*.*")]
            )
            if path:
                self.manager.recover_doc(doc_id, path)

    def recover_image(self):
        image_id = simpledialog.askinteger("id изображения", "введите id изображения для восстановления:")
        if image_id:
            path = filedialog.asksaveasfilename(
                title="сохранить изображение как",
                defaultextension=".*",
                filetypes=[("все файлы", "*.*")]
            )
            if path:
                self.manager.recover_image(image_id, path)

    def show_records(self):
        records = self.manager.get_all_records()
        if records:
            records_window = tk.Toplevel(self.root)
            records_window.title("все записи в базе данных")
            records_window.geometry("600x400")
            
            # создаем текстовое поле с прокруткой
            frame = tk.Frame(records_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(frame, wrap=tk.NONE)
            scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
            scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            text_widget.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            text_widget.grid(row=0, column=0, sticky="nsew")
            scrollbar_y.grid(row=0, column=1, sticky="ns")
            scrollbar_x.grid(row=1, column=0, sticky="ew")
            
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            
            # заголовок
            text_widget.insert(tk.END, "id | имя файла | тип файла | дата создания\n")
            text_widget.insert(tk.END, "-" * 70 + "\n")
            
            for record in records:
                text_widget.insert(tk.END, f"{record[0]} | {record[1]} | {record[2]} | {record[3]}\n")
            
            text_widget.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("информация", "в базе данных нет записей")

    def delete_record(self):
        record_id = simpledialog.askinteger("удаление записи", "введите id записи для удаления:")
        if record_id:
            if self.manager.delete_record(record_id):
                messagebox.showinfo("успех", f"запись с id {record_id} удалена")
            else:
                messagebox.showwarning("предупреждение", f"запись с id {record_id} не найдена")

if __name__ == "__main__":
    root = tk.Tk()
    app = application(root)
    root.mainloop()
