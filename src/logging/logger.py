import logging
from configuration.config import settings


logger = logging.getLogger(__name__)
logging.basicConfig(filename=settings.LOG_FILE, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
