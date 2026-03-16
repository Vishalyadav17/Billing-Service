import logging
import os


class Logger:
    def __init__(self, service_name: str):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(service_name)
        env = os.getenv("ENV", "dev").lower()
        if env in ("dev", "local"):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    @classmethod
    def get_logger(cls, service_name: str) -> logging.Logger:
        instance = cls(service_name)
        return instance.logger


logger = Logger.get_logger("billing-system")
