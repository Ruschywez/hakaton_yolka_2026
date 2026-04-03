"""Ёлка — Карьерный AI Ассистент. Точка входа."""

import tkinter as tk
import sys
import os

# Добавляем корень проекта в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import App


def main():
    root = tk.Tk()

    # Иконка окна (если есть)
    try:
        root.iconbitmap(os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico'))
    except Exception:
        pass

    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
