import logging
import sys
from tkinter import messagebox


def main():
    try:
        # Initialize settings
        from settings_new import Settings
        settings = Settings()
        config = settings.config  # Get the config dictionary

        # Create GUI with settings object
        from settings_gui import SettingsGUI
        gui = SettingsGUI(config)  # Pass the config dictionary

        # Initialize input manager
        try:
            from input_manager import InputManager
            input_manager = InputManager(config, gui)
            gui.input_manager = input_manager
            logging.info("Input manager initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize input manager: {e}")
            input_manager = None

        # Run main loop
        gui.run()

        # Save settings and cleanup on exit
        try:
            settings.config = gui.settings.config  # Get updated config from GUI
            settings.save()
            logging.info("Settings saved successfully")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

        # Cleanup
        if input_manager:
            try:
                input_manager.cleanup()
                logging.info("Input manager cleaned up successfully")
            except Exception as e:
                logging.error(f"Error during input manager cleanup: {e}")

    except Exception as e:
        logging.error(f"Application startup error: {e}")
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Application Error", f"A critical error occurred: {e}")
        except:
            pass  # If even the error message fails, just log it
        sys.exit(1)
