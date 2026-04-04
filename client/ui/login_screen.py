"""Экран входа."""

import tkinter as tk
from ui.theme import COLORS, get_font
from ui.components import ModernEntry, ModernButton


class LoginScreen(tk.Frame):
    """Экран авторизации."""

    def __init__(self, parent, on_login=None, on_switch_to_register=None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.on_login = on_login
        self.on_switch_to_register = on_switch_to_register
        self._build_ui()

    def _build_ui(self):
        # Центральная карточка
        center = tk.Frame(self, bg=COLORS['bg_primary'])
        center.place(relx=0.5, rely=0.5, anchor='center')

        card = tk.Frame(center, bg=COLORS['bg_secondary'],
                        highlightbackground=COLORS['border'],
                        highlightthickness=1)
        card.pack(padx=40, pady=40)

        inner = tk.Frame(card, bg=COLORS['bg_secondary'])
        inner.pack(padx=48, pady=48)

        # Логотип / Название
        tk.Label(inner, text="Ёлка", bg=COLORS['bg_secondary'],
                 fg=COLORS['accent'], font=get_font('title', bold=True)).pack(pady=(0, 4))
        tk.Label(inner, text="Карьерный AI Ассистент",
                 bg=COLORS['bg_secondary'], fg=COLORS['text_secondary'],
                 font=get_font('sm')).pack(pady=(0, 32))

        # Заголовок
        tk.Label(inner, text="Вход в аккаунт", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_primary'], font=get_font('xl', bold=True)).pack(
            pady=(0, 24))

        # Поля
        tk.Label(inner, text="Логин / Почта", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_secondary'], font=get_font('sm'),
                 anchor='w').pack(fill='x', pady=(0, 4))
        self.login_entry = ModernEntry(inner, placeholder="Введите логин")
        self.login_entry.pack(fill='x', pady=(0, 16))

        tk.Label(inner, text="Пароль", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_secondary'], font=get_font('sm'),
                 anchor='w').pack(fill='x', pady=(0, 4))
        self.password_entry = ModernEntry(inner, placeholder="Введите пароль",
                                          show="*")
        self.password_entry.pack(fill='x', pady=(0, 24))

        # Ошибка
        self.error_label = tk.Label(inner, text="", bg=COLORS['bg_secondary'],
                                    fg=COLORS['error'], font=get_font('sm'))
        self.error_label.pack(fill='x', pady=(0, 8))

        # Кнопка входа
        ModernButton(inner, text="Войти", command=self._do_login,
                     full_width=True).pack(fill='x', pady=(0, 16))

        # Ссылка на регистрацию
        link_frame = tk.Frame(inner, bg=COLORS['bg_secondary'])
        link_frame.pack()
        tk.Label(link_frame, text="Нет аккаунта? ",
                 bg=COLORS['bg_secondary'], fg=COLORS['text_secondary'],
                 font=get_font('sm')).pack(side='left')
        reg_link = tk.Label(link_frame, text="Зарегистрироваться",
                            bg=COLORS['bg_secondary'], fg=COLORS['accent'],
                            font=get_font('sm', bold=True), cursor='hand2')
        reg_link.pack(side='left')
        reg_link.bind('<Button-1>', lambda e: self.on_switch_to_register()
                      if self.on_switch_to_register else None)
        reg_link.bind('<Enter>', lambda e: reg_link.configure(
            fg=COLORS['accent_hover']))
        reg_link.bind('<Leave>', lambda e: reg_link.configure(
            fg=COLORS['accent']))

    def _do_login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        if not login or not password:
            self.error_label.configure(text="Заполните все поля")
            return
        self.error_label.configure(text="")
        if self.on_login:
            self.on_login(login, password)

    def show_error(self, text):
        self.error_label.configure(text=text)
