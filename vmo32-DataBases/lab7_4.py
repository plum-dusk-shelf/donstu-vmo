from lab4_graphics_fixed import db_config

#!/usr/bin/env python3
"""
tk_partition_orders.py

Tkinter GUI to help partition an existing PostgreSQL table `orders`.
Features:
 - Connect to PostgreSQL via psycopg2
 - Inspect table columns and preview first rows (Treeview)
 - Choose any column and partition type (range, list, hash)
 - Configure partition boundaries or values
 - Preview generated SQL
 - Create a new partitioned table (CREATE TABLE ... (LIKE orders INCLUDING ALL) PARTITION BY ...)
 - Create partitions, COPY data into new table, and optionally swap/rename tables

IMPORTANT: The tool creates a *new* partitioned table and does NOT drop the original `orders` unless you explicitly confirm.
Use carefully and always backup your database before changing production data.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2
from psycopg2 import sql
from datetime import datetime, date, timedelta
import math
import traceback


DB_SAMPLE = db_config

TABLE_NAME = 'orders'


def quote_literal(val, typ):
    # Return SQL literal appropriate for simple types
    if val is None:
        return 'NULL'
    if 'char' in typ or 'text' in typ or 'name' in typ:
        return "'" + str(val).replace("'", "''") + "'"
    if 'date' in typ or 'timestamp' in typ:
        return "'" + str(val) + "'"
    # numeric
    return str(val)


class PartitionGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # initialize optional UI attributes to avoid AttributeError when switching methods
        self.values_box = None
        self.manual_values_entry = None
        self.range_start = None
        self.range_end = None
        self.range_interval = None
        self.hash_n = None
        self.col_info = []
        self.title('Postgres Partitioning GUI — orders')
        self.geometry('1100x700')

        self.conn = None
        self.col_info = []  # list of (column_name, data_type)

        self._build_ui()

    def _build_ui(self):
        # Connection frame
        conn_frame = ttk.LabelFrame(self, text='Connection')
        conn_frame.pack(fill='x', padx=8, pady=6)

        self.entries = {}
        for i, (k, v) in enumerate(DB_SAMPLE.items()):
            ttk.Label(conn_frame, text=k).grid(row=0, column=2*i)
            e = ttk.Entry(conn_frame)
            e.grid(row=0, column=2*i+1, padx=4)
            e.insert(0, v)
            self.entries[k] = e

        ttk.Button(conn_frame, text='Connect', command=self.connect_db).grid(row=0, column=9, padx=8)
        ttk.Button(conn_frame, text='Refresh table preview', command=self.refresh_preview).grid(row=0, column=10)

        # Main panes
        main_pane = ttk.Panedwindow(self, orient='horizontal')
        main_pane.pack(fill='both', expand=True, padx=8, pady=6)

        left = ttk.Frame(main_pane, width=600)
        right = ttk.Frame(main_pane, width=400)
        main_pane.add(left, weight=3)
        main_pane.add(right, weight=2)

        # Left: Treeview showing table rows
        table_frame = ttk.LabelFrame(left, text=f'Table: {TABLE_NAME} (preview)')
        table_frame.pack(fill='both', expand=True, padx=4, pady=4)

        self.tree = ttk.Treeview(table_frame, show='headings')
        self.tree.pack(fill='both', expand=True, side='left')

        vsb = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        # Right: Partition options
        opts_frame = ttk.LabelFrame(right, text='Partition options')
        opts_frame.pack(fill='both', expand=True, padx=4, pady=4)

        ttk.Label(opts_frame, text='Column:').grid(row=0, column=0, sticky='w')
        self.col_var = tk.StringVar()
        self.col_combo = ttk.Combobox(opts_frame, textvariable=self.col_var, state='readonly')
        self.col_combo.grid(row=0, column=1, sticky='ew', padx=4, pady=2)
        self.col_combo.bind('<<ComboboxSelected>>', lambda e: self.on_column_selected())

        ttk.Label(opts_frame, text='Method:').grid(row=1, column=0, sticky='w')
        self.method_var = tk.StringVar(value='range')
        methods = [('Range', 'range'), ('List', 'list'), ('Hash', 'hash')]
        for i, (lab, val) in enumerate(methods):
            rb = ttk.Radiobutton(opts_frame, text=lab, variable=self.method_var, value=val, command=self.on_method_changed)
            rb.grid(row=1, column=1+i, sticky='w')

        # Dynamic options area
        self.dynamic_frame = ttk.Frame(opts_frame)
        self.dynamic_frame.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=6)

        # Buttons
        btn_frame = ttk.Frame(opts_frame)
        btn_frame.grid(row=10, column=0, columnspan=4, sticky='ew', pady=6)
        ttk.Button(btn_frame, text='Preview SQL', command=self.preview_sql).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Apply partition', command=self.apply_partition).pack(side='left', padx=4)

        # SQL preview area
        sql_frame = ttk.LabelFrame(right, text='Generated SQL / Logs')
        sql_frame.pack(fill='both', expand=True, padx=4, pady=4)
        self.sql_text = scrolledtext.ScrolledText(sql_frame, height=15)
        self.sql_text.pack(fill='both', expand=True)

        # Status bar
        self.status_var = tk.StringVar(value='Disconnected')
        status = ttk.Label(self, textvariable=self.status_var, relief='sunken', anchor='w')
        status.pack(fill='x')

        # Populate initial dynamic UI
        self.on_method_changed()

    def log(self, *parts):
        s = ' '.join(str(p) for p in parts)
        self.sql_text.insert('end', f"{datetime.now().isoformat()} - {s}\n")
        self.sql_text.see('end')

    def connect_db(self):
        params = {k: e.get().strip() for k, e in self.entries.items()}
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass
        try:
            self.conn = psycopg2.connect(**params)
            self.status_var.set(f"Connected to {params['database']}")#@{params['host']}:{params['port']}")
            self.load_columns()
            self.refresh_preview()
            self.log('Connected')
        except Exception as e:
            messagebox.showerror('Connection failed', str(e))
            self.status_var.set('Disconnected')
            self.log('Connection failed:', e)

    def execute(self, query, params=None, fetch=False):
        cur = self.conn.cursor()
        try:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            return None
        finally:
            cur.close()

    def load_columns(self):
        q = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        cur = self.conn.cursor()
        cur.execute(q, (TABLE_NAME,))
        rows = cur.fetchall()
        cur.close()
        self.col_info = rows
        cols = [r[0] for r in rows]
        self.col_combo['values'] = cols
        if cols:
            self.col_combo.current(0)
            self.on_column_selected()

    def refresh_preview(self):
        if not self.conn:
            return
        cur = self.conn.cursor()
        # fetch up to 200 rows
        cur.execute(sql.SQL('SELECT * FROM {} LIMIT 200').format(sql.Identifier(TABLE_NAME)))
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        cur.close()

        # configure tree
        self.tree.delete(*self.tree.get_children())
        self.tree['columns'] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor='w')
        for r in rows:
            self.tree.insert('', 'end', values=r)

        self.log(f'Preview loaded {len(rows)} rows')

    def on_column_selected(self):
        self.on_method_changed()

    def clear_dynamic(self):
        for w in self.dynamic_frame.winfo_children():
            w.destroy()

    def on_method_changed(self):
        self.clear_dynamic()
        method = self.method_var.get()
        col = self.col_var.get()
        dtype = None
        for c, t in self.col_info:
            if c == col:
                dtype = t
                break

        if method == 'range':
            ttk.Label(self.dynamic_frame, text='Range partition settings').grid(row=0, column=0, sticky='w')
            ttk.Label(self.dynamic_frame, text='Start (optional)').grid(row=1, column=0, sticky='w')
            self.range_start = ttk.Entry(self.dynamic_frame)
            self.range_start.grid(row=1, column=1, sticky='ew')
            ttk.Label(self.dynamic_frame, text='End (optional)').grid(row=2, column=0, sticky='w')
            self.range_end = ttk.Entry(self.dynamic_frame)
            self.range_end.grid(row=2, column=1, sticky='ew')
            ttk.Label(self.dynamic_frame, text='Interval').grid(row=3, column=0, sticky='w')
            self.range_interval = ttk.Entry(self.dynamic_frame)
            self.range_interval.insert(0, '1')
            self.range_interval.grid(row=3, column=1, sticky='ew')

            # If date-like, helper buttons
            if dtype and ('date' in dtype or 'timestamp' in dtype):
                ttk.Button(self.dynamic_frame, text='Use year partitions', command=lambda: self.range_interval.insert(0, 'year')).grid(row=3, column=2)
                ttk.Button(self.dynamic_frame, text='Use month partitions', command=lambda: self.range_interval.insert(0, 'month')).grid(row=3, column=3)

        elif method == 'list':
            ttk.Label(self.dynamic_frame, text='List partition settings').grid(row=0, column=0, sticky='w')
            btn_frame = ttk.Frame(self.dynamic_frame)
            btn_frame.grid(row=1, column=0, columnspan=4, sticky='w')
            ttk.Button(btn_frame, text='Load distinct values', command=self.load_distinct_values).pack(side='left', padx=2)
            ttk.Label(btn_frame, text='or enter values (comma-separated):').pack(side='left', padx=6)
            self.manual_values_entry = ttk.Entry(btn_frame)
            self.manual_values_entry.pack(side='left', fill='x', expand=True)
            ttk.Button(btn_frame, text='Add', command=self.add_manual_values).pack(side='left', padx=2)

            self.values_box = tk.Listbox(self.dynamic_frame, selectmode='extended', height=8)
            self.values_box.grid(row=2, column=0, columnspan=4, sticky='nsew')
            # small control row under listbox
            ctrl_frame = ttk.Frame(self.dynamic_frame)
            ctrl_frame.grid(row=3, column=0, columnspan=4, sticky='ew')
            ttk.Button(ctrl_frame, text='Remove selected', command=self.remove_selected_values).pack(side='left', padx=4)
            ttk.Button(ctrl_frame, text='Clear all', command=lambda: self.values_box.delete(0, 'end')).pack(side='left')
            # bind Enter key on manual entry to add values
            self.manual_values_entry.bind('<Return>', lambda e: self.add_manual_values())


        elif method == 'hash':
            ttk.Label(self.dynamic_frame, text='Hash partition settings').grid(row=0, column=0, sticky='w')
            ttk.Label(self.dynamic_frame, text='Number of partitions:').grid(row=1, column=0, sticky='w')
            self.hash_n = ttk.Entry(self.dynamic_frame)
            self.hash_n.insert(0, '4')
            self.hash_n.grid(row=1, column=1, sticky='w')

    def load_distinct_values(self):
        # ensure values_box exists
        if self.values_box is None:
            messagebox.showerror('Error', 'Values listbox not available')
            return

        col = self.col_var.get()
        cur = self.conn.cursor()
        cur.execute(sql.SQL('SELECT DISTINCT {} FROM {} ORDER BY 1 LIMIT 1000').format(sql.Identifier(col), sql.Identifier(TABLE_NAME)))
        vals = [r[0] for r in cur.fetchall()]
        cur.close()
        self.values_box.delete(0, 'end')
        for v in vals:
            self.values_box.insert('end', str(v))
        self.log(f'Loaded {len(vals)} distinct values for {col}')

    def build_sql(self):
        col = self.col_var.get()
        method = self.method_var.get()
        if not (col and method):
            raise ValueError('Column and method must be selected')

        new_table = f"{TABLE_NAME}_partitioned_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        sql_statements = []

        # create partitioned table like original
        create_parent = sql.SQL("CREATE TABLE {new} (LIKE {orig} INCLUDING ALL) PARTITION BY {ptype} ({col});").format(
            new=sql.Identifier(new_table),
            orig=sql.Identifier(TABLE_NAME),
            ptype=sql.SQL(method.upper()),
            col=sql.Identifier(col)
        )
        sql_statements.append(create_parent.as_string(self.conn))

        # partition creation
        if method == 'range':
            # determine min/max
            cur = self.conn.cursor()
            cur.execute(sql.SQL('SELECT MIN({c}), MAX({c}) FROM {t}').format(c=sql.Identifier(col), t=sql.Identifier(TABLE_NAME)))
            mn, mx = cur.fetchone()
            cur.close()

            # allow overrides
            start = self.range_start.get().strip()
            end = self.range_end.get().strip()
            interval = self.range_interval.get().strip()

            if start:
                mn = start
            if end:
                mx = end
            if mn is None or mx is None:
                raise ValueError('Cannot determine range bounds (table may be empty). Provide start/end manually.')

            # if interval is 'year' or 'month' we create partitions accordingly
            if interval.lower() in ('year', 'month'):
                # handle date-like values
                cur = self.conn.cursor()
                cur.execute(sql.SQL('SELECT data_type FROM information_schema.columns WHERE table_name=%s AND column_name=%s'), (TABLE_NAME, col))
                dtype = cur.fetchone()[0]
                cur.close()
                if 'date' not in dtype and 'timestamp' not in dtype:
                    raise ValueError('year/month interval only valid for date/timestamp columns')
                start_dt = mn if isinstance(mn, (date, datetime)) else datetime.fromisoformat(str(mn))
                end_dt = mx if isinstance(mx, (date, datetime)) else datetime.fromisoformat(str(mx))
                cur_dt = start_dt
                while cur_dt <= end_dt:
                    if interval.lower() == 'year':
                        next_dt = date(cur_dt.year + 1, 1, 1)
                        part_name = f"{new_table}_{cur_dt.year}"
                        from_val = date(cur_dt.year, 1, 1)
                        to_val = date(cur_dt.year + 1, 1, 1)
                    else:  # month
                        year = cur_dt.year
                        month = cur_dt.month
                        if month == 12:
                            n_year = year + 1
                            n_month = 1
                        else:
                            n_year = year
                            n_month = month + 1
                        part_name = f"{new_table}_{year}_{month:02d}"
                        from_val = date(year, month, 1)
                        to_val = date(n_year, n_month, 1)
                    stmt = sql.SQL('CREATE TABLE {p} PARTITION OF {parent} FOR VALUES FROM ({from_v}) TO ({to_v});').format(
                        p=sql.Identifier(part_name),
                        parent=sql.Identifier(new_table),
                        from_v=sql.SQL(quote_literal(from_val, 'date')),
                        to_v=sql.SQL(quote_literal(to_val, 'date'))
                    )
                    sql_statements.append(stmt.as_string(self.conn))
                    # increment
                    if interval.lower() == 'year':
                        cur_dt = date(cur_dt.year + 1, 1, 1)
                    else:
                        if cur_dt.month == 12:
                            cur_dt = date(cur_dt.year + 1, 1, 1)
                        else:
                            cur_dt = date(cur_dt.year, cur_dt.month + 1, 1)

            else:
                # numeric interval
                try:
                    step = float(interval)
                except Exception:
                    raise ValueError('Interval must be "year", "month" or a numeric value')
                # generate numeric ranges from mn to mx stepping by step
                cur_start = float(mn)
                cur_end = cur_start + step
                idx = 0
                while cur_start < float(mx) + 1e-12:
                    part_name = f"{new_table}_p{idx}"
                    stmt = sql.SQL('CREATE TABLE {p} PARTITION OF {parent} FOR VALUES FROM ({from_v}) TO ({to_v});').format(
                        p=sql.Identifier(part_name),
                        parent=sql.Identifier(new_table),
                        from_v=sql.SQL(str(cur_start)),
                        to_v=sql.SQL(str(cur_end))
                    )
                    sql_statements.append(stmt.as_string(self.conn))
                    cur_start = cur_end
                    cur_end = cur_start + step
                    idx += 1

        elif method == 'list':
            # get selected values
            sel_indexes = list(self.values_box.curselection())
            if sel_indexes:
                sel = [self.values_box.get(i) for i in sel_indexes]
            else:
                # if nothing selected, use all values in the listbox
                sel = [self.values_box.get(i) for i in range(self.values_box.size())]
            if not sel:
                raise ValueError('No list values provided for list partitioning')
            for i, v in enumerate(sel):
                part_name = f"{new_table}_list_{i}"
                # attempt to type cast based on column data type
                dtype = None
                for c, t in self.col_info:
                    if c == col:
                        dtype = t
                        break
                lit = quote_literal(v, dtype or '')
                stmt = sql.SQL('CREATE TABLE {p} PARTITION OF {parent} FOR VALUES IN ({val});').format(
                    p=sql.Identifier(part_name),
                    parent=sql.Identifier(new_table),
                    val=sql.SQL(lit)
                )
                sql_statements.append(stmt.as_string(self.conn))
            # default partition
            stmt = sql.SQL('CREATE TABLE {p} PARTITION OF {parent} DEFAULT;').format(
                p=sql.Identifier(f"{new_table}_default"),
                parent=sql.Identifier(new_table)
            )
            sql_statements.append(stmt.as_string(self.conn))

        elif method == 'hash':
            n = int(self.hash_n.get().strip())
            if n <= 0:
                raise ValueError('Number of partitions must be positive')
            for i in range(n):
                part_name = f"{new_table}_h{i}"
                stmt = sql.SQL('CREATE TABLE {p} PARTITION OF {parent} FOR VALUES WITH (MODULUS {m}, REMAINDER {r});').format(
                    p=sql.Identifier(part_name),
                    parent=sql.Identifier(new_table),
                    m=sql.Literal(n),
                    r=sql.Literal(i)
                )
                sql_statements.append(stmt.as_string(self.conn))

        # insert data into new table
        insert_stmt = sql.SQL('INSERT INTO {new} SELECT * FROM {orig};').format(new=sql.Identifier(new_table), orig=sql.Identifier(TABLE_NAME))
        sql_statements.append(insert_stmt.as_string(self.conn))

        # final swap/rename statements (performed only after confirmation in apply)
        rename_old = sql.SQL('ALTER TABLE {orig} RENAME TO {old_backup};').format(orig=sql.Identifier(TABLE_NAME), old_backup=sql.Identifier(f"{TABLE_NAME}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"))
        rename_new = sql.SQL('ALTER TABLE {new} RENAME TO {orig};').format(new=sql.Identifier(new_table), orig=sql.Identifier(TABLE_NAME))
        sql_statements.append('-- NOTE: The following renames will be executed only if you confirm when applying:')
        sql_statements.append(rename_old.as_string(self.conn))
        sql_statements.append(rename_new.as_string(self.conn))

        return sql_statements

    def add_manual_values(self):
        if self.manual_values_entry is None or self.values_box is None:
            return
        raw = self.manual_values_entry.get().strip()
        if not raw:
            return
        # split by comma and add trimmed values
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        for p in parts:
            self.values_box.insert('end', p)
        self.manual_values_entry.delete(0, 'end')

    def remove_selected_values(self):
        if self.values_box is None:
            return
        sel = list(self.values_box.curselection())
        # delete from end to avoid index shift
        for i in reversed(sel):
            self.values_box.delete(i)

    def preview_sql(self):
        try:
            stmts = self.build_sql()
            self.sql_text.delete('1.0', 'end')
            for s in stmts:
                self.sql_text.insert('end', s + '\n')
            self.sql_text.see('end')
        except Exception as e:
            messagebox.showerror('Error building SQL', str(e))
            self.log('Error building SQL:', traceback.format_exc())

    def apply_partition(self):
        try:
            stmts = self.build_sql()
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return

        # Show the key statements and ask for confirmation
        preview = '\n'.join(stmts[:5]) + '\n...\n' + '\n'.join(stmts[-3:])
        if not messagebox.askyesno('Confirm', f'This will create a new partitioned table and copy data.\nPreview:\n{preview}\n\nProceed?'):
            return

        cur = self.conn.cursor()
        try:
            # execute create & partitions & insert but stop before renames
            for s in stmts:
                if s.startswith('-- NOTE:'):
                    break
                self.log('Executing:', s)
                cur.execute(s)
            self.conn.commit()
            self.log('Partitioned table created and data copied.')

            # ask about renaming (swap)
            if messagebox.askyesno('Swap tables', 'Do you want to rename old table to backup and replace it with partitioned table now?'):
                # execute renames (last two statements are rename_old and rename_new)
                # find last two non-comment statements
                renames = [s for s in stmts if s.startswith('ALTER TABLE')]
                for s in renames:
                    self.log('Executing:', s)
                    cur.execute(s)
                self.conn.commit()
                self.log('Rename completed. Original table renamed to backup; partitioned table is now named orders.')
                messagebox.showinfo('Done', 'Partitioning complete and tables swapped.')
            else:
                messagebox.showinfo('Done', 'Partitioning complete. New table created but original table left in place (no rename).')

            self.refresh_preview()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Error executing SQL', str(e))
            self.log('Execution error:', traceback.format_exc())
        finally:
            cur.close()


if __name__ == '__main__':
    app = PartitionGUI()
    app.mainloop()

