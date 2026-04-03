"""Экран регистрации."""

import tkinter as tk
from ui.theme import COLORS, get_font
from ui.components import ModernEntry, ModernButton, ScrollableFrame


class RegisterScreen(tk.Frame):
    """Экран регистрации нового пользователя."""

    def __init__(self, parent, on_register=None, on_switch_to_login=None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.on_register = on_register
        self.on_switch_to_login = on_switch_to_login
        self._build_ui()

    def _build_ui(self):
        # Центральная карточка
        center = tk.Frame(self, bg=COLORS['bg_primary'])
        center.place(relx=0.5, rely=0.5, anchor='center')

        card = tk.Frame(center, bg=COLORS['bg_secondary'],
                        highlightbackground=COLORS['border'],
                        highlightthickness=1)
        card.pack(padx=40, pady=20)

        inner = tk.Frame(card, bg=COLORS['bg_secondary'])
        inner.pack(padx=48, pady=32)

        # Заголовок
        tk.Label(inner, text="Ёлка", bg=COLORS['bg_secondary'],
                 fg=COLORS['accent'], font=get_font('title', bold=True)).pack(
            pady=(0, 4))
        tk.Label(inner, text="Создание аккаунта", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_primary'], font=get_font('lg', bold=True)).pack(
            pady=(0, 20))

        # Две колонки
        columns = tk.Frame(inner, bg=COLORS['bg_secondary'])
        columns.pack(fill='x')

        left = tk.Frame(columns, bg=COLORS['bg_secondary'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 12))

        right = tk.Frame(columns, bg=COLORS['bg_secondary'])
        right.pack(side='left', fill='both', expand=True, padx=(12, 0))

        # Левая колонка
        fields_left = [
            ("Логин *", "Введите логин", None),
            ("Пароль *", "Введите пароль", "*"),
            ("Фамилия *", "Иванов", None),
            ("Имя *", "Иван", None),
        ]
        self.entries = {}
        for label_text, placeholder, show in fields_left:
            key = label_text.replace(" *", "").lower()
            tk.Label(left, text=label_text, bg=COLORS['bg_secondary'],
                     fg=COLORS['text_secondary'], font=get_font('sm'),
                     anchor='w').pack(fill='x', pady=(0, 2))
            entry = ModernEntry(left, placeholder=placeholder, show=show)
            entry.pack(fill='x', pady=(0, 10))
            self.entries[key] = entry

        # Правая колонка
        fields_right = [
            ("Отчество", "Иванович", None),
            ("Дата рождения *", "ГГГГ-ММ-ДД", None),
        ]
        for label_text, placeholder, show in fields_right:
            key = label_text.replace(" *", "").lower()
            tk.Label(right, text=label_text, bg=COLORS['bg_secondary'],
                     fg=COLORS['text_secondary'], font=get_font('sm'),
                     anchor='w').pack(fill='x', pady=(0, 2))
            entry = ModernEntry(right, placeholder=placeholder, show=show)
            entry.pack(fill='x', pady=(0, 10))
            self.entries[key] = entry

        # Ошибка
        self.error_label = tk.Label(inner, text="", bg=COLORS['bg_secondary'],
                                    fg=COLORS['error'], font=get_font('sm'))
        self.error_label.pack(fill='x', pady=(10, 4))

        # Кнопка
        ModernButton(inner, text="Зарегистрироваться",
                     command=self._do_register, full_width=True).pack(
            fill='x', pady=(4, 12))

        # Ссылка
        link_frame = tk.Frame(inner, bg=COLORS['bg_secondary'])
        link_frame.pack()
        tk.Label(link_frame, text="Уже есть аккаунт? ",
                 bg=COLORS['bg_secondary'], fg=COLORS['text_secondary'],
                 font=get_font('sm')).pack(side='left')
        login_link = tk.Label(link_frame, text="Войти",
                              bg=COLORS['bg_secondary'], fg=COLORS['accent'],
                              font=get_font('sm', bold=True), cursor='hand2')
        login_link.pack(side='left')
        login_link.bind('<Button-1>', lambda e: self.on_switch_to_login()
                        if self.on_switch_to_login else None)
        login_link.bind('<Enter>', lambda e: login_link.configure(
            fg=COLORS['accent_hover']))
        login_link.bind('<Leave>', lambda e: login_link.configure(
            fg=COLORS['accent']))

    def _do_register(self):
        login = self.entries.get('логин', self.entries.get('логин'))
        password = self.entries.get('пароль', self.entries.get('пароль'))
        last_name = self.entries.get('фамилия', self.entries.get('фамилия'))
        first_name = self.entries.get('имя', self.entries.get('имя'))

        # Получаем значения
        vals = {k: e.get() for k, e in self.entries.items()}

        if not vals.get('логин') or not vals.get('пароль') or \
           not vals.get('фамилия') or not vals.get('имя'):
            self.error_label.configure(
                text="Заполните обязательные поля (отмечены *)")
            return

        self.error_label.configure(text="")
        if self.on_register:
            self.on_register(vals)

    def show_error(self, text):
        self.error_label.configure(text=text)
