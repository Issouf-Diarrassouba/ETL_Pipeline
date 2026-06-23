import logging
import os 

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("etl_pipeline")
logger.setLevel(logging.DEBUG)

# prevent duplicate roots 
logger.propagate = False 
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


debug_handler = logging.FileHandler("logs/debug.log")
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(log_format)


error_handler = logging.FileHandler("logs/error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(log_format)


logger.addHandler(debug_handler)
logger.addHandler(error_handler)

