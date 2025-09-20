from tkinter import ttk

class TabBase(ttk.Frame):
    """Base class for notebook tabs"""
    def __init__(self, parent, main_gui):
        super().__init__(parent)
        self.main_gui = main_gui
        self.grid_columnconfigure(0, weight=1)
        self.setup_tab()

    def setup_tab(self):
        """Override this method to set up the tab's contents"""
        pass
