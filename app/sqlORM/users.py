from flask import jsonify, request
from flask_restful import Resource, reqparse
import requests
import json
from datetime import datetime, date
from bson.json_util import dumps
from bson.objectid import ObjectId
from config import read_config
from sqlalchemy.orm import Session
from .sql_model import UserInfo
from .database import SessionLocal
from app import app


# 读取配置文件
config_data = read_config()
wxConfig = {
    "appid": config_data["appId"],
    "secret": config_data["secret"],
    "url": "https://api.weixin.qq.com/sns/jscode2session",
    "grant_type": "authorization_code",
}

db = SessionLocal()

def serialize_query_result(result, model):
    if result:
        return {column.name: getattr(result, column.name) for column in model.__table__.columns}
    else:
        return {}
    
class Users(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            # parser.add_argument(
            #     "code", required=True, type=str, help="Code cannot be blank"
            # )
            query = parser.parse_args()

            # 查询用户信息
            result = db.query(UserInfo).filter_by(**query).first()

            # 判断查询结果
            if result:
                return jsonify({'code': 0, 'data': serialize_query_result(result, UserInfo)})
            else:
                # 如果查询结果为空，返回空字典或其他你认为合适的值
                return jsonify({'code': 400})
        except Exception as e:
            # 处理异常
            return jsonify({'code': 500, 'error': str(e)})


class WechatLogin(Resource):
    def post(self):
        # query = request.json
        # code=query.get('code')
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

        # 在这里处理微信服务器返回的数据，包括访问令牌和用户信息
        session_key = wechat_data.get("session_key")
        openid = wechat_data.get("openid")

        user = db.query(UserInfo).filter(UserInfo.user_id == openid).first()

        if not user:
            # 用户不存在，创建新用户
            default_user = UserInfo(
                user_id=openid,
                points=5,
                is_check="False",
                created_at=datetime.now(),
            )
            db.add(default_user)
            db.commit()
            # 获取刚刚创建的用户信息
            user = db.query(UserInfo).filter(UserInfo.user_id == openid).first()
            user_info = {
                "user_id": user.user_id,
                "points": user.points,
                "history_operations": user.history_operations,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at,
                "finished_works": user.finished_works,
                "pending_works": user.pending_works,
                "is_check": user.is_check,
            }
            response_data = {"code": 200, "session_key": session_key, "data": user_info}
        else:
            # 用户存在，更新用户信息
            user.last_login_at = datetime.now()  # 更新最后登录时间为当前时间
            db.commit()
            # 构建可以被序列化的用户信息字典
            user_info = {
                "user_id": user.user_id,
                "points": user.points,
                "history_operations": user.history_operations,
                "created_at": str(user.created_at),
                # "last_login_at": user.last_login_at,
                # "finished_works": user.finished_works,
                # "pending_works": user.pending_works,
                "is_check": user.is_check,
            }
            response_data = {
                "code": 200,
                "session_key": session_key,
                "data": user_info,
            }

        # 返回处理后的用户信息
        return response_data

class Works(Resource):
    def get(self):
        db = SessionLocal()
        parser = reqparse.RequestParser()
        parser.add_argument(
            "user_id", required=True, type=str, help="Code cannot be blank"
        )
        args = parser.parse_args()
        user_id = args["user_id"]


        user = db.query(UserInfo).filter(UserInfo.user_id == user_id).first()

        if not user:
            # 用户不存在，创建新用户
            default_user = UserInfo(
                user_id=openid,
                points=5,
                is_check="False",
                created_at=datetime.now(),
            )
            # 获取刚刚创建的用户信息
            user = db.query(UserInfo).filter(UserInfo.user_id == openid).first()
            user_info = {
                "user_id": user.user_id,
                "points": user.points,
                "history_operations": user.history_operations,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at,
                "finished_works": user.finished_works,
                "pending_works": user.pending_works,
                "is_check": user.is_check,
            }
            response_data = {"code": 200, works:{}}
        else:
            # 用户存在，更新用户信息
            user.last_login_at = datetime.now()  # 更新最后登录时间为当前时间
            db.commit()
            # 构建可以被序列化的用户信息字典
            user_info = {
                "user_id": user.user_id,
                "points": user.points,
                "history_operations": user.history_operations,
                "created_at": str(user.created_at),
                # "last_login_at": user.last_login_at,
                # "finished_works": user.finished_works,
                # "pending_works": user.pending_works,
                "is_check": user.is_check,
            }
            response_data = {
                "code": 200,
                "session_key": session_key,
                "data": user_info,
            }

        # 返回处理后的用户信息
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
