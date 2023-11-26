from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os, re
from flask_restful import Api
from app.resources.user import User,WechatLogin
from app.resources.images import Images

app = Flask(__name__)
api = Api(app)

api.add_resource(User, '/user/<int:user_id>')
api.add_resource(WechatLogin, '/wechat_login')
api.add_resource(Images, '/images')


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080, debug=True)


from app import routes
