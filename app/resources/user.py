from flask_restful import Resource, reqparse
import requests
import json
from datetime import date
from bson.json_util import dumps
from bson.objectid import ObjectId
from pymongo import MongoClient

mongo = MongoClient("mongodb://localhost:27017/")
db = mongo.YourDatabaseName

class WechatLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code', required=True, type=str, help='Code cannot be blank')
        args = parser.parse_args()
        code = args['code']

        # 向微信服务器发送请求以获取访问令牌和用户信息
        wechat_params = {
            "appid": "wx119cd856b94e2022",
            "secret": "1d680a99f50a791d44180dac063001d8",
            "js_code": code,
            "grant_type": "authorization_code",
        }
        wechat_response = requests.get(
            "https://api.weixin.qq.com/sns/jscode2session", params=wechat_params
        )
        wechat_data = wechat_response.json()

        # 在这里处理微信服务器返回的数据，包括访问令牌和用户信息
        session_key = wechat_data.get("session_key")
        openid = wechat_data.get("openid")
        # if not exist in database,  insert into database otherwise update database
        user = User.objects.filter(user_id=openid)
        if not user:
            user = User(
                user_id=openid,
                points=5,
                is_check=False,
            )
            user.save()
            response_data = {
                "session_key": session_key,
                "user": {
                    "user_id": openid,
                    "points": 5,
                    "is_check": False,
                },
            }
        else:
            user = user[0]
            user.last_check_date = date.today()
            user.save()
            response_data = {
                "session_key": session_key,
                "user": {
                    "user_id": openid,
                    "points": user.points,
                    "is_check": user.is_check,
                },
            }


        # 假设您有一个方法来处理和返回用户信息
        return response_data


class User(Resource):
    def get(self, user_id):
        try:
            # ObjectId用于处理MongoDB中的默认_id格式
            user = db.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            return {'error': str(e)}, 400

        if user:
            # 将MongoDB对象转换为JSON
            user_json = json.loads(dumps(user))
            return user_json, 200
        else:
            return {'message': 'User not found'}, 404
        
        