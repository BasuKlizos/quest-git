import logging
import os


class LoggerUtil:

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "app.log")

    @classmethod
    def setup_logger(cls, name):

        os.makedirs(cls.LOG_DIR, exist_ok=True)

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if logger.hasHandlers():
            return logger

        log_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

        # save
        # file_handler = logging.FileHandler(cls.LOG_FILE, encoding="utf-8")
        # file_handler.setFormatter(log_format)
        # file_handler.setLevel(logging.DEBUG)

        # Display
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(log_format)
        # console_handler.setLevel(logging.INFO)

        # if not logger.hasHandlers():  # Prevent duplicate handlers
        #     logger.addHandler(file_handler)
        #     # logger.addHandler(console_handler)

        return logger
