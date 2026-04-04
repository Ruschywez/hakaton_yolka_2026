"""Главный контроллер приложения — навигация между экранами."""

import tkinter as tk
from ui.theme import COLORS, apply_theme
from ui.login_screen import LoginScreen
from ui.register_screen import RegisterScreen
from ui.chat_screen import ChatScreen
from ui.profile_screen import ProfileScreen
from ui.edit_profile_screen import EditProfileScreen
from api import auth as auth_api
from config import APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT


class App:
    """Главное приложение с навигацией между экранами."""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Тёмная тема
        apply_theme(self.root)

        # Состояние
        self.user_data = None
        self.current_screen = None
        self.chat_screen = None

        # Контейнер для экранов
        self.container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        self.container.pack(fill='both', expand=True)

        # Старт с экрана входа
        self._show_login()

    def _clear_screen(self):
        """Удалить текущий экран."""
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

    def _show_login(self):
        """Показать экран входа."""
        self._clear_screen()
        self.chat_screen = None
        screen = LoginScreen(self.container,
                             on_login=self._handle_login,
                             on_switch_to_register=self._show_register)
        screen.pack(fill='both', expand=True)
        self.current_screen = screen

    def _show_register(self):
        """Показать экран регистрации."""
        self._clear_screen()
        screen = RegisterScreen(self.container,
                                on_register=self._handle_register,
                                on_switch_to_login=self._show_login)
        screen.pack(fill='both', expand=True)
        self.current_screen = screen

    def _show_chat(self):
        """Показать экран чата."""
        self._clear_screen()
        screen = ChatScreen(self.container,
                            user_data=self.user_data,
                            on_navigate=self._handle_navigation,
                            on_logout=self._handle_logout)
        screen.pack(fill='both', expand=True)
        self.current_screen = screen
        self.chat_screen = screen

    def _show_profile(self):
        """Показать профиль поверх чата."""
        self._clear_screen()

        # Создаём layout: sidebar + profile content
        wrapper = tk.Frame(self.container, bg=COLORS['bg_primary'])
        wrapper.pack(fill='both', expand=True)
        self.current_screen = wrapper

        # Пересоздаём чат для сайдбара
        chat = ChatScreen(wrapper, user_data=self.user_data,
                          on_navigate=self._handle_navigation,
                          on_logout=self._handle_logout)
        chat.pack(fill='both', expand=True)
        chat.set_active_nav('profile')
        self.chat_screen = chat

        # Оверлей профиля
        overlay = tk.Frame(wrapper, bg=COLORS['bg_primary'])
        overlay.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        # Полупрозрачный фон (имитация)
        sidebar_spacer = tk.Frame(overlay, bg=COLORS['bg_sidebar'],
                                  width=220)
        sidebar_spacer.pack(side='left', fill='y')
        sidebar_spacer.pack_propagate(False)

        profile = ProfileScreen(overlay, user_data=self.user_data,
                                on_back=self._show_chat,
                                on_edit=self._show_edit_profile)
        profile.pack(side='left', fill='both', expand=True)

    def _show_edit_profile(self):
        """Показать экран редактирования профиля."""
        self._clear_screen()

        wrapper = tk.Frame(self.container, bg=COLORS['bg_primary'])
        wrapper.pack(fill='both', expand=True)
        self.current_screen = wrapper

        chat = ChatScreen(wrapper, user_data=self.user_data,
                          on_navigate=self._handle_navigation,
                          on_logout=self._handle_logout)
        chat.pack(fill='both', expand=True)
        chat.set_active_nav('edit')
        self.chat_screen = chat

        overlay = tk.Frame(wrapper, bg=COLORS['bg_primary'])
        overlay.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        sidebar_spacer = tk.Frame(overlay, bg=COLORS['bg_sidebar'], width=220)
        sidebar_spacer.pack(side='left', fill='y')
        sidebar_spacer.pack_propagate(False)

        edit = EditProfileScreen(overlay, user_data=self.user_data,
                                 on_back=self._show_chat,
                                 on_save=self._handle_profile_save)
        edit.pack(side='left', fill='both', expand=True)

    def _handle_login(self, login, password):
        """Обработка входа."""
        try:
            result = auth_api.login(login, password)
            self.user_data = result
            self._show_chat()
        except Exception as e:
            if self.current_screen and hasattr(self.current_screen, 'show_error'):
                self.current_screen.show_error(f"Ошибка входа: {e}")

    def _handle_register(self, vals):
        """Обработка регистрации."""
        try:
            result = auth_api.register(
                vals.get('логин', ''), vals.get('пароль', ''),
                vals.get('фамилия', ''), vals.get('имя', ''),
                vals.get('отчество', ''), vals.get('дата рождения', '')
            )
            self.user_data = result
            self._show_chat()
        except Exception as e:
            if self.current_screen and hasattr(self.current_screen, 'show_error'):
                self.current_screen.show_error(f"Ошибка: {e}")

    def _handle_navigation(self, key):
        """Навигация из сайдбара."""
        if key == 'profile':
            self._show_profile()
        elif key == 'edit':
            self._show_edit_profile()
        elif key == 'chat':
            self._show_chat()

    def _handle_logout(self):
        """Выход из аккаунта."""
        self.user_data = None
        self.chat_screen = None
        self._show_login()

    def _handle_profile_save(self, updated_data):
        """Обновление данных после сохранения профиля."""
        self.user_data = updated_data
