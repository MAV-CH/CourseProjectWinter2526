import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
from GUI.widgets import ConfirmationDialog

class AddFlightDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить рейс")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Номер рейса:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.number_flight_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.number_flight_var, width=20).grid(row=0, column=1, pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Время вылета (ЧЧ:ММ):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.time_flight_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.time_flight_var, width=20).grid(row=1, column=1, pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Самолет:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.airplane_combo = ttk.Combobox(main_frame, width=25, state="readonly")
        self.airplane_combo.grid(row=2, column=1, pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Маршрут:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.airport_combo = ttk.Combobox(main_frame, width=25, state="readonly")
        self.airport_combo.grid(row=3, column=1, pady=5, sticky=tk.W)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        airplanes = self.db.get_all_airplanes()
        airplane_list = [f"{a.id}: {a.name_airplane}" for a in airplanes]
        self.airplane_combo['values'] = airplane_list
        if airplane_list:
            self.airplane_combo.current(0)
        airports = self.db.get_all_airports()
        airport_list = [f"{a.id}: {a.start_airport} → {a.finish_airport}" for a in airports]
        self.airport_combo['values'] = airport_list
        if airport_list:
            self.airport_combo.current(0)

    def save(self):
        try:
            number_flight = self.number_flight_var.get().strip()
            time_flight = self.time_flight_var.get().strip()

            if not number_flight or not time_flight:
                messagebox.showwarning("Ошибка", "Заполните все поля")
                return

            airplane_text = self.airplane_combo.get()
            airport_text = self.airport_combo.get()

            if not airplane_text or not airport_text:
                messagebox.showwarning("Ошибка", "Выберите самолет и маршрут")
                return

            id_airplane = int(airplane_text.split(':')[0])
            id_airport = int(airport_text.split(':')[0])

            flight_id = self.db.add_flight(
                id_airplane=id_airplane,
                id_airport=id_airport,
                number_flight=int(number_flight),
                time_flight=time_flight
            )

            if flight_id:
                messagebox.showinfo("Успех", f"Рейс #{flight_id} успешно добавлен")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить рейс")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")


class AddPassengerDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить пассажира")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Имя:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.first_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.first_name_var, width=30).grid(row=0, column=1, pady=10)

        ttk.Label(main_frame, text="Фамилия:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.second_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.second_name_var, width=30).grid(row=1, column=1, pady=10)

        ttk.Label(main_frame, text="Телефон:").grid(row=2, column=0, sticky=tk.W, pady=10)
        self.phone_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.phone_var, width=30).grid(row=2, column=1, pady=10)

        ttk.Label(main_frame, text="Паспорт:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.passport_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.passport_var, width=30).grid(row=3, column=1, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        try:
            first_name = self.first_name_var.get().strip()
            second_name = self.second_name_var.get().strip()
            phone = self.phone_var.get().strip()
            passport = self.passport_var.get().strip()

            if not all([first_name, second_name, phone, passport]):
                messagebox.showwarning("Ошибка", "Заполните все поля")
                return

            passenger_id = self.db.add_passenger(
                first_name=first_name,
                second_name=second_name,
                number_phone=phone,
                number_passport=passport
            )

            if passenger_id:
                messagebox.showinfo("Успех", f"Пассажир #{passenger_id} успешно добавлен")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить пассажира")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")


class CreateBookingDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать бронирование")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Рейс:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.flight_combo = ttk.Combobox(main_frame, width=40, state="readonly")
        self.flight_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.flight_combo.bind('<<ComboboxSelected>>', self.on_flight_selected)

        ttk.Label(main_frame, text="Пассажир:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.passenger_combo = ttk.Combobox(main_frame, width=40, state="readonly")
        self.passenger_combo.grid(row=1, column=1, pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Место:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.place_combo = ttk.Combobox(main_frame, width=40, state="readonly")
        self.place_combo.grid(row=2, column=1, pady=5, sticky=tk.W)

        ttk.Label(main_frame, text="Статус:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Подтверждено", variable=self.status_var).grid(row=3, column=1, pady=5, sticky=tk.W)

        self.info_label = ttk.Label(main_frame, text="", foreground="blue")
        self.info_label.grid(row=4, column=0, columnspan=2, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Создать", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        flights = self.db.get_all_flights()
        flight_list = [f"{f['id']}: Рейс #{f['number_flight']} - {f['airport']}" for f in flights]
        self.flight_combo['values'] = flight_list
        if flight_list:
            self.flight_combo.current(0)
            self.on_flight_selected(None)

        passengers = self.db.get_all_passengers()
        passenger_list = [f"{p.id}: {p.first_name} {p.second_name}" for p in passengers]
        self.passenger_combo['values'] = passenger_list
        if passenger_list:
            self.passenger_combo.current(0)

    def on_flight_selected(self, event):
        flight_text = self.flight_combo.get()
        if flight_text:
            flight_id = int(flight_text.split(':')[0])
            # обновление инфы о рейсе
            flights = self.db.get_all_flights()
            selected_flight = next((f for f in flights if f['id'] == flight_id), None)
            if selected_flight:
                info = f"{selected_flight['airport']} | {selected_flight['time_flight']} | {selected_flight['name_company']}"
                self.info_label.config(text=info)

            # загрузка доступных мест
            self.load_available_places(flight_id)

    def load_available_places(self, flight_id: int):
        places = self.db.get_available_places(flight_id)
        place_list = [f"{p['id']}: {p['seat_class']}{p['row_number']}{p['seat_letter']}" for p in places]
        self.place_combo['values'] = place_list
        if place_list:
            self.place_combo.current(0)
        else:
            self.place_combo.set('')
            messagebox.showwarning("Внимание", "Нет свободных мест на выбранный рейс")

    def save(self):
        try:
            flight_text = self.flight_combo.get()
            passenger_text = self.passenger_combo.get()
            place_text = self.place_combo.get()

            if not all([flight_text, passenger_text, place_text]):
                messagebox.showwarning("Ошибка", "Заполните все поля")
                return

            flight_id = int(flight_text.split(':')[0])
            passenger_id = int(passenger_text.split(':')[0])
            place_id = int(place_text.split(':')[0])

            booking_id = self.db.create_booking(
                id_flight=flight_id,
                id_place=place_id,
                id_passenger=passenger_id,
                status=self.status_var.get()
            )

            if booking_id:
                messagebox.showinfo("Успех", f"Бронирование #{booking_id} успешно создано")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать бронирование. Возможно, место уже занято.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании бронирования: {e}")


class EditCompanyDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Управление авиакомпаниями")
        self.dialog.geometry("550x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.load_companies()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Новая авиакомпания:", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=5)

        add_frame = ttk.Frame(main_frame)
        add_frame.pack(fill=tk.X, pady=10)

        self.new_company_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.new_company_var, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(add_frame, text="Добавить", command=self.add_company).pack(side=tk.LEFT)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text="Список авиакомпаний:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)

        ttk.Button(header_frame, text="Удалить выбранную", command=self.delete_company).pack(side=tk.RIGHT)

        columns = ("ID", "Название")
        self.company_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.company_tree.heading(col, text=col)
            self.company_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.company_tree.yview)
        self.company_tree.configure(yscrollcommand=scrollbar.set)

        self.company_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    def load_companies(self):
        companies = self.db.get_all_companies()
        for item in self.company_tree.get_children():
            self.company_tree.delete(item)
        for company in companies:
            self.company_tree.insert("", tk.END, values=(company.id, company.name_company))

    def add_company(self):
        name = self.new_company_var.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Введите название компании")
            return

        company_id = self.db.add_company(name)
        if company_id:
            messagebox.showinfo("Успех", f"Компания #{company_id} добавлена")
            self.new_company_var.set("")
            self.load_companies()
            if self.callback:
                self.callback()

    def delete_company(self):
        selection = self.company_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите компанию для удаления")
            return
        company_id = self.company_tree.item(selection[0])['values'][0]
        company_name = self.company_tree.item(selection[0])['values'][1]
        if ConfirmationDialog.askyesno(self.parent, "Подтверждение", f"Удалить компанию '{company_name}'?"):
            if self.db.delete_company(company_id):
                messagebox.showinfo("Успех", "Компания удалена")
                self.load_companies()
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить компанию. Возможно, есть связанные записи.")


class ManageUsersDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.main_window = parent
        self.db = db
        self.callback = callback

        self.dialog = tk.Toplevel(parent.root)
        self.dialog.title("Управление пользователями")
        self.dialog.geometry("950x500")
        self.dialog.transient(parent.root)
        self.dialog.grab_set()

        if hasattr(parent, 'current_user'):
            self.current_user = parent.current_user
        else:
            self.current_user = {'nickname': 'Неизвестный', 'admin': False}
        if not self.current_user.get('admin'):
            messagebox.showerror("Ошибка", "Доступ запрещен. Требуются права администратора.")
            self.dialog.destroy()
            return

        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Управление пользователями", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        admin_info = f"Текущий администратор: {self.current_user.get('nickname', 'Неизвестный')}"
        ttk.Label(main_frame, text=admin_info, font=("Arial", 14)).pack(pady=(0, 10))

        columns = ("ID", "Логин", "Роль")
        self.users_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Логин", text="Логин")
        self.users_tree.heading("Роль", text="Роль")

        self.users_tree.column("ID", width=50)
        self.users_tree.column("Логин", width=150)
        self.users_tree.column("Роль", width=150)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.selected_info = tk.StringVar(value="Выберите пользователя")
        info_label = ttk.Label(actions_frame, textvariable=self.selected_info, wraplength=200, justify=tk.LEFT)
        info_label.pack(pady=(0, 15))

        role_frame = ttk.LabelFrame(actions_frame, text="Назначить роль", padding="10")
        role_frame.pack(fill=tk.X, pady=5)
        ttk.Button(role_frame, text="Администратор", command=lambda: self.set_user_role('ADMIN'), width=20).pack(pady=3, fill=tk.X)
        ttk.Button(role_frame, text="Старший сотрудник", command=lambda: self.set_user_role('SENIOR'), width=20).pack(pady=3, fill=tk.X)
        ttk.Button(role_frame, text="Обычный сотрудник", command=lambda: self.set_user_role('EMPLOYEE'), width=20).pack(pady=3, fill=tk.X)
        ttk.Button(actions_frame, text="Удалить роль", command=self.remove_user_role, width=20).pack(pady=10, fill=tk.X)

        ttk.Separator(actions_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        delete_frame = ttk.LabelFrame(actions_frame, text="", padding="10")
        delete_frame.pack(fill=tk.X, pady=5)
        ttk.Button(delete_frame, text="Удалить пользователя", command=self.delete_user, width=20).pack(pady=3, fill=tk.X)
        ttk.Button(delete_frame, text="Обновить список", command=self.load_users, width=20).pack(pady=3, fill=tk.X)
        ttk.Button(actions_frame, text="Закрыть", command=self.dialog.destroy, width=20).pack(pady=20, fill=tk.X)

        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_selected)

    def on_user_selected(self, event):
        user = self.get_selected_user()
        if user:
            role_display = self.get_role_display(user['role'])
            self.selected_info.set(f"Выбран: {user['nickname']}\nРоль: {role_display}")

    def get_role_display(self, role):
        role_map = {
            'ADMIN': 'Администратор',
            'SENIOR': 'Старший сотрудник',
            'EMPLOYEE': 'Обычный сотрудник',
            True: 'Администратор',
            False: 'Обычный сотрудник'
        }
        return role_map.get(role, role)

    def get_role_code(self, role_display):
        role_map_reverse = {
            'Администратор': 'ADMIN',
            'Старший сотрудник': 'SENIOR',
            'Обычный сотрудник': 'EMPLOYEE'
        }
        return role_map_reverse.get(role_display, 'EMPLOYEE')

    def load_users(self):
        users = self.db.get_all_users()
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        for user in users:
            if 'role' in user:
                role = user['role']
            else:
                role = 'ADMIN' if user.get('admin') else 'EMPLOYEE'

            role_display = self.get_role_display(role)

            self.users_tree.insert("", tk.END, values=(
                user['id'], user['nickname'], role_display
            ))

    def get_selected_user(self):
        selection = self.users_tree.selection()
        if not selection:
            return None

        values = self.users_tree.item(selection[0])['values']

        return {
            'id': values[0],
            'nickname': values[1],
            'role': self.get_role_code(values[2]),
            'role_display': values[2]
        }

    def set_user_role(self, new_role):
        user = self.get_selected_user()
        if not user:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return

        if self.current_user.get('id') == user['id'] and new_role != 'ADMIN':
            messagebox.showerror("Ошибка", "Нельзя понизить свою роль")
            return

        if user['role'] == 'ADMIN' and new_role != 'ADMIN':
            if not self.check_if_other_admins_exist(user['id']):
                messagebox.showerror("Ошибка",
                                     "Нельзя убрать права администратора у последнего администратора в системе")
                return

        new_role_display = self.get_role_display(new_role)

        if user['role'] == new_role:
            messagebox.showinfo("Информация", f"Пользователь уже имеет роль '{new_role_display}'")
            return

        if ConfirmationDialog.askyesno(self.dialog, "Подтверждение",
                                       f"Назначить пользователю '{user['nickname']}' роль '{new_role_display}'?"):

            if hasattr(self.db, 'update_user_role'):
                success = self.db.update_user_role(user['id'], new_role)
            else:
                is_admin = new_role == 'ADMIN'
                success = self.db.update_user_admin(user['id'], is_admin)

            if success:
                messagebox.showinfo("Успех", f"Роль '{new_role_display}' назначена пользователю")
                self.load_users()
                self.on_user_selected(None)  #
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Ошибка", "Не удалось изменить роль пользователя")

    def remove_user_role(self):
        user = self.get_selected_user()
        if not user:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return

        if user['role'] == 'EMPLOYEE':
            messagebox.showinfo("Информация", "Пользователь уже имеет базовую роль 'Обычный сотрудник'")
            return

        if self.current_user.get('id') == user['id']:
            messagebox.showerror("Ошибка", "Нельзя изменить свою роль")
            return

        if ConfirmationDialog.askyesno(self.dialog, "Подтверждение",
                                       f"Вернуть пользователя '{user['nickname']}' в базовую роль 'Обычный сотрудник'?"):

            if hasattr(self.db, 'update_user_role'):
                success = self.db.update_user_role(user['id'], 'EMPLOYEE')
            else:
                success = self.db.update_user_admin(user['id'], False)

            if success:
                messagebox.showinfo("Успех", "Пользователь возвращен в базовую роль")
                self.load_users()
                self.on_user_selected(None)
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Ошибка", "Не удалось изменить роль пользователя")

    def check_if_other_admins_exist(self, exclude_user_id):
        users = self.db.get_all_users()
        admin_count = 0

        for user in users:
            if user['id'] == exclude_user_id:
                continue

            if 'role' in user:
                if user['role'] == 'ADMIN':
                    admin_count += 1
            else:
                if user.get('admin'):
                    admin_count += 1

        return admin_count > 0

    def delete_user(self):
        user = self.get_selected_user()
        if not user:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return

        if self.current_user.get('id') == user['id']:
            messagebox.showerror("Ошибка", "Нельзя удалить себя")
            return

        if ConfirmationDialog.askyesno(self.dialog, "Подтверждение",
                                       f"Удалить пользователя '{user['nickname']}'?"):
            if self.db.delete_user(user['id']):
                messagebox.showinfo("Успех", "Пользователь удален")
                self.load_users()
                self.selected_info.set("Выберите пользователя")
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя")

class AddAirplaneDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить самолет")
        self.dialog.geometry("480x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.load_companies()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Название самолета:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=10)

        ttk.Label(main_frame, text="Авиакомпания:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.company_combo = ttk.Combobox(main_frame, width=28, state="readonly")
        self.company_combo.grid(row=1, column=1, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить", command=self.save, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def load_companies(self):
        companies = self.db.get_all_companies()
        company_list = [f"{c.id}: {c.name_company}" for c in companies]
        self.company_combo['values'] = company_list
        if company_list:
            self.company_combo.current(0)

    def save(self):
        try:
            name = self.name_var.get().strip()
            company_text = self.company_combo.get()
            if not name:
                messagebox.showwarning("Ошибка", "Введите название самолета")
                return
            if not company_text:
                messagebox.showwarning("Ошибка", "Выберите авиакомпанию")
                return

            company_id = int(company_text.split(':')[0])
            airplane_id = self.db.add_airplane(name, company_id)

            if airplane_id:
                messagebox.showinfo("Успех", f"Самолет #{airplane_id} успешно добавлен")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить самолет")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")


class AddAirportDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить маршрут")
        self.dialog.geometry("480x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Аэропорт отправления:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.start_airport_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.start_airport_var, width=30).grid(row=0, column=1, pady=10)

        ttk.Label(main_frame, text="Аэропорт прибытия:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.finish_airport_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.finish_airport_var, width=30).grid(row=1, column=1, pady=10)

        info_frame = ttk.LabelFrame(main_frame, text="Информация")
        info_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=tk.EW)

        info_text = """Введите названия аэропортов.
Примеры:
- SVO-LED
- ARE-EMO
- KJI-YOI"""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Сохранить", command=self.save, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)

    def save(self):
        try:
            start = self.start_airport_var.get().strip()
            finish = self.finish_airport_var.get().strip()
            if not start or not finish:
                messagebox.showwarning("Ошибка", "Заполните все поля")
                return
            if start.lower() == finish.lower():
                messagebox.showwarning("Ошибка", "Аэропорты отправления и прибытия не могут совпадать")
                return

            airport_id = self.db.add_airport(start, finish)
            if airport_id:
                messagebox.showinfo("Успех", f"Маршрут #{airport_id} успешно добавлен: {start} → {finish}")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить маршрут")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")


class CreateBookingDialog:
    def __init__(self, parent, db: Database, callback=None):
        self.parent = parent
        self.db = db
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать бронирование")
        self.dialog.geometry("700x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Рейс:", font=("Arial", 14)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.flight_combo = ttk.Combobox(main_frame, width=40, state="readonly")
        self.flight_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.flight_combo.bind('<<ComboboxSelected>>', self.on_flight_selected)

        ttk.Label(main_frame, text="Пассажир:", font=("Arial", 14)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.passenger_combo = ttk.Combobox(main_frame, width=40, state="readonly")
        self.passenger_combo.grid(row=1, column=1, pady=5, sticky=tk.W)

        self.seat_stats_label = ttk.Label(main_frame, text="", font=("Arial", 14))
        self.seat_stats_label.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.W)

        seat_frame = ttk.LabelFrame(main_frame, text="Выбор места", padding="10")
        seat_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W + tk.E)

        ttk.Label(seat_frame, text="Класс:", font=("Arial", 14)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.class_combo = ttk.Combobox(seat_frame, values=["BUS", "ECO"], state="readonly", width=15)
        self.class_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.class_combo.set("ECO")
        self.class_combo.bind('<<ComboboxSelected>>', self.on_class_selected)

        ttk.Label(seat_frame, text="Ряд:", font=("Arial", 14)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.row_combo = ttk.Combobox(seat_frame, width=15, state="readonly")
        self.row_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        self.row_combo.bind('<<ComboboxSelected>>', self.on_row_selected)

        ttk.Label(seat_frame, text="Место:", font=("Arial", 14)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.letter_combo = ttk.Combobox(seat_frame, values=["A", "B", "C", "D"], state="readonly", width=15)
        self.letter_combo.grid(row=2, column=1, pady=5, sticky=tk.W)
        self.letter_combo.set("A")

        self.seat_info_label = ttk.Label(main_frame, text="", foreground="blue")
        self.seat_info_label.grid(row=4, column=0, columnspan=2, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Создать", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        self.current_flight_id = None
        self.selected_seat = None

    def load_data(self):
        flights = self.db.get_all_flights()
        flight_list = [f"{f['id']}: Рейс #{f['number_flight']} - {f['airport']}" for f in flights]
        self.flight_combo['values'] = flight_list
        if flight_list:
            self.flight_combo.current(0)
            self.on_flight_selected(None)

        passengers = self.db.get_all_passengers()
        passenger_list = [f"{p.id}: {p.first_name} {p.second_name}" for p in passengers]
        self.passenger_combo['values'] = passenger_list
        if passenger_list:
            self.passenger_combo.current(0)

    def on_flight_selected(self, event):
        flight_text = self.flight_combo.get()
        if flight_text:
            self.current_flight_id = int(flight_text.split(':')[0])

            flights = self.db.get_all_flights()
            selected_flight = next((f for f in flights if f['id'] == self.current_flight_id), None)
            if selected_flight:
                info = f"{selected_flight['airport']} | {selected_flight['time_flight']} | {selected_flight['name_company']}"
                self.seat_info_label.config(text=info)

            self.load_seat_statistics()

            self.on_class_selected(None)

    def load_seat_statistics(self):
        if not self.current_flight_id:
            return
        stats = self.db.get_seat_statistics(self.current_flight_id)
        business_stats = stats.get('BUS', {'total': 12, 'booked': 0, 'available': 12})
        economy_stats = stats.get('ECO', {'total': 40, 'booked': 0, 'available': 40})

        text = f"Статистика мест: Бизнес: {business_stats['available']}/{business_stats['total']} свободно | " \
               f"Эконом: {economy_stats['available']}/{economy_stats['total']} свободно"
        self.seat_stats_label.config(text=text, font=("Arial", 14))

    def on_class_selected(self, event):
        if not self.current_flight_id:
            return
        selected_class = self.class_combo.get()
        if selected_class == "BUS":
            rows = list(range(1, 4))
        else:  # ECONOMY
            rows = list(range(1, 11))

        self.row_combo['values'] = rows
        self.load_occupied_seats(selected_class)

    def on_row_selected(self, event):
        self.check_seat_availability()

    def load_occupied_seats(self, seat_class):
        if not self.current_flight_id:
            return
        seats = self.db.get_all_places_for_flight(self.current_flight_id)

        #создаем карту занятых мест
        occupied_seats = set()
        for seat in seats:
            if seat.seat_class == seat_class:
                #проверяем, занято ли место
                if not self.db.is_seat_available(seat.id, self.current_flight_id):
                    occupied_seats.add(f"{seat.row_number}{seat.seat_letter}")
        #можно подсветить занятые места в интерфейсе
        if hasattr(self, 'seat_map_frame'):
            self.seat_map_frame.destroy()

        self.create_seat_map(seat_class, occupied_seats)

    def create_seat_map(self, seat_class, occupied_seats):
        map_frame = ttk.LabelFrame(self.dialog, text=f"Карта мест ({seat_class} класс)", padding="10")
        map_frame.place(x=480, y=30, width=200, height=320)
        ttk.Label(map_frame, text="   A   B   C   D").pack(pady=5)

        rows = 3 if seat_class == "BUS" else 10
        for row in range(1, rows + 1):
            row_frame = ttk.Frame(map_frame)
            row_frame.pack(pady=2)
            ttk.Label(row_frame, text=f"{row:2d}", width=3).pack(side=tk.LEFT)
            for letter in ['A', 'B', 'C', 'D']:
                seat_label = ttk.Label(row_frame, text="□", width=2, relief="ridge")
                seat_label.pack(side=tk.LEFT, padx=1)
                seat_key = f"{row}{letter}"
                if seat_key in occupied_seats:
                    seat_label.config(text="✗", foreground="red", background="lightgray")
                else:
                    seat_label.config(text="□", foreground="green")
                    seat_label.bind("<Button-1>", lambda e, r=row, l=letter: self.select_seat_from_map(r, l))

    def select_seat_from_map(self, row, letter):
        selected_class = self.class_combo.get()
        seat = self.db.find_seat_by_details(
            self.current_flight_id,
            selected_class,
            row,
            letter
        )
        if seat:
            self.selected_seat = seat
            self.row_combo.set(str(row))
            self.letter_combo.set(letter)

            self.check_seat_availability()

    def check_seat_availability(self):
        if not self.current_flight_id:
            return
        selected_class = self.class_combo.get()
        row_text = self.row_combo.get()
        letter = self.letter_combo.get()
        if not all([selected_class, row_text, letter]):
            return

        row = int(row_text)
        if not self.db.validate_seat(selected_class, row, letter):
            self.seat_info_label.config(text="Некорректное место", foreground="red")
            self.selected_seat = None
            return

        seat = self.db.find_seat_by_details(self.current_flight_id, selected_class, row, letter)
        if not seat:
            self.seat_info_label.config(text="Место не найдено", foreground="red")
            self.selected_seat = None
            return

        if self.db.is_seat_available(seat.id, self.current_flight_id):
            self.seat_info_label.config(text=f"Место {seat.number_place} ({seat.seat_class}) доступно", foreground="green"
            )
            self.selected_seat = seat
        else:
            self.seat_info_label.config(text=f"Место {seat.number_place} ({seat.seat_class}) занято", foreground="red"
            )
            self.selected_seat = None

    def save(self):
        try:
            flight_text = self.flight_combo.get()
            passenger_text = self.passenger_combo.get()
            if not all([flight_text, passenger_text]):
                messagebox.showwarning("Ошибка", "Выберите рейс и пассажира")
                return
            if not self.selected_seat:
                messagebox.showwarning("Ошибка", "Выберите свободное место")
                return
            if not self.db.is_seat_available(self.selected_seat.id, self.current_flight_id):
                messagebox.showwarning("Ошибка", "Место уже занято. Обновите список мест.")
                self.check_seat_availability()
                return

            flight_id = int(flight_text.split(':')[0])
            passenger_id = int(passenger_text.split(':')[0])
            place_id = self.selected_seat.id
            booking_id = self.db.create_booking(
                id_flight=flight_id,
                id_place=place_id,
                id_passenger=passenger_id,
                status=True
            )

            if booking_id:
                messagebox.showinfo("Успех",
                                    f"Бронирование #{booking_id} создано\n"
                                    f"Место: {self.selected_seat.number_place} ({self.selected_seat.seat_class})")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать бронирование")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании бронирования: {e}")


class EditFlightDialog:
    def __init__(self, parent, db: Database, flight_id: int, flight_data: dict, callback=None):
        self.parent = parent
        self.db = db
        self.flight_id = flight_id
        self.flight_data = flight_data
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Редактировать рейс #{flight_id}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=f"Редактирование рейса #{self.flight_id}", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="Номер рейса:").grid(row=0, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        self.number_flight_var = tk.StringVar(value=self.flight_data.get('number_flight', ''))
        ttk.Entry(input_frame, textvariable=self.number_flight_var, width=20).grid(row=0, column=1, pady=10, sticky=tk.W)

        ttk.Label(input_frame, text="Время вылета (ЧЧ:ММ):").grid(row=1, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        self.time_flight_var = tk.StringVar(value=self.flight_data.get('time_flight', ''))
        ttk.Entry(input_frame, textvariable=self.time_flight_var, width=20).grid(row=1, column=1, pady=10, sticky=tk.W)

        ttk.Label(input_frame, text="Самолет:").grid(row=2, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        self.airplane_combo = ttk.Combobox(input_frame, width=25, state="readonly")
        self.airplane_combo.grid(row=2, column=1, pady=10, sticky=tk.W)

        ttk.Label(input_frame, text="Маршрут:").grid(row=3, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        self.airport_combo = ttk.Combobox(input_frame, width=25, state="readonly")
        self.airport_combo.grid(row=3, column=1, pady=10, sticky=tk.W)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)

        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        airplanes = self.db.get_all_airplanes()
        airplane_list = [f"{a.id}: {a.name_airplane}" for a in airplanes]
        self.airplane_combo['values'] = airplane_list

        current_airplane_id = self.flight_data.get('id_airplane')
        current_found = False
        for i, airplane_str in enumerate(airplane_list):
            if airplane_str.startswith(f"{current_airplane_id}:"):
                self.airplane_combo.current(i)
                current_found = True
                break

        if not current_found and airplane_list:
            self.airplane_combo.current(0)

        airports = self.db.get_all_airports()
        airport_list = [f"{a.id}: {a.start_airport} → {a.finish_airport}" for a in airports]
        self.airport_combo['values'] = airport_list

        current_airport_id = self.flight_data.get('id_airport')
        current_found = False
        for i, airport_str in enumerate(airport_list):
            if airport_str.startswith(f"{current_airport_id}:"):
                self.airport_combo.current(i)
                current_found = True
                break

        if not current_found and airport_list:
            self.airport_combo.current(0)

    def save(self):
        try:
            number_flight = self.number_flight_var.get().strip()
            time_flight = self.time_flight_var.get().strip()

            if not number_flight:
                messagebox.showwarning("Ошибка", "Введите номер рейса")
                return

            if not time_flight:
                messagebox.showwarning("Ошибка", "Введите время вылета")
                return

            airplane_text = self.airplane_combo.get()
            airport_text = self.airport_combo.get()
            if not airplane_text:
                messagebox.showwarning("Ошибка", "Выберите самолет")
                return
            if not airport_text:
                messagebox.showwarning("Ошибка", "Выберите маршрут")
                return

            id_airplane = int(airplane_text.split(':')[0])
            id_airport = int(airport_text.split(':')[0])

            from datetime import datetime
            try:
                datetime.strptime(time_flight, '%H:%M')
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат времени ЧЧ:ММ")
                return

            success = self.db.update_flight(
                flight_id=self.flight_id,
                id_airplane=id_airplane,
                id_airport=id_airport,
                number_flight=int(number_flight),
                time_flight=time_flight
            )

            if success:
                messagebox.showinfo("Успех", f"Рейс #{self.flight_id} успешно обновлен")
                if self.callback:
                    self.callback()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить рейс")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")

