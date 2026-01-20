import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class AuthWindow:
    def __init__(self, parent, on_success_callback, db):
        self.parent = parent
        self.on_success_callback = on_success_callback
        self.db = db
        self.current_user = None

        self.saved_username = ""
        self.saved_password = ""
        self.saved_remember_login = False
        self.saved_remember_password = False

        self.auth_frame = ttk.Frame(parent, padding="20")
        self.auth_frame.pack(fill=tk.BOTH, expand=True)

        self.show_auth_form()

    def show_auth_form(self):
        for widget in self.auth_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.auth_frame, text="Авторизация",
                  font=("Arial", 16, "bold")).pack(pady=10)

        ttk.Label(self.auth_frame, text="Логин:").pack(pady=5)
        self.username_var = tk.StringVar(value=self.saved_username)
        username_entry = ttk.Entry(self.auth_frame, textvariable=self.username_var, width=30)
        username_entry.pack(pady=5)

        ttk.Label(self.auth_frame, text="Пароль:").pack(pady=5)
        self.password_var = tk.StringVar(value=self.saved_password)
        password_entry = ttk.Entry(self.auth_frame, textvariable=self.password_var,
                                   show="*", width=30)
        password_entry.pack(pady=5)

        self.remember_login_var = tk.BooleanVar(value=self.saved_remember_login)
        self.remember_password_var = tk.BooleanVar(value=self.saved_remember_password)

        ttk.Checkbutton(self.auth_frame, text="Запомнить логин",
                        variable=self.remember_login_var).pack(pady=2, anchor=tk.W)
        ttk.Checkbutton(self.auth_frame, text="Запомнить пароль",
                        variable=self.remember_password_var).pack(pady=2, anchor=tk.W)

        self.load_saved_credentials()

        button_frame = ttk.Frame(self.auth_frame)
        button_frame.pack(pady=15)

        ttk.Button(button_frame, text="Войти",
                   command=self.login, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Регистрация",
                   command=self.show_reg_form, width=15).pack(side=tk.LEFT, padx=5)

        username_entry.focus_set()

    def show_reg_form(self):
        if hasattr(self, 'username_var') and hasattr(self, 'password_var'):
            self.saved_username = self.username_var.get()
            self.saved_password = self.password_var.get()
            if hasattr(self, 'remember_login_var'):
                self.saved_remember_login = self.remember_login_var.get()
            if hasattr(self, 'remember_password_var'):
                self.saved_remember_password = self.remember_password_var.get()

        for widget in self.auth_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.auth_frame, text="Регистрация",
                  font=("Arial", 16, "bold")).pack(pady=10)

        ttk.Label(self.auth_frame, text="Логин:").pack(pady=5)
        self.reg_username_var = tk.StringVar()
        ttk.Entry(self.auth_frame, textvariable=self.reg_username_var,
                  width=30).pack(pady=5)

        ttk.Label(self.auth_frame, text="Пароль:").pack(pady=5)
        self.reg_password_var = tk.StringVar()
        ttk.Entry(self.auth_frame, textvariable=self.reg_password_var,
                  show="*", width=30).pack(pady=5)

        ttk.Label(self.auth_frame, text="Подтвердите пароль:").pack(pady=5)
        self.reg_confirm_var = tk.StringVar()
        ttk.Entry(self.auth_frame, textvariable=self.reg_confirm_var,
                  show="*", width=30).pack(pady=5)

        button_frame = ttk.Frame(self.auth_frame)
        button_frame.pack(pady=15)

        ttk.Button(button_frame, text="Зарегистрироваться",
                   command=self.register, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Назад",
                   command=self.show_auth_form, width=10).pack(side=tk.LEFT, padx=5)

        self.auth_frame.focus_set()

    def load_saved_credentials(self):
        try:
            if os.path.exists("auth_settings.json"):
                with open("auth_settings.json", 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if not self.saved_username and settings.get("remember_login", False):
                        self.username_var.set(settings.get("username", ""))
                        self.remember_login_var.set(True)
                    if not self.saved_password and settings.get("remember_password", False):
                        self.password_var.set(settings.get("password", ""))
                        self.remember_password_var.set(True)
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")

    def save_credentials(self):
        settings = {
            "username": self.username_var.get() if self.remember_login_var.get() else "",
            "password": self.password_var.get() if self.remember_password_var.get() else "",
            "remember_login": self.remember_login_var.get(),
            "remember_password": self.remember_password_var.get()
        }

        try:
            with open("auth_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return

        user = self.db.authenticate_user(username, password)
        if user:
            self.current_user = user

            self.save_credentials()

            self.auth_frame.destroy()
            self.on_success_callback(self.current_user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def register(self):
        username = self.reg_username_var.get().strip()
        password = self.reg_password_var.get().strip()
        confirm = self.reg_confirm_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return

        if len(username) < 3:
            messagebox.showerror("Ошибка", "Логин должен быть не менее 3 символов")
            return

        if password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return

        if self.db.check_user_exists(username):
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует")
            return

        user_id = self.db.register_user(username, password)
        if user_id:
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")

            self.saved_username = username
            self.saved_password = password
            self.saved_remember_login = True
            self.saved_remember_password = True

            self.show_auth_form()
        else:
            messagebox.showerror("Ошибка", "Ошибка при регистрации пользователя")