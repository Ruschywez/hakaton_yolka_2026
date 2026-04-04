"""Главный контроллер приложения — навигация между экранами."""

import tkinter as tk
from ui.theme import COLORS, apply_theme, get_font, SIDEBAR_WIDTH
from ui.login_screen import LoginScreen
from ui.register_screen import RegisterScreen
from ui.chat_screen import ChatScreen
from ui.profile_screen import ProfileScreen
from ui.edit_profile_screen import EditProfileScreen
from ui.components import SidebarButton
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
        self.current_nav = 'chat'
        self.chat_screen = None

        # Контейнер для экранов (логин/регистрация используют полный экран)
        self.container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        self.container.pack(fill='both', expand=True)

        # Фрейм с сайдбаром + контентом (для авторизованных экранов)
        self.main_layout = None
        self.sidebar = None
        self.content_area = None
        self.nav_buttons = {}

        # Старт с экрана входа
        self._show_login()

    def _clear_screen(self):
        """Удалить текущий экран."""
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

    def _destroy_main_layout(self):
        """Удалить layout с сайдбаром."""
        if self.main_layout:
            self.main_layout.destroy()
            self.main_layout = None
            self.sidebar = None
            self.content_area = None
            self.nav_buttons = {}

    def _build_sidebar_layout(self):
        """Создать постоянный layout: сайдбар + область контента."""
        if self.main_layout:
            return  # Уже создан

        self.main_layout = tk.Frame(self.container, bg=COLORS['bg_primary'])
        self.main_layout.pack(fill='both', expand=True)

        # === SIDEBAR ===
        self.sidebar = tk.Frame(self.main_layout, bg=COLORS['bg_sidebar'],
                                width=SIDEBAR_WIDTH)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Лого
        logo_frame = tk.Frame(self.sidebar, bg=COLORS['bg_sidebar'])
        logo_frame.pack(fill='x', padx=16, pady=(20, 8))
        tk.Label(logo_frame, text="Ёлка", bg=COLORS['bg_sidebar'],
                 fg=COLORS['accent'], font=get_font('xl', bold=True)).pack(
            anchor='w')
        tk.Label(logo_frame, text="AI Карьера", bg=COLORS['bg_sidebar'],
                 fg=COLORS['text_muted'], font=get_font('xs')).pack(anchor='w')

        # Разделитель
        tk.Frame(self.sidebar, bg=COLORS['divider'], height=1).pack(
            fill='x', padx=16, pady=12)

        # Инфо пользователя
        user_frame = tk.Frame(self.sidebar, bg=COLORS['bg_sidebar'])
        user_frame.pack(fill='x', padx=16, pady=(0, 12))
        name = self.user_data.get('first_name', 'Пользователь')
        tk.Label(user_frame, text=f"Привет, {name}!",
                 bg=COLORS['bg_sidebar'], fg=COLORS['text_primary'],
                 font=get_font('md', bold=True), anchor='w').pack(fill='x')

        # Разделитель
        tk.Frame(self.sidebar, bg=COLORS['divider'], height=1).pack(
            fill='x', padx=16, pady=(0, 12))

        # Навигация
        self.nav_buttons = {}
        nav_items = [
            ('chat', 'Чат', chr(9776)),
            ('profile', 'Профиль', chr(9679)),
            ('edit', 'Изменить данные', chr(9998)),
        ]
        for key, text, icon in nav_items:
            active = (key == self.current_nav)
            btn = SidebarButton(self.sidebar, text=text, icon=icon,
                                command=lambda k=key: self._handle_navigation(k),
                                active=active)
            btn.pack(fill='x')
            self.nav_buttons[key] = btn

        # Спейсер
        tk.Frame(self.sidebar, bg=COLORS['bg_sidebar']).pack(
            fill='both', expand=True)

        # Кнопка выхода
        logout_btn = SidebarButton(self.sidebar, text="Выйти", icon=chr(8592),
                                   command=self._handle_logout)
        logout_btn.pack(fill='x', pady=(0, 16))

        # === ОБЛАСТЬ КОНТЕНТА ===
        self.content_area = tk.Frame(self.main_layout, bg=COLORS['bg_primary'])
        self.content_area.pack(side='left', fill='both', expand=True)

    def _set_active_nav(self, key):
        """Подсветить активную вкладку в сайдбаре."""
        self.current_nav = key
        for k, btn in self.nav_buttons.items():
            btn.set_active(k == key)

    def _clear_content(self):
        """Очистить область контента (справа от сайдбара)."""
        if self.content_area:
            for widget in self.content_area.winfo_children():
                widget.destroy()

    def _show_login(self):
        """Показать экран входа."""
        self._destroy_main_layout()
        self._clear_screen()
        self.chat_screen = None
        screen = LoginScreen(self.container,
                             on_login=self._handle_login,
                             on_switch_to_register=self._show_register)
        screen.pack(fill='both', expand=True)
        self.current_screen = screen

    def _show_register(self):
        """Показать экран регистрации."""
        self._destroy_main_layout()
        self._clear_screen()
        screen = RegisterScreen(self.container,
                                on_register=self._handle_register,
                                on_switch_to_login=self._show_login)
        screen.pack(fill='both', expand=True)
        self.current_screen = screen

    def _show_chat(self):
        """Показать экран чата."""
        self._clear_screen()  # убрать экран логина/регистрации, если есть
        self._build_sidebar_layout()
        self._clear_content()
        self._set_active_nav('chat')

        chat = ChatScreen(self.content_area,
                          user_data=self.user_data,
                          on_navigate=self._handle_navigation,
                          on_logout=self._handle_logout,
                          show_sidebar=False)
        chat.pack(fill='both', expand=True)
        self.chat_screen = chat

    def _show_profile(self):
        """Показать профиль."""
        self._clear_screen()
        self._build_sidebar_layout()
        self._clear_content()
        self._set_active_nav('profile')
        self.chat_screen = None

        profile = ProfileScreen(self.content_area, user_data=self.user_data,
                                on_back=self._show_chat,
                                on_edit=self._show_edit_profile)
        profile.pack(fill='both', expand=True)

    def _show_edit_profile(self):
        """Показать экран редактирования профиля."""
        self._clear_screen()
        self._build_sidebar_layout()
        self._clear_content()
        self._set_active_nav('edit')
        self.chat_screen = None

        edit = EditProfileScreen(self.content_area, user_data=self.user_data,
                                 on_back=self._show_chat,
                                 on_save=self._handle_profile_save)
        edit.pack(fill='both', expand=True)

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
        self.current_nav = 'chat'
        self._destroy_main_layout()
        self._show_login()

    def _handle_profile_save(self, updated_data):
        """Обновление данных после сохранения профиля."""
        self.user_data = updated_data
