import configparser
import logging


logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get(section: str, option: str) -> str:
    try:
        return config.get(section, option)
    except configparser.NoOptionError as e:
        logger.warning(e.message)
        return option
    except configparser.NoSectionError as e:
        logger.warning(e.message)
        return option


config = configparser.ConfigParser()
