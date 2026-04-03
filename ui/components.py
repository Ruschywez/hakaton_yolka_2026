"""Переиспользуемые UI-компоненты."""

import tkinter as tk
from tkinter import ttk
from ui.theme import COLORS, get_font, SIDEBAR_WIDTH
from config import ASSISTANT_NAME


class ModernEntry(tk.Frame):
    """Стилизованное поле ввода с placeholder."""

    def __init__(self, parent, placeholder="", show=None, **kwargs):
        super().__init__(parent, bg=COLORS['bg_input'],
                         highlightthickness=2,
                         highlightbackground=COLORS['border'],
                         highlightcolor=COLORS['border_focus'])
        self.placeholder = placeholder
        self.show_char = show
        self.has_placeholder = True

        self.entry = tk.Entry(self, bg=COLORS['bg_input'],
                              fg=COLORS['text_secondary'],
                              insertbackground=COLORS['text_primary'],
                              font=get_font('md'), relief='flat', border=0)
        self.entry.pack(fill='x', padx=10, pady=8)

        if placeholder:
            self.entry.insert(0, placeholder)
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)
        self.entry.bind('<Return>', lambda e: kwargs.get('on_return', lambda: None)())

    def _on_focus_in(self, event):
        if self.has_placeholder:
            self.entry.delete(0, 'end')
            self.entry.config(fg=COLORS['text_primary'])
            if self.show_char:
                self.entry.config(show=self.show_char)
            self.has_placeholder = False

    def _on_focus_out(self, event):
        if not self.entry.get():
            self.entry.config(fg=COLORS['text_secondary'])
            if self.show_char:
                self.entry.config(show='')
            self.entry.insert(0, self.placeholder)
            self.has_placeholder = True

    def get(self):
        return '' if self.has_placeholder else self.entry.get()

    def set(self, text):
        self.has_placeholder = False
        self.entry.delete(0, 'end')
        self.entry.config(fg=COLORS['text_primary'])
        if self.show_char:
            self.entry.config(show=self.show_char)
        self.entry.insert(0, text)

    def clear(self):
        self.entry.delete(0, 'end')
        self.entry.config(fg=COLORS['text_secondary'])
        if self.show_char:
            self.entry.config(show='')
        self.entry.insert(0, self.placeholder)
        self.has_placeholder = True


class ModernButton(tk.Frame):
    """Стилизованная кнопка с hover-эффектом."""

    def __init__(self, parent, text="", command=None,
                 bg_color=None, hover_color=None, text_color=None,
                 font_config=None, padx=24, pady=10, full_width=False):
        self.bg_color = bg_color or COLORS['accent']
        self.hover_color = hover_color or COLORS['accent_hover']
        self.text_color = text_color or COLORS['text_on_accent']
        self.command = command

        parent_bg = COLORS['bg_primary']
        try:
            parent_bg = parent.cget('bg')
        except Exception:
            pass

        super().__init__(parent, bg=parent_bg)

        self.btn_frame = tk.Frame(self, bg=self.bg_color, cursor='hand2')
        if full_width:
            self.btn_frame.pack(fill='x')
        else:
            self.btn_frame.pack()

        self.label = tk.Label(self.btn_frame, text=text,
                              bg=self.bg_color, fg=self.text_color,
                              font=font_config or get_font('md', bold=True),
                              padx=padx, pady=pady)
        self.label.pack(expand=True, fill='both')

        for w in [self.btn_frame, self.label]:
            w.bind('<Enter>', self._on_enter)
            w.bind('<Leave>', self._on_leave)
            w.bind('<Button-1>', self._on_click)

    def _on_enter(self, event):
        self.btn_frame.configure(bg=self.hover_color)
        self.label.configure(bg=self.hover_color)

    def _on_leave(self, event):
        self.btn_frame.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color)

    def _on_click(self, event):
        if self.command:
            self.command()

    def set_enabled(self, enabled):
        color = self.bg_color if enabled else COLORS['bg_tertiary']
        self.btn_frame.configure(bg=color)
        self.label.configure(bg=color)
        self.command = self.command if enabled else None


