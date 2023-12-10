# # routes.py
from app import app
from flask_restful import Api
from app.resources.user import User
from app.resources.images import Images
from app.sqlORM.sql_api import QueueProcessAPI, QueryResultAPI
from app.sqlORM.sql_api import QueryUserDataAPI, QueryPhotoImagesAPI
from app.sqlORM.user_api import WechatLogin

api = Api(app)

api.add_resource(User, "/user/<string:user_id>")
api.add_resource(WechatLogin, "/wechat_login")
# api.add_resource(WechatLogin, '/wechat_login')
api.add_resource(Images, "/images")
api.add_resource(QueueProcessAPI, "/queue-process")
api.add_resource(QueryResultAPI, "/query-result")
api.add_resource(QueryUserDataAPI, "/query-user-data")
api.add_resource(QueryPhotoImagesAPI, "/query-photo-images")
