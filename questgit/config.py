import os
from typing import Dict
from utils.file_utils import FileHandler
from utils.constants import GIT_DIR
from utils.logger_utils import LoggerUtil

logger = LoggerUtil.setup_logger(__name__)


class Config:
    CONFIG_PATH = os.path.join(GIT_DIR, "config")

    @staticmethod
    def set(key: str, value: str):
        config = (
            FileHandler.read_config(Config.CONFIG_PATH)
            if os.path.exists(Config.CONFIG_PATH)
            else {}
        )
        config[key] = value
        FileHandler.write_config(Config.CONFIG_PATH, config)
        logger.info(f"Config set: {key}={value}")

    @staticmethod
    def validate_required() -> bool:
        try:
            if not os.path.exists(Config.CONFIG_PATH):
                logger.debug("Config file not found")
                return False

            config = FileHandler.read_config(Config.CONFIG_PATH)

            required_keys = ["user.name", "user.email"]
            return all(
                key in config and bool(config[key].strip()) for key in required_keys
            )

        except Exception as e:
            logger.error(f"Config validation failed: {str(e)}")
            return False

    @staticmethod
    def prompt_setup():
        print("Initial configuration required for commits:")
        name = input("Your name: ").strip()
        email = input("Your email: ").strip()

        Config.set("user.name", name)
        Config.set("user.email", email)
        print("Configuration saved.")
