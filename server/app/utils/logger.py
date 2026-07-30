import logging
import sys
import io

def setup_logger(name: str = "tripgenie") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Ensure sys.stdout handles UTF-8 strings (e.g. ₹ currency symbols) safely on Windows
        try:
            stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except Exception:
            stream = sys.stdout

        handler = logging.StreamHandler(stream)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()
