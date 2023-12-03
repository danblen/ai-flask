from flask_restful import Resource, reqparse
import requests
import json
from datetime import datetime, date
from bson.json_util import dumps
from bson.objectid import ObjectId
from pymongo import MongoClient

mongo = MongoClient("mongodb://localhost:27017/")
db = mongo.myapp

wxConfig = {
    "appid": "wx3e67e2268416075f",
    "secret": "c49ae70f9b671c074c3f684687c27177",
    "url": "https://api.weixin.qq.com/sns/jscode2session",
    "grant_type": "authorization_code",
}


class WechatLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "code", required=True, type=str, help="Code cannot be blank"
        )
        args = parser.parse_args()
        code = args["code"]

        # 向微信服务器发送请求以获取访问令牌和用户信息 小程序 js_code  公众号 code
        wechat_params = {
            "appid": wxConfig["appid"],
            "secret": wxConfig["secret"],
            "js_code": code,
            "grant_type": wxConfig["grant_type"],
        }
        wechat_response = requests.get(wxConfig["url"], params=wechat_params)
        wechat_data = wechat_response.json()
        print(111, code, wechat_data)

        # 在这里处理微信服务器返回的数据，包括访问令牌和用户信息
        session_key = wechat_data.get("session_key")
        openid = wechat_data.get("openid")
        users_collection = db.users

        user = users_collection.find_one({"user_id": openid})

        # if not exist in database,  insert into database otherwise update database
        if not user:
            # 用户不存在，创建新用户
            new_user_id = users_collection.insert_one(
                {
                    "user_id": openid,
                    "points": 5,
                    "is_check": False,
                    # 其他需要的字段
                }
            ).inserted_id
            user = users_collection.find_one({"_id": new_user_id})
            response_data = {
                "session_key": session_key,
                "user": {
                    "user_id": openid,
                    "points": 5,
                    "is_check": False,
                },
            }
        else:
            # 用户存在，更新用户信息
            users_collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "last_check_date": datetime.combine(
                            date.today(), datetime.min.time()
                        )
                    }
                },
            )
            user = users_collection.find_one({"_id": user["_id"]})
            response_data = {
                "session_key": session_key,
                "user": {
                    "user_id": openid,
                    "points": user["points"],
                    "is_check": user["is_check"],
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
            return {"error": str(e)}, 400

        if user:
            # 将MongoDB对象转换为JSON
            user_json = json.loads(dumps(user))
            return user_json, 200
        else:
            return {"message": "User not found"}, 404
