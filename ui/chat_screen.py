"""Основной экран чата."""

import tkinter as tk
import threading
from ui.theme import COLORS, get_font, SIDEBAR_WIDTH
from ui.components import (SidebarButton, ScrollableFrame, ChatBubble,
                            TypingIndicator, ModernEntry)
from config import ASSISTANT_NAME, ASSISTANT_DESCRIPTION
from api import messages as msg_api


class ChatScreen(tk.Frame):
    """Экран чата с боковой панелью."""

    def __init__(self, parent, user_data=None,
                 on_navigate=None, on_logout=None, show_sidebar=True):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.user_data = user_data or {}
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.is_sending = False
        self.show_sidebar = show_sidebar
        self.nav_buttons = {}
        self._build_ui()
        self._load_messages()

    def _build_ui(self):
        if self.show_sidebar:
            # === SIDEBAR ===
            sidebar = tk.Frame(self, bg=COLORS['bg_sidebar'], width=SIDEBAR_WIDTH)
            sidebar.pack(side='left', fill='y')
            sidebar.pack_propagate(False)

            # Лого в сайдбаре
            logo_frame = tk.Frame(sidebar, bg=COLORS['bg_sidebar'])
            logo_frame.pack(fill='x', padx=16, pady=(20, 8))
            tk.Label(logo_frame, text="Ёлка", bg=COLORS['bg_sidebar'],
                     fg=COLORS['accent'], font=get_font('xl', bold=True)).pack(
                anchor='w')
            tk.Label(logo_frame, text="AI Карьера", bg=COLORS['bg_sidebar'],
                     fg=COLORS['text_muted'], font=get_font('xs')).pack(anchor='w')

            # Разделитель
            tk.Frame(sidebar, bg=COLORS['divider'], height=1).pack(
                fill='x', padx=16, pady=12)

            # Инфо пользователя
            user_frame = tk.Frame(sidebar, bg=COLORS['bg_sidebar'])
            user_frame.pack(fill='x', padx=16, pady=(0, 12))
            name = self.user_data.get('first_name', 'Пользователь')
            tk.Label(user_frame, text=f"Привет, {name}!",
                     bg=COLORS['bg_sidebar'], fg=COLORS['text_primary'],
                     font=get_font('md', bold=True), anchor='w').pack(fill='x')

            # Разделитель
            tk.Frame(sidebar, bg=COLORS['divider'], height=1).pack(
                fill='x', padx=16, pady=(0, 12))

            # Навигация
            nav_items = [
                ('chat', 'Чат', chr(9776)),
                ('profile', 'Профиль', chr(9679)),
                ('edit', 'Изменить данные', chr(9998)),
            ]
            for key, text, icon in nav_items:
                active = (key == 'chat')
                btn = SidebarButton(sidebar, text=text, icon=icon,
                                    command=lambda k=key: self._navigate(k),
                                    active=active)
                btn.pack(fill='x')
                self.nav_buttons[key] = btn

            # Спейсер
            tk.Frame(sidebar, bg=COLORS['bg_sidebar']).pack(fill='both', expand=True)

            # Кнопка выхода
            logout_btn = SidebarButton(sidebar, text="Выйти", icon=chr(8592),
                                       command=self.on_logout)
            logout_btn.pack(fill='x', pady=(0, 16))

        # === ОСНОВНАЯ ОБЛАСТЬ ===
        main = tk.Frame(self, bg=COLORS['bg_primary'])
        main.pack(side='left', fill='both', expand=True)

        # Заголовок чата
        header = tk.Frame(main, bg=COLORS['bg_secondary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        header_inner = tk.Frame(header, bg=COLORS['bg_secondary'])
        header_inner.pack(fill='both', expand=True, padx=20)

        # Иконка статуса + имя
        name_frame = tk.Frame(header_inner, bg=COLORS['bg_secondary'])
        name_frame.pack(side='left', fill='y')

        status_dot = tk.Canvas(name_frame, width=10, height=10,
                               bg=COLORS['bg_secondary'], highlightthickness=0)
        status_dot.create_oval(1, 1, 9, 9, fill=COLORS['success'], outline='')
        status_dot.pack(side='left', padx=(0, 8), pady=20)

        tk.Label(name_frame, text=ASSISTANT_NAME,
                 bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
                 font=get_font('lg', bold=True)).pack(side='left')
        tk.Label(name_frame, text=f"  —  {ASSISTANT_DESCRIPTION}",
                 bg=COLORS['bg_secondary'], fg=COLORS['text_muted'],
                 font=get_font('sm')).pack(side='left')

        # Разделитель под заголовком
        tk.Frame(main, bg=COLORS['divider'], height=1).pack(fill='x')

        # Область сообщений
        self.chat_scroll = ScrollableFrame(main, bg_color=COLORS['bg_primary'])
        self.chat_scroll.pack(fill='both', expand=True)

        # Разделитель над вводом
        tk.Frame(main, bg=COLORS['divider'], height=1).pack(fill='x')

        # Область ввода
        input_area = tk.Frame(main, bg=COLORS['bg_secondary'], height=60)
        input_area.pack(fill='x')
        input_area.pack_propagate(False)

        input_inner = tk.Frame(input_area, bg=COLORS['bg_secondary'])
        input_inner.pack(fill='both', expand=True, padx=16, pady=10)

        # Поле ввода
        self.msg_entry = tk.Entry(input_inner, bg=COLORS['bg_input'],
                                  fg=COLORS['text_primary'],
                                  insertbackground=COLORS['text_primary'],
                                  font=get_font('md'), relief='flat',
                                  border=0)
        self.msg_entry.pack(side='left', fill='both', expand=True, padx=(8, 12))
        self.msg_entry.insert(0, "Напишите сообщение...")
        self.msg_entry.configure(fg=COLORS['text_secondary'])
        self.msg_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.msg_entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.msg_entry.bind('<Return>', lambda e: self._send_message())

        # Кнопка отправки
        self.send_btn = tk.Label(input_inner, text="  Отправить  ",
                                 bg=COLORS['accent'], fg=COLORS['text_on_accent'],
                                 font=get_font('sm', bold=True),
                                 cursor='hand2', padx=16, pady=4)
        self.send_btn.pack(side='right')
        self.send_btn.bind('<Button-1>', lambda e: self._send_message())
        self.send_btn.bind('<Enter>', lambda e: self.send_btn.configure(
            bg=COLORS['accent_hover']))
        self.send_btn.bind('<Leave>', lambda e: self.send_btn.configure(
            bg=COLORS['accent']))

    def _on_entry_focus_in(self, event):
        if self.msg_entry.get() == "Напишите сообщение...":
            self.msg_entry.delete(0, 'end')
            self.msg_entry.configure(fg=COLORS['text_primary'])

    def _on_entry_focus_out(self, event):
        if not self.msg_entry.get():
            self.msg_entry.insert(0, "Напишите сообщение...")
            self.msg_entry.configure(fg=COLORS['text_secondary'])

    def _navigate(self, key):
        for k, btn in self.nav_buttons.items():
            btn.set_active(k == key)
        if self.on_navigate and key != 'chat':
            self.on_navigate(key)

    def _load_messages(self):
        user_id = self.user_data.get('user', 1)
        try:
            msgs = msg_api.get_messages(user_id)
            for msg in msgs:
                self._add_bubble(msg['text'],
                                 msg['type'] == 'user',
                                 msg.get('date_time', ''),
                                 msg.get('message_id'))
            self.after(100, self.chat_scroll.scroll_to_bottom)
        except Exception as e:
            self._add_bubble(f"Ошибка загрузки: {e}", False, "")

    def _add_bubble(self, text, is_user, timestamp, msg_id=None):
        bubble = ChatBubble(self.chat_scroll.inner, text=text,
                            is_user=is_user, timestamp=timestamp,
                            message_id=msg_id)
        bubble.pack(fill='x')

    def _send_message(self):
        if self.is_sending:
            return
        text = self.msg_entry.get().strip()
        if not text or text == "Напишите сообщение...":
            return

        self.msg_entry.delete(0, 'end')
        self._add_bubble(text, True,
                         __import__('datetime').datetime.now().strftime('%H:%M'))
        self.chat_scroll.scroll_to_bottom()

        # Индикатор печати
        self.typing = TypingIndicator(self.chat_scroll.inner)
        self.typing.pack(fill='x')
        self.chat_scroll.scroll_to_bottom()

        self.is_sending = True
        user_id = self.user_data.get('user', 1)

        def do_send():
            try:
                result = msg_api.send_message(user_id, text)
                self.after(0, lambda: self._on_response(result))
            except Exception as e:
                self.after(0, lambda: self._on_response_error(str(e)))

        threading.Thread(target=do_send, daemon=True).start()

    def _on_response(self, result):
        self.typing.destroy()
        self.is_sending = False
        if result:
            self._add_bubble(result['text'], False,
                             result.get('date_time', ''),
                             result.get('message_id'))
        self.chat_scroll.scroll_to_bottom()

    def _on_response_error(self, error):
        self.typing.destroy()
        self.is_sending = False
        self._add_bubble(f"Ошибка: {error}", False, "")
        self.chat_scroll.scroll_to_bottom()

    def set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            btn.set_active(k == key)
