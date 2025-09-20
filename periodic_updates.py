"""
Handle periodic updates for the Pro Driver Assist V2 GUI
"""
import logging
import time
import threading

class PeriodicUpdates:
    def __init__(self, gui):
        self.gui = gui
        self._updates_active = True
        self._update_initialized = False
        self._update_lock = threading.Lock()

    def start(self):
        """Initialize and start periodic updates"""
        if self._update_initialized:
            return

        try:
            with self._update_lock:
                self._update_initialized = True
                self._updates_active = True

            # Start visualization updates (60 FPS)
            self._schedule_visualization_update()
            
            # Start process checking (every 2 seconds)
            self._schedule_process_check()

        except Exception as e:
            logging.error(f"Error starting periodic updates: {e}")
            if self.gui.msgbox:
                self.gui.msgbox.showerror("Error", f"Failed to start updates: {e}")

    def stop(self):
        """Stop all periodic updates"""
        with self._update_lock:
            self._updates_active = False

    def _schedule_visualization_update(self):
        """Schedule the next visualization update"""
        if not self._should_continue():
            return

        try:
            self.gui.update_visualization()
        except Exception as e:
            logging.error(f"Error in visualization update: {e}")

        if self._should_continue():
            self.gui.root.after(16, self._schedule_visualization_update)

    def _schedule_process_check(self):
        """Schedule the next process check"""
        if not self._should_continue():
            return

        try:
            self._check_running_game()
        except Exception as e:
            logging.error(f"Error in process check: {e}")

        if self._should_continue():
            self.gui.root.after(1000, self._schedule_process_check)

    def _check_running_game(self):
        """Check for running games and update profile if needed"""
        from pro_driver_assist_v2 import detect_running_game, settings

        current_time = time.time()
        if current_time - self.gui.last_process_check <= self.gui.process_check_interval:
            return

        game = detect_running_game()
        if game != self.gui.current_game:
            self.gui.current_game = game
            if game:
                profile = settings.game_profiles.get(game)
                if profile:
                    def update_profile():
                        try:
                            self.gui.game_var.set(profile['name'])
                            self.gui.load_game_profile(profile)
                        except Exception as e:
                            logging.error(f"Error updating game profile: {e}")

                    # Ensure profile update happens on main thread
                    if threading.current_thread() is threading.main_thread():
                        update_profile()
                    else:
                        self.gui.root.after_idle(update_profile)

        self.gui.last_process_check = current_time

    def _should_continue(self):
        """Check if updates should continue"""
        return (self._updates_active and 
                self.gui and self.gui.root and 
                self.gui.root.winfo_exists())
