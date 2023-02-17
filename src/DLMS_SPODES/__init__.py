import configparser
from . import settings

# set language
config = configparser.ConfigParser()
if config.read("config.ini") and __name__ in config.sections():
    language = config[__name__].get("language")
    settings.set_current_language(language)


from .cosem_interface_classes import collection