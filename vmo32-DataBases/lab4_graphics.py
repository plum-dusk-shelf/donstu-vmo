import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2
from psycopg2 import Error


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
        #self.load_data()

    def create_widgets(self):
        # Input frame for SQL commands
        input_frame = ttk.LabelFrame(self.root, text="SQL Command Input")
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # ScrolledText widget for multi-line SQL input
        self.sql_input = scrolledtext.ScrolledText(input_frame, height=8, font=("Consolas", 10))
        self.sql_input.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        # Execute button
        self.execute_btn = ttk.Button(button_frame, text="Execute Query", command=self.execute_query)
        self.execute_btn.pack(side="left", padx=5)
        
        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_input)
        clear_btn.pack(side="left", padx=5)
        
        # Output frame for results
        output_frame = ttk.LabelFrame(self.root, text="Query Results")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview widget for displaying results in a table format
        self.result_tree = ttk.Treeview(output_frame)
        
        # Scrollbars for the treeview
        v_scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.result_tree.yview)
        h_scrollbar = ttk.Scrollbar(output_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack the treeview and scrollbars
        self.result_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

    def connect_to_db(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            messagebox.showinfo("Success", "Database connection established!")
        except Error as e:
            messagebox.showerror("Connection Error", f"Failed to connect to database:\n{str(e)}")

    def execute_query(self):
        """Execute the SQL query from input area and display results"""
        sql_command = self.sql_input.get("1.0", tk.END).strip()
        
        if not sql_command:
            messagebox.showwarning("Warning", "Please enter a SQL command")
            return
        
        try:
            # Execute the query
            self.cursor.execute(sql_command)
            
            # Check if query produces results (SELECT-like statements)
            if self.cursor.description:
                # Get column names
                columns = [desc[0] for desc in self.cursor.description]
                
                # Clear previous results
                self.result_tree.delete(*self.result_tree.get_children())
                
                # Configure treeview columns
                self.result_tree["columns"] = columns
                self.result_tree["show"] = "headings"
                
                # Set up column headers
                for col in columns:
                    self.result_tree.heading(col, text=col)
                    self.result_tree.column(col, width=100, minwidth=50)
                
                # Fetch and display all rows
                rows = self.cursor.fetchall()
                for row in rows:
                    self.result_tree.insert("", "end", values=row)
                    
                messagebox.showinfo("Success", f"Query executed successfully!\n{len(rows)} rows returned")
            else:
                # For INSERT, UPDATE, DELETE etc.
                self.conn.commit()
                affected_rows = self.cursor.rowcount
                messagebox.showinfo("Success", f"Query executed successfully!\n{affected_rows} rows affected")
                
                # Clear any previous results since this wasn't a SELECT
                self.result_tree.delete(*self.result_tree.get_children())
                self.result_tree["columns"] = []
                
        except Error as e:
            messagebox.showerror("Query Error", f"Error executing query:\n{str(e)}")

    def clear_input(self):
        """Clear the SQL input area"""
        self.sql_input.delete("1.0", tk.END)

    def __del__(self):
        """Clean up database connection when object is destroyed"""
        if hasattr(self, 'conn'):
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = PostgresGUI(root)
    root.mainloop()