class SidebarButton(tk.Frame):
    """Кнопка бокового меню."""

    def __init__(self, parent, text="", icon="", command=None, active=False):
        self.is_active = active
        self.command = command
        self.normal_bg = COLORS['bg_sidebar']
        self.hover_bg = COLORS['bg_hover']
        self.active_bg = COLORS['bg_tertiary']
        bg = self.active_bg if active else self.normal_bg

        super().__init__(parent, bg=bg, cursor='hand2')

        self.indicator = tk.Frame(self, bg=COLORS['accent'] if active else bg, width=3)
        self.indicator.pack(side='left', fill='y')

        display_text = f"  {icon}  {text}" if icon else f"    {text}"
        self.label = tk.Label(self, text=display_text, bg=bg,
                              fg=COLORS['text_primary'] if active else COLORS['text_secondary'],
                              font=get_font('md', bold=active),
                              anchor='w', padx=8, pady=12)
        self.label.pack(side='left', fill='x', expand=True)

        for w in [self, self.label]:
            w.bind('<Enter>', self._on_enter)
            w.bind('<Leave>', self._on_leave)
            w.bind('<Button-1>', self._on_click)

    def set_active(self, active):
        self.is_active = active
        bg = self.active_bg if active else self.normal_bg
        self.configure(bg=bg)
        self.label.configure(
            bg=bg,
            fg=COLORS['text_primary'] if active else COLORS['text_secondary'],
            font=get_font('md', bold=active))
        self.indicator.configure(bg=COLORS['accent'] if active else bg)

    def _on_enter(self, event):
        if not self.is_active:
            self.configure(bg=self.hover_bg)
            self.label.configure(bg=self.hover_bg)

    def _on_leave(self, event):
        if not self.is_active:
            self.configure(bg=self.normal_bg)
            self.label.configure(bg=self.normal_bg)

    def _on_click(self, event):
        if self.command:
            self.command()


class ScrollableFrame(tk.Frame):
    """Прокручиваемый контейнер."""

    def __init__(self, parent, bg_color=None):
        bg = bg_color or COLORS['bg_primary']
        super().__init__(parent, bg=bg)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical',
                                       command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)

        self.inner.bind('<Configure>',
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox('all')))
        self.win_id = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')

        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all(
            '<MouseWheel>', self._on_mousewheel))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all('<MouseWheel>'))
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.win_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)


class ChatBubble(tk.Frame):
    """Пузырёк сообщения в чате."""

    def __init__(self, parent, text="", is_user=True, timestamp="", message_id=None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        self.message_id = message_id

        container = tk.Frame(self, bg=COLORS['bg_primary'])
        container.pack(fill='x', padx=16, pady=4)

        bubble_bg = COLORS['bubble_user'] if is_user else COLORS['bubble_ai']
        bubble_fg = COLORS['bubble_user_text'] if is_user else COLORS['bubble_ai_text']
        pack_side = 'right' if is_user else 'left'

        bubble = tk.Frame(container, bg=bubble_bg)
        if not is_user:
            bubble.configure(highlightbackground=COLORS['bubble_ai_border'],
                             highlightthickness=1)
        bubble.pack(side=pack_side)

        sender = "Вы" if is_user else ASSISTANT_NAME
        tk.Label(bubble, text=sender, bg=bubble_bg, fg=bubble_fg,
                 font=get_font('xs', bold=True), anchor='w').pack(
            fill='x', padx=12, pady=(8, 0))

        tk.Label(bubble, text=text, bg=bubble_bg, fg=bubble_fg,
                 font=get_font('md'), wraplength=450,
                 justify='left', anchor='w').pack(
            fill='x', padx=12, pady=(4, 4))

        time_fg = '#d4a0ab' if is_user else COLORS['text_muted']
        tk.Label(bubble, text=timestamp, bg=bubble_bg, fg=time_fg,
                 font=get_font('xs'), anchor='e').pack(
            fill='x', padx=12, pady=(0, 8))


class TypingIndicator(tk.Frame):
    """Индикатор 'печатает...'."""

    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        container = tk.Frame(self, bg=COLORS['bg_primary'])
        container.pack(fill='x', padx=16, pady=4)

        bubble = tk.Frame(container, bg=COLORS['bubble_ai'],
                          highlightbackground=COLORS['bubble_ai_border'],
                          highlightthickness=1)
        bubble.pack(side='left')

        tk.Label(bubble, text=ASSISTANT_NAME, bg=COLORS['bubble_ai'],
                 fg=COLORS['bubble_ai_text'],
                 font=get_font('xs', bold=True), anchor='w').pack(
            fill='x', padx=12, pady=(8, 0))

        self.dots_label = tk.Label(bubble, text="печатает...",
                                   bg=COLORS['bubble_ai'],
                                   fg=COLORS['text_secondary'],
                                   font=get_font('md'), anchor='w')
        self.dots_label.pack(fill='x', padx=12, pady=(4, 8))
