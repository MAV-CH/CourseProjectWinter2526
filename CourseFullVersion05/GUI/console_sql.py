import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pandas as pd
import sys
import os
from datetime import datetime
from database import Database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SQLConsoleDialog:
    def __init__(self, parent, db: Database):
        self.parent = parent
        self.db = db

        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title("SQL Консоль")
        self.dialog.geometry("1200x700")
        self.dialog.transient(parent.root)
        self.dialog.grab_set()

        if not hasattr(parent, 'current_user') or not parent.current_user.get('admin'):
            messagebox.showerror("Ошибка", "Доступ запрещен. Требуются права администратора.")
            self.dialog.destroy()
            return

        self.create_widgets()
        self.history = []
        self.history_index = -1

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(top_frame, text="Выполнить (F5)", command=self.execute_query, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Очистить", command=self.clear_console, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="История запросов", command=self.show_history, width=15).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Экспорт в CSV", command=self.export_to_csv, width=15).pack(side=tk.LEFT, padx=2)

        query_frame = ttk.LabelFrame(main_frame, text="SQL Запрос", padding="5")
        query_frame.pack(fill=tk.BOTH, expand=True)

        self.query_text = scrolledtext.ScrolledText(query_frame, height=8, font=("Courier", 10))
        self.query_text.pack(fill=tk.BOTH, expand=True)
        self.query_text.bind('<F5>', lambda e: self.execute_query())

        results_frame = ttk.LabelFrame(main_frame, text="Результаты", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.results_tree = ttk.Treeview(results_frame, show="headings")

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        self.query_text.focus_set()

    def execute_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Внимание", "Введите SQL запрос")
            return
        if not self.history or self.history[-1] != query:
            self.history.append(query)
            self.history_index = len(self.history)
        try:
            self.status_var.set("Выполнение запроса")
            self.dialog.update()

            query_lower = query.lower().strip()
            if query_lower.startswith(('select', 'show', 'explain', 'with')):
                with self.db.connection.cursor() as cursor:
                    cursor.execute(query)

                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        for item in self.results_tree.get_children():
                            self.results_tree.delete(item)
                        self.results_tree['columns'] = columns
                        for col in columns:
                            self.results_tree.heading(col, text=col)
                            self.results_tree.column(col, width=100, minwidth=50)
                        for row in rows:
                            self.results_tree.insert("", tk.END, values=row)

                        self.status_var.set(f"Запрос выполнен. Найдено {len(rows)} записей")
                    else:
                        self.status_var.set("Запрос выполнен успешно. Затронуто строк: " + str(cursor.rowcount))

            else:
                with self.db.connection.cursor() as cursor:
                    cursor.execute(query)
                    self.db.connection.commit()
                    self.status_var.set(f"Запрос выполнен. Затронуто строк: {cursor.rowcount}")

                messagebox.showinfo("Успех", f"Запрос выполнен успешно\nЗатронуто строк: {cursor.rowcount}")

        except Exception as e:
            self.status_var.set("Ошибка выполнения запроса")
            messagebox.showerror("Ошибка SQL", f"Ошибка выполнения запроса:\n{str(e)}")
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            self.results_tree['columns'] = ("Ошибка",)
            self.results_tree.heading("Ошибка", text="Ошибка")
            self.results_tree.column("Ошибка", width=800)
            self.results_tree.insert("", tk.END, values=(str(e),))

    def clear_console(self):
        self.query_text.delete("1.0", tk.END)
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.status_var.set("Готов")

    def show_history(self):
        history_dialog = tk.Toplevel(self.dialog)
        history_dialog.title("История запросов")
        history_dialog.geometry("600x400")

        main_frame = ttk.Frame(history_dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="История SQL запросов", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        history_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        history_text.pack(fill=tk.BOTH, expand=True)

        for i, query in enumerate(self.history, 1):
            history_text.insert(tk.END, f"{i}. {query}\n{'-' * 80}\n")
        history_text.config(state='disabled')

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Закрыть", command=history_dialog.destroy).pack(side=tk.RIGHT)

    def export_to_csv(self):
        items = self.results_tree.get_children()
        if not items:
            messagebox.showwarning("Внимание", "Нет данных для экспорта")
            return

        try:
            columns = self.results_tree['columns']
            data = []
            for item in items:
                values = self.results_tree.item(item)['values']
                data.append(values)
            df = pd.DataFrame(data, columns=columns)
            filename = f"sql_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            messagebox.showinfo("Успех", f"Данные экспортированы в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")

    def navigate_history(self, direction):
        if not self.history:
            return

        if direction == 'up':
            if self.history_index > 0:
                self.history_index -= 1
        elif direction == 'down':
            if self.history_index < len(self.history) - 1:
                self.history_index += 1

        if 0 <= self.history_index < len(self.history):
            self.query_text.delete("1.0", tk.END)
            self.query_text.insert("1.0", self.history[self.history_index])