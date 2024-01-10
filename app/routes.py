# # routes.py
from app import app
from flask_restful import Api
# from app.resources.user import User
from app.resources.images import GetAllImages
from app.sqlORM.sql_api import QueueProcessAPI, QueryResultAPI
from app.sqlORM.sql_api import QueryUserPcocessDataAPI, QueryPhotoImagesAPI 
from app.sqlORM.sql_api import DeleteAllImages, DeleteSelectImages
from app.sqlORM.users import WechatLogin, Users

api = Api(app)

# api.add_resource(User, "/user/<string:user_id>")
api.add_resource(WechatLogin, "/wechat_login")
api.add_resource(GetAllImages, "/get-all-images")
api.add_resource(DeleteAllImages, "/delete-all-images")
api.add_resource(DeleteSelectImages, "/delete-select-images")
api.add_resource(QueueProcessAPI, "/queue-process")
api.add_resource(QueryResultAPI, "/query-result")
# api.add_resource(wechat_login, "/wechat_login")
api.add_resource(Users, "/users",endpoint='users')
api.add_resource(QueryUserPcocessDataAPI, "/query-user-process-data")
api.add_resource(QueryPhotoImagesAPI, "/query-photo-images")
