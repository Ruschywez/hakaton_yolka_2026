"""Экран редактирования профиля."""

import tkinter as tk
from tkinter import ttk
from ui.theme import COLORS, get_font
from ui.components import ModernEntry, ModernButton
from api import auth as auth_api

EDUCATION_LEVELS = [
    "",
    "Среднее общее",
    "Среднее профессиональное образование",
    "Бакалавриат",
    "Специалитет",
    "Магистратура",
]


class EditProfileScreen(tk.Frame):
    """Редактирование данных профиля."""

    def __init__(self, parent, user_data=None, on_back=None, on_save=None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.user_data = user_data or {}
        self.on_back = on_back
        self.on_save = on_save
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

        tk.Label(header, text="Изменить данные", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_primary'], font=get_font('lg', bold=True)).pack(
            side='left', padx=8, fill='y')

        tk.Frame(self, bg=COLORS['divider'], height=1).pack(fill='x')

        # Контент
        content = tk.Frame(self, bg=COLORS['bg_primary'])
        content.pack(fill='both', expand=True, padx=40, pady=32)

        card = tk.Frame(content, bg=COLORS['bg_secondary'],
                        highlightbackground=COLORS['border'],
                        highlightthickness=1)
        card.pack(fill='x')

        inner = tk.Frame(card, bg=COLORS['bg_secondary'])
        inner.pack(fill='x', padx=32, pady=32)

        # Две колонки
        columns = tk.Frame(inner, bg=COLORS['bg_secondary'])
        columns.pack(fill='x')

        left = tk.Frame(columns, bg=COLORS['bg_secondary'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 16))

        right = tk.Frame(columns, bg=COLORS['bg_secondary'])
        right.pack(side='left', fill='both', expand=True, padx=(16, 0))

        self.entries = {}

        # Левая колонка
        left_fields = [
            ('last_name', 'Фамилия'),
            ('first_name', 'Имя'),
            ('sur_name', 'Отчество'),
            ('date_birth', 'Дата рождения'),
        ]
        for key, label in left_fields:
            tk.Label(left, text=label, bg=COLORS['bg_secondary'],
                     fg=COLORS['text_secondary'], font=get_font('sm'),
                     anchor='w').pack(fill='x', pady=(0, 2))
            entry = ModernEntry(left, placeholder=label)
            if key == 'sur_name':
                val = self.user_data.get('surname', self.user_data.get('sur_name', ''))
            else:
                val = self.user_data.get(key, '')
            if val:
                entry.set(val)
            entry.pack(fill='x', pady=(0, 12))
            self.entries[key] = entry

        # Правая колонка — Уровень образования (выпадающий список)
        tk.Label(right, text="Уровень образования", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_secondary'], font=get_font('sm'),
                 anchor='w').pack(fill='x', pady=(0, 2))

        combo_frame = tk.Frame(right, bg=COLORS['bg_input'],
                               highlightthickness=2,
                               highlightbackground=COLORS['border'],
                               highlightcolor=COLORS['border_focus'])
        combo_frame.pack(fill='x', pady=(0, 12))

        self.education_combo = ttk.Combobox(
            combo_frame, values=EDUCATION_LEVELS[1:],
            state='readonly', font=get_font('md'))
        self.education_combo.pack(fill='x', padx=6, pady=6)

        # Стиль combobox
        style = ttk.Style()
        style.configure('TCombobox',
                        fieldbackground=COLORS['bg_input'],
                        background=COLORS['bg_tertiary'],
                        foreground=COLORS['text_primary'],
                        arrowsize=14)
        style.map('TCombobox',
                  fieldbackground=[('readonly', COLORS['bg_input'])],
                  foreground=[('readonly', COLORS['text_primary'])])

        current_edu = self.user_data.get('education_level', '')
        if current_edu:
            self.education_combo.set(current_edu)

        # Специальность
        tk.Label(right, text="Специальность", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_secondary'], font=get_font('sm'),
                 anchor='w').pack(fill='x', pady=(0, 2))
        spec_entry = ModernEntry(right, placeholder="Ваша специальность")
        val = self.user_data.get('education_specialize', self.user_data.get('education_specialice', ''))
        if val:
            spec_entry.set(val)
        spec_entry.pack(fill='x', pady=(0, 12))
        self.entries['education_specialice'] = spec_entry # API ждёт 'c' на входе

        tk.Label(right, text="Увлечения", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_secondary'], font=get_font('sm'),
                 anchor='w').pack(fill='x', pady=(0, 2))
        interest_entry = ModernEntry(right, placeholder="Ваши увлечения")
        val = self.user_data.get('interests', self.user_data.get('interest', ''))
        if val:
            interest_entry.set(val)
        interest_entry.pack(fill='x', pady=(0, 12))
        self.entries['interests'] = interest_entry # API ждёт 'interests' (plural)

        # Новый пароль
        tk.Label(right, text="Новый пароль", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_secondary'], font=get_font('sm'),
                 anchor='w').pack(fill='x', pady=(0, 2))
        pass_entry = ModernEntry(right, placeholder="Новый пароль", show="*")
        pass_entry.pack(fill='x', pady=(0, 12))
        self.entries['password'] = pass_entry

        # Сообщение
        self.msg_label = tk.Label(inner, text="", bg=COLORS['bg_secondary'],
                                  font=get_font('sm'))
        self.msg_label.pack(fill='x', pady=(8, 4))

        # Кнопки
        btn_frame = tk.Frame(inner, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill='x', pady=(8, 0))

        ModernButton(btn_frame, text="Сохранить",
                     command=self._do_save).pack(side='left', padx=(0, 12))
        ModernButton(btn_frame, text="Отмена", command=self.on_back,
                     bg_color=COLORS['bg_tertiary'],
                     hover_color=COLORS['bg_hover']).pack(side='left')

    def _do_save(self):
        data = {}
        for key, entry in self.entries.items():
            val = entry.get()
            if val:
                data[key] = val

        # Уровень образования из выпадающего списка
        edu_val = self.education_combo.get()
        if edu_val:
            data['education_level'] = edu_val
            
        user_ident = self.user_data.get('user_id', self.user_data.get('user'))
        if user_ident:
            data['user_id'] = user_ident

        if not data or len(data) == 1: # only user_id
            self.msg_label.configure(text="Нечего сохранять",
                                     fg=COLORS['warning'])
            return

        try:
            auth_api.update_profile(**data)
            
            # Синхронизируем локальные данные (учитываем расхождения в ключах API)
            for k, v in data.items():
                if k == 'password': continue
                self.user_data[k] = v
                
                # Дублируем для совместимости с отображением (z/c и surname/sur_name)
                if k == 'education_specialice': self.user_data['education_specialize'] = v
                if k == 'sur_name': self.user_data['surname'] = v
                if k == 'interests': self.user_data['interest'] = v

            self.msg_label.configure(text="Данные сохранены!",
                                     fg=COLORS['success'])
            if self.on_save:
                self.on_save(self.user_data)
        except Exception as e:
            self.msg_label.configure(text=f"Ошибка: {e}",
                                     fg=COLORS['error'])
