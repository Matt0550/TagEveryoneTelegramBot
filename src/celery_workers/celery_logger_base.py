import logging
import os
from logging.handlers import RotatingFileHandler

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, "celery.log"),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

# Set debug level for "logger_base"
logging.getLogger("logger_base").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
