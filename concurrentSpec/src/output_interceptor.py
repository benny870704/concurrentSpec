import io, sys
import logging

class OutputInterceptor:
    class CustomLogHandler(logging.Handler):
        def __init__(self):
            logging.Handler.__init__(self)
            self.logs = []

        def emit(self, record):
            msg = self.format(record)
            self.logs.append(msg)

    def __init__(self):
        self.captured_output = io.StringIO()
        self.captured_error = io.StringIO()
        self.log_handler = self.CustomLogHandler()

    def start(self, output=True, error=True, log=True):
        self.capture_output = output
        self.capture_error = error
        self.capture_log = log
        if output: sys.stdout = self.captured_output
        if error: sys.stderr = self.captured_error
        if log: self.__intercept_log_from_root_logger()

    def stop(self):
        if self.capture_output: sys.stdout = sys.__stdout__
        if self.capture_error: sys.stderr = sys.__stderr__
        if self.capture_log: self.__stop_intercept_log()

    def get_captured_output(self) -> str:
        return self.captured_output.getvalue()
    
    def get_captured_error(self) -> str:
        return self.captured_error.getvalue()
    
    def get_captured_logs(self) -> list:
        return self.log_handler.logs

    def __intercept_log_from_root_logger(self):
        # Remove the default StreamHandler from the root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                root_logger.removeHandler(handler)

        # Create a custom log handler and add it to the root logger
        logging.getLogger().addHandler(self.log_handler)

    def __stop_intercept_log(self):
        logging.getLogger().addHandler(logging.StreamHandler())

