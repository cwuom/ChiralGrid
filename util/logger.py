import time
import threading

LEVEL_DEBUG = 1
LEVEL_INFO = 2
LEVEL_WARNING = 3
LEVEL_ERROR = 4


def get_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


class Logger:
    def __init__(self, level: int = LEVEL_INFO, log_file=None):
        self.log_file = log_file
        self.level = level
        self.lock = threading.Lock()

    def output(self, level, message):
        _time = get_time()
        with self.lock:
            self.write_to_log_file(_time, level, message)
            print(f"[{_time}] [{level}] : {message}")

    def info(self, message):
        if self.level <= LEVEL_INFO:
            threading.Thread(target=self.output, args=("I", message)).start()

    def error(self, message):
        if self.level <= LEVEL_ERROR:
            threading.Thread(target=self.output, args=("E", message)).start()

    def debug(self, message):
        if self.level <= LEVEL_DEBUG:
            threading.Thread(target=self.output, args=("D", message)).start()

    def warning(self, message):
        if self.level <= LEVEL_WARNING:
            threading.Thread(target=self.output, args=("W", message)).start()

    def write_to_log_file(self, _time, level, message):
        if self.log_file is None:
            return

        with open(self.log_file, 'a') as f:
            f.write(f"[{_time}] [{level}] : {message}\n")
