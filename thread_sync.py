"""
Thread synchronization utilities for Pro Driver Assist V2
"""
import threading
import logging
import time
from collections import deque
from typing import Callable, Any

class ThreadSync:
    def __init__(self):
        self._main_thread = threading.main_thread()
        self._lock = threading.Lock()
        self._task_queue = deque()
        self._results = {}
        self._result_ready = threading.Event()
        self._error_handlers = {}

    def is_main_thread(self) -> bool:
        """Check if current thread is main thread"""
        return threading.current_thread() is self._main_thread

    def run_on_main(self, func: Callable, *args, **kwargs) -> Any:
        """Run a function on the main thread and wait for result"""
        if self.is_main_thread():
            return func(*args, **kwargs)

        # Generate unique task ID
        task_id = threading.get_ident()
        
        with self._lock:
            self._task_queue.append((task_id, func, args, kwargs))
            self._result_ready.clear()

        # Wait for result with timeout
        timeout = kwargs.pop('timeout', 5.0)  # 5 second default timeout
        if self._result_ready.wait(timeout):
            with self._lock:
                if task_id in self._results:
                    result = self._results.pop(task_id)
                    if isinstance(result, Exception):
                        raise result
                    return result
                return None  # Task completed but no result
        else:
            raise TimeoutError(f"Task timed out after {timeout} seconds")

    def process_tasks(self):
        """Process queued tasks on main thread"""
        while True:
            try:
                with self._lock:
                    if not self._task_queue:
                        break
                    task_id, func, args, kwargs = self._task_queue.popleft()

                try:
                    result = func(*args, **kwargs)
                    with self._lock:
                        self._results[task_id] = result
                except Exception as e:
                    logging.error(f"Error in main thread task: {e}")
                    with self._lock:
                        self._results[task_id] = e
                    if task_id in self._error_handlers:
                        try:
                            self._error_handlers[task_id](e)
                        except:
                            pass

                self._result_ready.set()

            except Exception as e:
                logging.error(f"Error processing tasks: {e}")
                break

    def register_error_handler(self, task_id: int, handler: Callable[[Exception], None]):
        """Register an error handler for a specific task"""
        with self._lock:
            self._error_handlers[task_id] = handler

    def clear_tasks(self):
        """Clear all pending tasks"""
        with self._lock:
            self._task_queue.clear()
            self._results.clear()
            self._error_handlers.clear()
            self._result_ready.set()

# Global instance for convenience
thread_sync = ThreadSync()
