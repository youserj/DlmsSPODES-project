import configparser

config = configparser.ConfigParser()
config.read(
    filenames="./config.ini",
    encoding="utf-8")
