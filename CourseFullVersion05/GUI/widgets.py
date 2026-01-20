import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class ValidatedEntry(ttk.Entry):

    def __init__(self, parent, validate_func: Optional[Callable] = None,
                 error_message: str = "Неверное значение", **kwargs):
        super().__init__(parent, **kwargs)
        self.validate_func = validate_func
        self.error_message = error_message
        self.valid = True

        self.bind('<FocusOut>', self.validate)
        self.bind('<Return>', self.validate)

    def validate(self, event=None) -> bool:
        if self.validate_func:
            try:
                value = self.get()
                self.valid = self.validate_func(value)
            except:
                self.valid = False
            if not self.valid:
                self.show_error()
            else:
                self.clear_error()
        return self.valid

    def show_error(self):
        self.config(foreground='red')
        tooltip = tk.Toplevel(self)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height()}")
        label = ttk.Label(tooltip, text=self.error_message, background="yellow", relief="solid", borderwidth=1)
        label.pack()
        self.after(2000, tooltip.destroy)

    def clear_error(self):
        self.config(foreground='black')

    def get_validated_value(self):
        if self.validate():
            return self.get()
        return None


class DateEntry(ttk.Entry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<KeyRelease>', self.format_date)

    def format_date(self, event):
        text = self.get().replace('.', '')
        if len(text) >= 2:
            text = text[:2] + '.' + text[2:]
        if len(text) >= 5:
            text = text[:5] + '.' + text[5:]
        if len(text) > 10:
            text = text[:10]

        cursor_pos = self.index(tk.INSERT)
        self.delete(0, tk.END)
        self.insert(0, text)
        self.icursor(min(cursor_pos, len(text)))

    def get_date(self):
        from datetime import datetime
        try:
            return datetime.strptime(self.get(), '%d.%m.%Y')
        except:
            return None


class TimeEntry(ttk.Entry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<KeyRelease>', self.format_time)

    def format_time(self, event):
        text = self.get().replace(':', '')
        if len(text) >= 2:
            text = text[:2] + ':' + text[2:]
        if len(text) > 5:
            text = text[:5]

        if len(text) >= 2:
            try:
                hours = int(text[:2])
                if hours < 0 or hours > 23:
                    self.config(foreground='red')
                    return
            except:
                self.config(foreground='red')
                return

        if len(text) >= 5:
            try:
                minutes = int(text[3:5])
                if minutes < 0 or minutes > 59:
                    self.config(foreground='red')
                    return
            except:
                self.config(foreground='red')
                return

        self.config(foreground='black')
        cursor_pos = self.index(tk.INSERT)
        self.delete(0, tk.END)
        self.insert(0, text)
        self.icursor(min(cursor_pos, len(text)))

    def get_time(self):
        if len(self.get()) == 5:
            return self.get()
        return None


class PhoneEntry(ttk.Entry):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<KeyRelease>', self.format_phone)

    def format_phone(self, event):
        text = self.get().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if text.startswith('+'):
            formatted = '+'
            text = text[1:]
        else:
            formatted = ''

        if len(text) > 0:
            formatted += text[0]
        if len(text) > 1:
            formatted += text[1:4] + ' '
        if len(text) > 4:
            formatted += text[4:7] + '-'
        if len(text) > 7:
            formatted += text[7:9] + '-'
        if len(text) > 9:
            formatted += text[9:11]

        cursor_pos = self.index(tk.INSERT)
        self.delete(0, tk.END)
        self.insert(0, formatted)
        self.icursor(min(cursor_pos, len(formatted)))


class AutoCompleteCombobox(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._values = []
        self.bind('<KeyRelease>', self._autocomplete)
    def set_values(self, values):
        self._values = values
        self['values'] = values
    def _autocomplete(self, event):
        if event.keysym in ('BackSpace', 'Return', 'Up', 'Down', 'Left', 'Right'):
            return
        current = self.get()
        if current:
            matches = [v for v in self._values if v.lower().startswith(current.lower())]
            if matches:
                self['values'] = matches
                self.event_generate('<Down>')
            else:
                self['values'] = []
        else:
            self['values'] = self._values


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def destroy(self):
        self.canvas.unbind_all("<MouseWheel>")
        super().destroy()

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class StatusBar(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.status_var = tk.StringVar(value="Готов")

        ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.db_status_var = tk.StringVar(value="БД: Не подключено")
        ttk.Label(self, textvariable=self.db_status_var, relief=tk.SUNKEN, anchor=tk.E, width=20).pack(side=tk.RIGHT)

    def set_status(self, text: str):
        self.status_var.set(text)

    def set_db_status(self, connected: bool):
        if connected:
            self.db_status_var.set("БД: Подключено")
        else:
            self.db_status_var.set("БД: Отключено")


class ConfirmationDialog:
    def __init__(self, parent, title: str, message: str):
        self.result = False
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        ttk.Label(self.dialog, text=message, wraplength=350, justify=tk.CENTER, padding=20).pack()
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Да", command=self.on_yes, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Нет", command=self.on_no, width=10).pack(side=tk.RIGHT, padx=10)

        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
        self.dialog.wait_window()

    def on_yes(self):
        self.result = True
        self.dialog.destroy()

    def on_no(self):
        self.result = False
        self.dialog.destroy()

    @staticmethod
    def askyesno(parent, title: str, message: str) -> bool:
        dialog = ConfirmationDialog(parent, title, message)
        return dialog.result


class ProgressDialog:
    def __init__(self, parent, title: str, maximum: int = 100):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x100")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.dialog, variable=self.progress_var, maximum=maximum, mode='determinate')
        self.progress_bar.pack(pady=20, padx=20, fill=tk.X)
        self.status_var = tk.StringVar(value="Выполняется...")
        ttk.Label(self.dialog, textvariable=self.status_var).pack()
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    def update(self, value: int, status: str = None):
        self.progress_var.set(value)
        if status:
            self.status_var.set(status)
        self.dialog.update()

    def close(self):
        self.dialog.destroy()