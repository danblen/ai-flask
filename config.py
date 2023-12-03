import os
import configparser


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"


def read_config():
    config = configparser.ConfigParser()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config/config.ini")
    config.read(config_path)

    # 获取配置文件中的值
    appId = config["AppConfig"]["appId"]
    secret = config["AppConfig"]["secret"]

    return {
        "appId": appId,
        "secret": secret,
    }
