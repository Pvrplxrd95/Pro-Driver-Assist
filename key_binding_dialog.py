"""
Key Binding Dialog for selecting keyboard controls
"""
import tkinter as tk
from tkinter import ttk
import keyboard
import logging

class KeyBindDialog:
    def __init__(self, parent, title, current_key=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.result = None
        self.current_key = current_key
        self.listening = False

        # Known gaming keys that are commonly used
        self.known_keys = [
            'w', 'a', 's', 'd',  # WASD
            'up', 'down', 'left', 'right',  # Arrow keys
            'space', 'shift', 'ctrl', 'alt',  # Modifier keys
            'tab', 'enter', 'esc',  # Function keys
            '1', '2', '3', '4', '5',  # Number keys
            'q', 'e', 'r', 'f',  # Additional common gaming keys
            'z', 'x', 'c', 'v'  # Bottom row keys
        ]

        self._create_widgets()
        self._center_dialog()

    def _create_widgets(self):
        """Create dialog widgets"""
        # Main content frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Instructions
        ttk.Label(main_frame,
                 text="Choose a key from the list or press 'Listen' to detect any key press",
                 wraplength=300).grid(row=0, column=0, columnspan=2, pady=10)

        # Current binding
        if self.current_key:
            ttk.Label(main_frame,
                     text=f"Current binding: {self.current_key}").grid(
                         row=1, column=0, columnspan=2, pady=5)

        # Known keys listbox
        ttk.Label(main_frame, text="Common Keys:").grid(row=2, column=0, sticky="w", pady=5)
        self.key_listbox = tk.Listbox(main_frame, height=10, width=20)
        self.key_listbox.grid(row=3, column=0, padx=5, pady=5)

        # Populate listbox
        for key in self.known_keys:
            self.key_listbox.insert(tk.END, key)

        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical",
                                command=self.key_listbox.yview)
        scrollbar.grid(row=3, column=1, sticky="ns")
        self.key_listbox.config(yscrollcommand=scrollbar.set)

        # Listen button
        self.listen_button = ttk.Button(main_frame, text="Listen for Key",
                                      command=self.start_listening)
        self.listen_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        # OK and Cancel buttons
        ttk.Button(button_frame, text="OK",
                  command=self.ok_pressed).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel",
                  command=self.cancel_pressed).pack(side=tk.LEFT, padx=5)

        # Bind listbox selection
        self.key_listbox.bind('<<ListboxSelect>>', self.on_select)

        # Bind keyboard events for listen mode
        self.dialog.bind('<Key>', self.on_key_press)

    def _center_dialog(self):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        parent = self.dialog.master

        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2

        self.dialog.geometry(f"+{x}+{y}")

    def start_listening(self):
        """Start listening for key presses"""
        if not self.listening:
            self.listening = True
            self.listen_button.configure(text="Press any key (ESC to cancel)")
            self.key_listbox.selection_clear(0, tk.END)

    def on_key_press(self, event):
        """Handle key press when in listen mode"""
        if self.listening:
            if event.keysym.lower() == 'escape':
                self.listening = False
                self.listen_button.configure(text="Listen for Key")
                return

            self.result = event.keysym.lower()
            self.ok_pressed()

    def on_select(self, event):
        """Handle listbox selection"""
        if self.listening:
            self.listening = False
            self.listen_button.configure(text="Listen for Key")

        selection = self.key_listbox.curselection()
        if selection:
            self.result = self.key_listbox.get(selection[0])

    def ok_pressed(self):
        """Handle OK button press"""
        if not self.result and self.key_listbox.curselection():
            self.result = self.key_listbox.get(self.key_listbox.curselection())
        self.dialog.destroy()

    def cancel_pressed(self):
        """Handle Cancel button press"""
        self.result = None
        self.dialog.destroy()

    def get_result(self):
        """Get the selected key"""
        self.dialog.wait_window()
        return self.result
