import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import csv
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GUI.console_sql import SQLConsoleDialog
from database import Database
from GUI.dialogs import (AddFlightDialog, AddPassengerDialog, CreateBookingDialog, EditCompanyDialog, ManageUsersDialog,
                         AddAirplaneDialog, AddAirportDialog, EditFlightDialog)
from GUI.widgets import StatusBar, ConfirmationDialog


class MainWindow:
    def __init__(self, root, db_params, current_user=None):
        self.root = root
        self.root.title("Система бронирования авиабилетов")
        self.root.geometry("1200x700")

        self.current_user = current_user if current_user else {'nickname': 'Гость', 'admin': False}

        self.db = Database(db_params)
        if not self.db.connect():
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
            root.destroy()
            return

        self.db.current_user = self.current_user

        self.create_widgets()
        self.load_initial_data()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('aqua')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        self.flights_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.flights_frame, text="Рейсы")
        self.create_flights_tab()

        self.passengers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.passengers_frame, text="Пассажиры")
        self.create_passengers_tab()

        self.bookings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bookings_frame, text="Бронирования")
        self.create_bookings_tab()

        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Поиск")
        self.create_search_tab()

        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Отчеты")
        self.create_reports_tab()

        if hasattr(self, 'current_user') and self.current_user.get('senior'):
            self.management_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.management_frame, text="Управление")
            self.create_management_tab()

        if hasattr(self, 'current_user') and self.current_user.get('admin'):
            self.console_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.console_frame, text="Консоль")
            self.create_console_tab()

        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.set_db_status(True)

    def create_flights_tab(self):
        control_frame = ttk.Frame(self.flights_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(control_frame, text="Обновить", command=self.load_flights).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Добавить рейс", command=lambda: AddFlightDialog(self.root, self.db, self.load_flights)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Редактировать рейс", command=self.edit_flight).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить рейс", command=self.delete_flight).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Карта мест", command=self.show_seat_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Отменить все брони", command=self.cancel_all_bookings_for_flight).pack(side=tk.LEFT, padx=5)

        columns = ("ID", "Номер рейса", "Самолет", "Аэропорт", "Время вылета", "Авиакомпания")
        self.flights_tree = ttk.Treeview(self.flights_frame, columns=columns, show="headings", height=20)
        for col in columns:
            self.flights_tree.heading(col, text=col)
            self.flights_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.flights_frame, orient=tk.VERTICAL, command=self.flights_tree.yview)
        self.flights_tree.configure(yscrollcommand=scrollbar.set)

        self.flights_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

    def create_passengers_tab(self):
        control_frame = ttk.Frame(self.passengers_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Обновить", command=self.load_passengers).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Добавить пассажира", command=lambda: AddPassengerDialog(self.root, self.db, self.load_passengers)).pack(side=tk.LEFT,
                                                                                                      padx=5)
        ttk.Button(control_frame, text="Удалить пассажира", command=self.delete_passenger).pack(side=tk.LEFT, padx=5)

        columns = ("ID", "Имя", "Фамилия", "Телефон", "Паспорт")
        self.passengers_tree = ttk.Treeview(self.passengers_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.passengers_tree.heading(col, text=col)
            self.passengers_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.passengers_frame, orient=tk.VERTICAL, command=self.passengers_tree.yview)
        self.passengers_tree.configure(yscrollcommand=scrollbar.set)

        self.passengers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

    def create_bookings_tab(self):
        control_frame = ttk.Frame(self.bookings_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Обновить", command=self.load_bookings).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Создать бронь", command=lambda: CreateBookingDialog(self.root, self.db, self.load_bookings)).pack(side=tk.LEFT,
                                                                                                     padx=5)
        ttk.Button(control_frame, text="Отменить бронь", command=self.cancel_booking).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Подтвердить бронь", command=self.confirm_booking).pack(side=tk.LEFT, padx=5)

        columns = ("ID", "Рейс", "Пассажир", "Место", "Время брони", "Статус")
        self.bookings_tree = ttk.Treeview(self.bookings_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.bookings_frame, orient=tk.VERTICAL, command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)

        self.bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

    def create_search_tab(self):
        search_frame = ttk.Frame(self.search_frame)
        search_frame.pack(fill=tk.X, padx=20, pady=20)

        ttk.Label(search_frame, text="Поиск рейсов:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky=tk.W, pady=10)
        ttk.Label(search_frame, text="Аэропорт отправления:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_airport_entry = ttk.Entry(search_frame, width=20)
        self.start_airport_entry.grid(row=1, column=1, pady=5)

        ttk.Label(search_frame, text="Аэропорт прибытия:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.finish_airport_entry = ttk.Entry(search_frame, width=20)
        self.finish_airport_entry.grid(row=2, column=1, pady=5)

        ttk.Button(search_frame, text="Найти рейсы", command=self.search_flights).grid(row=3, column=0, columnspan=2, pady=10)
        search_results_frame = ttk.LabelFrame(self.search_frame, text="Результаты поиска")
        search_results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("ID", "Номер рейса", "Отправление", "Прибытие", "Время", "Авиакомпания")
        self.search_tree = ttk.Treeview(search_results_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(search_results_frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)

        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

    def create_reports_tab(self):
        reports_frame = ttk.Frame(self.reports_frame)
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(reports_frame, text="Система отчетности",
                  font=("Arial", 16, "bold")).pack(pady=10)

        reports_buttons = ttk.Frame(reports_frame)
        reports_buttons.pack(pady=20)

        ttk.Button(reports_buttons, text="📊 Рейсы по авиакомпаниям",
                   command=self.show_company_flights_report,
                   width=25).pack(side=tk.LEFT, padx=10, pady=5)

        ttk.Button(reports_buttons, text="👥 Статистика пассажиров",
                   command=self.show_passenger_stats_report,
                   width=25).pack(side=tk.LEFT, padx=10, pady=5)

        ttk.Button(reports_buttons, text="💺 Занятость мест",
                   command=self.show_seat_occupancy_report,
                   width=25).pack(side=tk.LEFT, padx=10, pady=5)

        self.report_container = ttk.Frame(reports_frame)
        self.report_container.pack(fill=tk.BOTH, expand=True, pady=10)

        self.show_empty_report()

    def show_empty_report(self):
        for widget in self.report_container.winfo_children():
            widget.destroy()

        empty_label = ttk.Label(self.report_container, text="Выберите отчет из кнопок выше", font=("Arial", 14))
        empty_label.pack(expand=True)

    def show_company_flights_report(self):
        try:
            for widget in self.report_container.winfo_children():
                widget.destroy()
            ttk.Label(self.report_container, text="📊 Отчет: Количество рейсов по авиакомпаниям", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)

            data = self.db.get_report_company_flights()
            if not data:
                ttk.Label(self.report_container, text="Нет данных для отображения",
                          font=("Arial", 12)).pack(pady=20)
                return
            columns = ["Авиакомпания", "Количество рейсов", "Количество самолетов"]
            ttk.Label(self.report_container, text=f"Найдено записей: {len(data)}", font=("Arial", 14)).pack(anchor=tk.W, pady=5)

            self.create_report_tree(columns, data)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить отчет: {str(e)}")

    def show_passenger_stats_report(self):
        try:
            for widget in self.report_container.winfo_children():
                widget.destroy()
            ttk.Label(self.report_container, text="👥 Отчет: Статистика по пассажирам(Выборка 20)", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)
            data = self.db.get_report_passenger_stats(limit=20)
            if not data:
                ttk.Label(self.report_container, text="Нет данных для отображения", font=("Arial", 14)).pack(pady=20)
                return

            columns = ["Пассажир", "Паспорт", "Всего бронирований"]
            ttk.Label(self.report_container, text=f"Найдено записей: {len(data)}", font=("Arial", 14)).pack(anchor=tk.W, pady=5)

            self.create_report_tree(columns, data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить отчет: {str(e)}")

    def show_seat_occupancy_report(self):
        try:
            for widget in self.report_container.winfo_children():
                widget.destroy()

            ttk.Label(self.report_container, text="💺 Отчет: Бронирования по рейсам",font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=10)

            data = self.db.get_report_seat_occupancy()
            if not data:
                ttk.Label(self.report_container, text="Нет данных для отображения",font=("Arial", 14)).pack(pady=20)
                return
            columns = ["Номер рейса", "Маршрут", "Количество броней"]
            ttk.Label(self.report_container, text=f"Найдено записей: {len(data)}", font=("Arial", 14)).pack(anchor=tk.W, pady=5)
            self.create_report_tree(columns, data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить отчет: {str(e)}")
    def create_report_tree(self, columns, data):
        tree_frame = ttk.Frame(self.report_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        for row in data:
            values = [row.get(col, "") for col in columns]
            tree.insert("", tk.END, values=values)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = ttk.Frame(self.report_container)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Экспорт в CSV", command=lambda: self.export_report_to_csv(columns, data)).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Очистить отчет", command=self.show_empty_report).pack(side=tk.LEFT, padx=5)

    def export_report_to_csv(self, columns, data):
        try:
            filename = f"отчет_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(columns)
                for row in data:
                    writer.writerow([row.get(col, "") for col in columns])
            messagebox.showinfo("Успех", f"Отчет сохранен в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")

    def create_management_tab(self):
        management_frame = ttk.Frame(self.management_frame)
        management_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        ttk.Button(management_frame, text="Управление авиакомпаниями", command=lambda: EditCompanyDialog(self.root, self.db, self.load_flights), width=30).pack(pady=10)
        ttk.Button(management_frame, text="Добавить самолет", command=self.add_airplane_dialog, width=30).pack(pady=10)
        ttk.Button(management_frame, text="Добавить маршрут", command=self.add_airport_dialog, width=30).pack(pady=10)
        if hasattr(self, 'current_user') and self.current_user.get('admin'):
            ttk.Button(management_frame, text="Управление пользователями", command=self.manage_users_dialog, width=30).pack(pady=10)
        info_frame = ttk.LabelFrame(management_frame, text="Информация о системе")
        info_frame.pack(fill=tk.X, pady=20)
        info_text = """Система бронирования авиабилетов

    Функционал:
    - Управление рейсами, пассажирами, бронированиями
    - Поиск рейсов по маршрутам
    - Отчеты и аналитика
    - Управление справочниками (авиакомпании, самолеты, маршруты)
    - Управление пользователями"""
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=10, pady=10)

    def manage_users_dialog(self):
        if not hasattr(self, 'current_user') or not self.current_user.get('admin'):
            messagebox.showerror("Ошибка", "Доступ запрещен.")
            return

        ManageUsersDialog(self, self.db, self.load_users_list)

    def load_users_list(self):
        pass

    def load_initial_data(self):
        self.load_flights()
        self.load_passengers()
        self.load_bookings()

    def load_flights(self):
        flights = self.db.get_all_flights()
        for item in self.flights_tree.get_children():
            self.flights_tree.delete(item)
        for flight in flights:
            self.flights_tree.insert("", tk.END, values=(
                flight['id'], flight['number_flight'], flight['name_airplane'],
                flight['airport'], flight['time_flight'], flight['name_company']
            ))

    def load_passengers(self):
        passengers = self.db.get_all_passengers()
        for item in self.passengers_tree.get_children():
            self.passengers_tree.delete(item)
        for passenger in passengers:
            self.passengers_tree.insert("", tk.END, values=(
                passenger.id, passenger.first_name, passenger.second_name,
                passenger.number_phone, passenger.number_passport
            ))

    def load_bookings(self):
        bookings = self.db.get_all_bookings()
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        for booking in bookings:
            status = "Подтверждено" if booking['status'] else "Отменено"
            self.bookings_tree.insert("", tk.END, values=(
                booking['id'], booking['number_flight'], booking['passenger'],
                booking['seat'], booking['booking_time'], status
            ))

    def search_flights(self):
        start = self.start_airport_entry.get().strip().upper()
        finish = self.finish_airport_entry.get().strip().upper()
        flights = self.db.search_flights(start, finish)
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        for flight in flights:
            self.search_tree.insert("", tk.END, values=(
                flight['id'], flight['number_flight'], flight['start_airport'],
                flight['finish_airport'], flight['time_flight'], flight['name_company']
            ))
        if not flights:
            messagebox.showinfo("Результат", "Рейсы не найдены")

    def delete_flight(self):
        selection = self.flights_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите рейс для удаления")
            return
        flight_id = self.flights_tree.item(selection[0])['values'][0]
        flight_info = f"Рейс #{self.flights_tree.item(selection[0])['values'][1]}"
        if ConfirmationDialog.askyesno(self.root, "Подтверждение", f"Удалить {flight_info}?"):
            self.status_bar.set_status(f"Удаление рейса #{flight_id}...")
            if self.db.delete_flight(flight_id):
                messagebox.showinfo("Успех", "Рейс удален")
                self.load_flights()
                self.status_bar.set_status("Готов")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить рейс")
                self.status_bar.set_status("Ошибка удаления")

    def delete_passenger(self):
        selection = self.passengers_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите пассажира для удаления")
            return
        passenger_id = self.passengers_tree.item(selection[0])['values'][0]
        passenger_name = f"{self.passengers_tree.item(selection[0])['values'][1]} {self.passengers_tree.item(selection[0])['values'][2]}"

        if ConfirmationDialog.askyesno(self.root, "Подтверждение", f"Удалить пассажира {passenger_name}?"):
            if self.db.delete_passenger(passenger_id):
                messagebox.showinfo("Успех", "Пассажир удален")
                self.load_passengers()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пассажира")

    def cancel_booking(self):
        selection = self.bookings_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите бронирование")
            return

        booking_id = self.bookings_tree.item(selection[0])['values'][0]
        passenger_name = self.bookings_tree.item(selection[0])['values'][2]
        flight_number = self.bookings_tree.item(selection[0])['values'][1]
        if ConfirmationDialog.askyesno(
                self.root,
                "Отмена бронирования",
                f"Отменить бронирование #{booking_id}?\n"
                f"Пассажир: {passenger_name}\n"
                f"Рейс: #{flight_number}"
        ):
            if self.db.cancel_booking_by_id(booking_id):
                messagebox.showinfo("Успех", "Бронирование отменено")
                self.load_bookings()
            else:
                messagebox.showerror("Ошибка", "Не удалось отменить бронирование")

    def add_airplane_dialog(self):
        AddAirplaneDialog(self.root, self.db, self.refresh_airplanes)

    def add_airport_dialog(self):
        AddAirportDialog(self.root, self.db, self.refresh_airports)

    def refresh_airplanes(self):
        messagebox.showinfo("Успех", "Самолет добавлен успешно")
        self.load_flights()

    def refresh_airports(self):
        messagebox.showinfo("Успех", "Маршрут добавлен успешно")
        self.load_flights()

    def show_seat_map(self):
        selection = self.flights_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите рейс")
            return

        flight_id = self.flights_tree.item(selection[0])['values'][0]

        seat_map_dialog = tk.Toplevel(self.root)
        seat_map_dialog.title(f"Карта мест - Рейс #{self.flights_tree.item(selection[0])['values'][1]}")
        seat_map_dialog.geometry("700x500")

        stats = self.db.get_seat_statistics(flight_id)

        notebook = ttk.Notebook(seat_map_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        business_frame = ttk.Frame(notebook)
        notebook.add(business_frame, text=f"Бизнес-класс (BUS)")
        self.create_seat_map_frame(business_frame, flight_id, 'BUS')

        economy_frame = ttk.Frame(notebook)
        notebook.add(economy_frame, text=f"Эконом-класс (ECO)")
        self.create_seat_map_frame(economy_frame, flight_id, 'ECO')

        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Статистика")

        stats_text_frame = ttk.Frame(stats_frame)
        stats_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(stats_text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text = tk.Text(stats_text_frame, height=15, width=60, yscrollcommand=scrollbar.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text.yview)

        business_stats = stats.get('BUS', {'total': 12, 'booked': 0, 'available': 12, 'percentage': 0})
        economy_stats = stats.get('ECO', {'total': 40, 'booked': 0, 'available': 40, 'percentage': 0})

        stats_text = "СТАТИСТИКА ЗАНЯТОСТИ МЕСТ\n\n"

        stats_text += "БИЗНЕС-КЛАСС:\n"
        stats_text += f"    Всего мест: {business_stats['total']}\n"
        stats_text += f"    Занято: {business_stats['booked']}\n"
        stats_text += f"    Свободно: {business_stats['available']}\n"
        stats_text += f"    Заполненность: {business_stats['percentage']:.2f}%\n\n"

        stats_text += "ЭКОНОМ-КЛАСС:\n"
        stats_text += f"    Всего мест: {economy_stats['total']}\n"
        stats_text += f"    Занято: {economy_stats['booked']}\n"
        stats_text += f"    Свободно: {economy_stats['available']}\n"
        stats_text += f"    Заполненность: {economy_stats['percentage']:.2f}%\n\n"

        stats_text += "ОБЩАЯ СТАТИСТИКА:\n"
        total_all = business_stats['total'] + economy_stats['total']
        booked_all = business_stats['booked'] + economy_stats['booked']
        available_all = business_stats['available'] + economy_stats['available']
        percentage_all = round((booked_all / total_all) * 100, 2) if total_all > 0 else 0

        stats_text += f"    Всего мест: {total_all}\n"
        stats_text += f"    Занято: {booked_all}\n"
        stats_text += f"    Свободно: {available_all}\n"
        stats_text += f"    Общая заполненность: {percentage_all}%"

        text.insert(1.0, stats_text)
        text.config(state='disabled')

        ttk.Button(stats_frame, text="Обновить статистику",
                   command=lambda: self.update_seat_stats(text, flight_id)).pack(pady=10)

    def update_seat_stats(self, text_widget, flight_id):
        stats = self.db.get_seat_statistics(flight_id)

        business_stats = stats.get('BUS', {'total': 12, 'booked': 0, 'available': 12, 'percentage': 0})
        economy_stats = stats.get('ECO', {'total': 40, 'booked': 0, 'available': 40, 'percentage': 0})

        stats_text = f"СТАТИСТИКА ЗАНЯТОСТИ МЕСТ\n"

        stats_text += f"БИЗНЕС-КЛАСС:\n"
        stats_text += f"  Всего мест: {business_stats['total']}\n"
        stats_text += f"  Занято: {business_stats['booked']}\n"
        stats_text += f"  Свободно: {business_stats['available']}\n"
        stats_text += f"  Заполненность: {business_stats['percentage']}%\n\n"

        stats_text += f"ЭКОНОМ-КЛАСС:\n"
        stats_text += f"  Всего мест: {economy_stats['total']}\n"
        stats_text += f"  Занято: {economy_stats['booked']}\n"
        stats_text += f"  Свободно: {economy_stats['available']}\n"
        stats_text += f"  Заполненность: {economy_stats['percentage']}%\n\n"

        stats_text += f"ОБЩАЯ СТАТИСТИКА:\n"
        total_all = business_stats['total'] + economy_stats['total']
        booked_all = business_stats['booked'] + economy_stats['booked']
        available_all = business_stats['available'] + economy_stats['available']
        percentage_all = round((booked_all / total_all) * 100, 2) if total_all > 0 else 0

        stats_text += f"  Всего мест: {total_all}\n"
        stats_text += f"  Занято: {booked_all}\n"
        stats_text += f"  Свободно: {available_all}\n"
        stats_text += f"  Общая заполненность: {percentage_all}%"

        text_widget.config(state='normal')
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, stats_text)
        text_widget.config(state='disabled')


    def create_seat_map_frame(self, parent, flight_id, seat_class):
        seats = self.db.get_all_places_for_flight(flight_id)
        # Фильтруем места по нужному классу
        filtered_seats = [seat for seat in seats if seat.seat_class == seat_class]
        if not filtered_seats:
            ttk.Label(parent, text=f"Нет мест класса {seat_class}").pack(pady=20)
            return

        max_row = max(seat.row_number for seat in filtered_seats)
        letters = ['A', 'B', 'C', 'D']
        for col, letter in enumerate(letters):
            ttk.Label(parent, text=letter, width=3, anchor="center").grid(row=0, column=col + 1, padx=2, pady=2)
        for row in range(1, max_row + 1):
            ttk.Label(parent, text=f"Ряд {row}", width=8, anchor="w").grid(row=row, column=0, padx=5, pady=2)

            for col, letter in enumerate(letters):
                seat = next((s for s in filtered_seats if s.row_number == row and s.seat_letter == letter), None)

                if seat:
                    is_available = self.db.is_seat_available(seat.id, flight_id)

                    label = tk.Label(parent, text=seat.seat_letter, width=3, height=1, relief="ridge", borderwidth=1, font=("Arial", 10))
                    if is_available:
                        label.config(bg="green", fg="white", text=f"{row}{letter}")
                    else:
                        label.config(bg="red", fg="white", text="X")

                    label.grid(row=row, column=col + 1, padx=2, pady=2)
                else:
                    tk.Label(parent, text="", width=3, height=1, relief="ridge", borderwidth=1, bg="lightgray").grid(row=row, column=col + 1, padx=2, pady=2)

    def edit_flight(self):
        selection = self.flights_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите рейс для редактирования")
            return

        flight_id = self.flights_tree.item(selection[0])['values'][0]
        flights = self.db.get_all_flights()
        flight_data = None
        for flight in flights:
            if flight['id'] == flight_id:
                flight_data = {
                    'id': flight['id'],
                    'number_flight': flight['number_flight'],
                    'time_flight': flight['time_flight'],
                    'id_airplane': flight['id_airplane'],
                    'id_airport': flight['id_airport'],
                    'name_airplane': flight['name_airplane'],
                    'airport': flight['airport']
                }
                break

        if not flight_data:
            messagebox.showerror("Ошибка", "Не удалось найти данные рейса")
            return

        EditFlightDialog(
            self.root,
            self.db,
            flight_id,
            flight_data,
            callback=self.load_flights
        )

    def cancel_all_bookings_for_flight(self):
        selection = self.flights_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите рейс")
            return

        flight_id = self.flights_tree.item(selection[0])['values'][0]
        flight_number = self.flights_tree.item(selection[0])['values'][1]

        if not ConfirmationDialog.askyesno(
                self.root,
                "Подтверждение",
                f"Отменить ВСЕ бронирования на рейсе #{flight_number}?\n\n"
        ):
            return

        try:
            if self.db.cancel_all_flight_bookings(flight_id):
                messagebox.showinfo("Успех",
                                    f"Все бронирования на рейсе #{flight_number} отменены")

                self.load_bookings()
                self.load_flights()
                self.status_bar.set_status(f"Отменены брони рейса #{flight_number}")
            else:
                messagebox.showerror("Ошибка", "Не удалось отменить бронирования")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")

    def confirm_booking(self):
        selection = self.bookings_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите бронирование")
            return

        booking_id = self.bookings_tree.item(selection[0])['values'][0]
        current_status = self.bookings_tree.item(selection[0])['values'][5]

        if current_status == "Подтверждено":
            messagebox.showinfo("Информация", "Бронирование уже активно")
            return

        result = messagebox.askyesno(
            "Подтверждение",
            "Подтвердить отмененное бронирование?"
        )

        if result:
            if self.db.confirm_cancelled_booking(booking_id):
                messagebox.showinfo("Успех", "Бронирование подтверждено")
                self.load_bookings()
            else:
                messagebox.showerror("Ошибка", "Не удалось подтвердить")

    def create_console_tab(self):
        console_frame = ttk.Frame(self.console_frame)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        ttk.Label(console_frame, text="SQL Консоль администратора", font=("Arial", 16, "bold")).pack(pady=10)

        info_text = """ Консоль позволяет выполнять любые SQL запросы напрямую к базе данных.

        • Вы можете выполнять SELECT, INSERT, UPDATE, DELETE, CREATE и другие запросы
        • Для выполнения запроса нажмите F5
         ВНИМАНИЕ! Неправильные запросы могут повредить базу данных."""

        ttk.Label(console_frame, text=info_text, justify=tk.LEFT, foreground="black", wraplength=800).pack(pady=10)

        ttk.Button(console_frame, text="Открыть SQL Консоль", command=self.open_sql_console, width=25).pack(pady=20)

    def open_sql_console(self):
        SQLConsoleDialog(self, self.db)

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.disconnect()