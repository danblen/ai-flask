from flask import Flask, jsonify, request
from flask_restful import Api, Resource,reqparse
import os

static_directory = "/home/ubuntu/static/"

class UserImages(Resource):
    def get(self):
        target_directory = os.path.join(static_directory, "allImages")
        albums_directory = os.path.join(target_directory, "albums")
        tags_directory = os.path.join(target_directory, "tags")

        parser = reqparse.RequestParser()
        parser.add_argument(
            "user_id", required=True, type=str, help="user_id cannot be blank"
        )
        args = parser.parse_args()
        user_id = args["user_id"]
        
        if os.path.exists(albums_directory) and os.path.isdir(albums_directory):
            
        else:
            return {"error": "Albums directory not found"}, 404

    def post(self):
        # POST请求处理逻辑
        pass
