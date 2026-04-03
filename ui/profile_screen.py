"""Экран профиля пользователя."""

import tkinter as tk
from ui.theme import COLORS, get_font
from ui.components import ModernButton


class ProfileScreen(tk.Frame):
    """Просмотр профиля пользователя."""

    def __init__(self, parent, user_data=None, on_back=None, on_edit=None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.user_data = user_data or {}
        self.on_back = on_back
        self.on_edit = on_edit
        self._build_ui()

    def _build_ui(self):
        # Заголовок
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        back_btn = tk.Label(header, text="  \u2190  Назад  ",
                            bg=COLORS['bg_secondary'],
                            fg=COLORS['text_secondary'],
                            font=get_font('md'), cursor='hand2')
        back_btn.pack(side='left', padx=16, fill='y')
        back_btn.bind('<Button-1>', lambda e: self.on_back() if self.on_back else None)
        back_btn.bind('<Enter>', lambda e: back_btn.configure(fg=COLORS['text_primary']))
        back_btn.bind('<Leave>', lambda e: back_btn.configure(fg=COLORS['text_secondary']))

        tk.Label(header, text="Профиль", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_primary'], font=get_font('lg', bold=True)).pack(
            side='left', padx=8, fill='y')

        tk.Frame(self, bg=COLORS['divider'], height=1).pack(fill='x')

        # Контент
        content = tk.Frame(self, bg=COLORS['bg_primary'])
        content.pack(fill='both', expand=True, padx=40, pady=32)

        # Карточка профиля
        card = tk.Frame(content, bg=COLORS['bg_secondary'],
                        highlightbackground=COLORS['border'],
                        highlightthickness=1)
        card.pack(fill='x')

        inner = tk.Frame(card, bg=COLORS['bg_secondary'])
        inner.pack(fill='x', padx=32, pady=32)

        # Аватар (круг)
        avatar_size = 80
        avatar = tk.Canvas(inner, width=avatar_size, height=avatar_size,
                           bg=COLORS['bg_secondary'], highlightthickness=0)
        avatar.create_oval(2, 2, avatar_size - 2, avatar_size - 2,
                           fill=COLORS['accent'], outline=COLORS['accent_dark'],
                           width=2)
        initials = (self.user_data.get('first_name', 'П')[0] +
                    self.user_data.get('last_name', 'П')[0])
        avatar.create_text(avatar_size // 2, avatar_size // 2,
                           text=initials, fill='white',
                           font=get_font('xl', bold=True))
        avatar.pack(pady=(0, 16))

        # ФИО
        full_name = ' '.join(filter(None, [
            self.user_data.get('last_name', ''),
            self.user_data.get('first_name', ''),
            self.user_data.get('sur_name', '')
        ]))
        tk.Label(inner, text=full_name or 'Пользователь',
                 bg=COLORS['bg_secondary'], fg=COLORS['text_primary'],
                 font=get_font('xl', bold=True)).pack(pady=(0, 4))

        tk.Label(inner, text=f"@{self.user_data.get('login', 'user')}",
                 bg=COLORS['bg_secondary'], fg=COLORS['text_muted'],
                 font=get_font('sm')).pack(pady=(0, 20))

        # Разделитель
        tk.Frame(inner, bg=COLORS['divider'], height=1).pack(fill='x', pady=8)

        # Информация
        fields = [
            ("Дата рождения", self.user_data.get('date_birth', '—')),
            ("Образование", self.user_data.get('education_level', '—') or '—'),
            ("Специальность", self.user_data.get('education_specialize', self.user_data.get('education_specialice', '—')) or '—'),
            ("Интересы", self.user_data.get('interests', self.user_data.get('interest', '—')) or '—'),
        ]

        for label_text, value in fields:
            row = tk.Frame(inner, bg=COLORS['bg_secondary'])
            row.pack(fill='x', pady=6)
            tk.Label(row, text=label_text, bg=COLORS['bg_secondary'],
                     fg=COLORS['text_secondary'], font=get_font('sm'),
                     width=18, anchor='w').pack(side='left')
            tk.Label(row, text=value, bg=COLORS['bg_secondary'],
                     fg=COLORS['text_primary'], font=get_font('md'),
                     anchor='w').pack(side='left', fill='x', expand=True)

        # Кнопка редактирования
        tk.Frame(inner, bg=COLORS['bg_secondary'], height=16).pack()
        ModernButton(inner, text="Редактировать профиль",
                     command=self.on_edit,
                     bg_color=COLORS['accent_secondary'],
                     hover_color=COLORS['accent_secondary_hover']).pack()
