import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GUI.main_window import MainWindow
from GUI.auth_window import AuthWindow
from database import Database


def create_main_app(root, current_user):
    db_params = {
        'dbname': 'dbproject',
        'user': 'matskevich_av',
        'password': '57U8&Sp66$r',
        'host': '5942e-rw.db.pub.dbaas.postgrespro.ru',
        'port': '5432'
    }

    for widget in root.winfo_children():
        widget.destroy()

    app = MainWindow(root, db_params, current_user)


def main():
    root = tk.Tk()
    root.title("Система бронирования авиабилетов - Авторизация")
    root.geometry("420x350")

    db_params = {
        'dbname': 'dbproject',
        'user': 'matskevich_av',
        'password': '57U8&Sp66$r',
        'host': '5942e-rw.db.pub.dbaas.postgrespro.ru',
        'port': '5432'
    }

    db = Database(db_params)
    if not db.connect():
        tk.messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
        root.destroy()
        return

    auth = AuthWindow(root, lambda user: create_main_app(root, user), db)

    root.mainloop()


if __name__ == "__main__":
    main()