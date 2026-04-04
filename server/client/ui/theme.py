"""Тема и стили приложения."""

import tkinter as tk
from tkinter import ttk

COLORS = {
    'bg_primary': '#0f0f1a',
    'bg_secondary': '#1a1a2e',
    'bg_tertiary': '#252547',
    'bg_sidebar': '#0a0a14',
    'bg_input': '#1e1e3f',
    'bg_hover': '#2a2a4a',
    'bg_card': '#16213e',
    'accent': '#e94560',
    'accent_hover': '#ff6b81',
    'accent_dark': '#c23152',
    'accent_secondary': '#6c63ff',
    'accent_secondary_hover': '#8b83ff',
    'text_primary': '#eaeaea',
    'text_secondary': '#8892b0',
    'text_muted': '#5a6480',
    'text_on_accent': '#ffffff',
    'bubble_user': '#e94560',
    'bubble_user_text': '#ffffff',
    'bubble_ai': '#1e1e3f',
    'bubble_ai_text': '#eaeaea',
    'bubble_ai_border': '#3a3a6a',
    'border': '#2a2a4a',
    'border_focus': '#6c63ff',
    'scrollbar': '#3a3a5a',
    'scrollbar_hover': '#4a4a6a',
    'success': '#64ffda',
    'error': '#ff6b6b',
    'warning': '#ffd93d',
    'divider': '#1e1e38',
}

FONTS = {
    'family': 'Segoe UI',
    'family_mono': 'Consolas',
    'size_xs': 9, 'size_sm': 10, 'size_md': 11,
    'size_lg': 13, 'size_xl': 16, 'size_xxl': 20, 'size_title': 24,
}

SIDEBAR_WIDTH = 220


def get_font(size='md', bold=False):
    """Получить кортеж шрифта."""
    family = FONTS['family']
    sz = FONTS.get(f'size_{size}', FONTS['size_md'])
    weight = 'bold' if bold else 'normal'
    return (family, sz, weight)


def apply_theme(root):
    """Применить тёмную тему."""
    root.configure(bg=COLORS['bg_primary'])
    style = ttk.Style()
    style.theme_use('clam')

    style.configure('.', background=COLORS['bg_primary'],
                    foreground=COLORS['text_primary'], font=get_font('md'))
    style.configure('TFrame', background=COLORS['bg_primary'])
    style.configure('Sidebar.TFrame', background=COLORS['bg_sidebar'])
    style.configure('TLabel', background=COLORS['bg_primary'],
                    foreground=COLORS['text_primary'])
    style.configure('Sidebar.TLabel', background=COLORS['bg_sidebar'],
                    foreground=COLORS['text_primary'])
    style.configure('Muted.TLabel', foreground=COLORS['text_secondary'])
    style.configure('Title.TLabel', font=get_font('title', bold=True))
    style.configure('Heading.TLabel', font=get_font('xl', bold=True))

    style.configure('TEntry', fieldbackground=COLORS['bg_input'],
                    foreground=COLORS['text_primary'],
                    insertcolor=COLORS['text_primary'], borderwidth=0)

    style.configure('TButton', background=COLORS['accent'],
                    foreground=COLORS['text_on_accent'], borderwidth=0,
                    font=get_font('md', bold=True))
    style.map('TButton',
              background=[('active', COLORS['accent_hover']),
                          ('pressed', COLORS['accent_dark'])])

    style.configure('Vertical.TScrollbar',
                    background=COLORS['scrollbar'],
                    troughcolor=COLORS['bg_primary'],
                    borderwidth=0, arrowsize=0)
    style.map('Vertical.TScrollbar',
              background=[('active', COLORS['scrollbar_hover'])])
