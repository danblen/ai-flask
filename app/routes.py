# # routes.py
from app import app
from flask_restful import Api
from app.resources.user import User,WechatLogin
from app.resources.images import Images
api = Api(app)


api.add_resource(User, '/user/<string:user_id>')
api.add_resource(WechatLogin, '/wechat_login')
api.add_resource(Images, '/images')