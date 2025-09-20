import threading
import tkinter as tk
import logging
from tkinter import messagebox

class ThreadSafeUI:
    """Thread-safe UI operations manager"""
    def __init__(self, root):
        self.root = root
        self._ui_lock = threading.Lock()

    def show_error(self, title, message):
        """Show error dialog in a thread-safe manner"""
        if not threading.current_thread() is threading.main_thread():
            if self.root:
                self.root.after_idle(lambda: self.show_error(title, message))
            return

        with self._ui_lock:
            try:
                messagebox.showerror(title, message)
            except Exception as e:
                logging.error(f"Failed to show error dialog: {e}")

    def show_info(self, title, message):
        """Show info dialog in a thread-safe manner"""
        if not threading.current_thread() is threading.main_thread():
            if self.root:
                self.root.after_idle(lambda: self.show_info(title, message))
            return

        with self._ui_lock:
            try:
                messagebox.showinfo(title, message)
            except Exception as e:
                logging.error(f"Failed to show info dialog: {e}")

    def update_widget(self, widget, update_func):
        """Update a widget in a thread-safe manner"""
        if not threading.current_thread() is threading.main_thread():
            if self.root:
                self.root.after_idle(lambda: self.update_widget(widget, update_func))
            return

        with self._ui_lock:
            try:
                update_func(widget)
            except Exception as e:
                logging.error(f"Failed to update widget: {e}")
                self.show_error("Error", f"Failed to update widget: {e}")

    # Alias methods for compatibility with messagebox interface
    showinfo = show_info
    showerror = show_error
    showwarning = messagebox.showwarning
    askyesno = messagebox.askyesno
    askokcancel = messagebox.askokcancel

    def validate_in_main_thread(self):
        """Validate that we're in the main thread"""
        return threading.current_thread() is threading.main_thread()
