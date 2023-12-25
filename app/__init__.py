from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os, re
from flask_restful import Api
from app.resources.user import User,WechatLogin
from app.resources.images import Images
from pymongo import MongoClient

app = Flask(__name__)


# MongoDB 连接配置
# app.config["MONGO_URI"] = "mongodb://localhost:27017/myapp"

# # 创建 MongoDB 客户端实例
# mongo = MongoClient(app.config["MONGO_URI"])

# # 选择数据库
# db = mongo.BackendDB





from app import routes
