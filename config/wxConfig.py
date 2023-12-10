from config import read_config

config_data = read_config()


wxConfig = {
    "appid": config_data["appId"],
    "secret": config_data["secret"],
    "url": "https://api.weixin.qq.com/sns/jscode2session",
    "grant_type": "authorization_code",
}
