import hashlib
from logger_utils import LoggerUtil

logger = LoggerUtil.setup_logger(__name__)


class HashCalculate:
    @staticmethod
    def calculate_sha1(content: str) -> str:

        if not content:
            logger.error("Hash's content is empty or none.")
            raise ValueError("Content connot be empty or none.")

        hash_digested = hashlib.sha1(content.encode()).hexdigest()
        logger.info(f"Hash calculated successfully: {hash_digested}.")

        return hash_digested
