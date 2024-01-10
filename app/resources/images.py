from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import os

static_directory = "/home/ubuntu/code/ai-flask/static/"

class GetAllImages(Resource):
    def get(self):
        target_directory = os.path.join(static_directory, "allImages")
        albums_directory = os.path.join(target_directory, "albums")
        tags_directory = os.path.join(target_directory, "tags")

        if os.path.exists(albums_directory) and os.path.isdir(albums_directory):
            try:
                albums = {}
                for person in os.listdir(albums_directory):
                    person_path = os.path.join(albums_directory, person)
                    if os.path.isdir(person_path):
                        person_dict = {"index": "", "urls": []}
                        for category in os.listdir(person_path):
                            category_path = os.path.join(person_path, category)

                            if os.path.isdir(category_path):
                                for image in os.listdir(category_path):
                                    if image.lower().endswith(
                                        (".png", ".jpg", ".jpeg", ".gif", ".bmp")
                                    ):
                                        image_path = os.path.join(
                                            "https://facei.top/static/allImages/albums",
                                            person,
                                            category,
                                            image,
                                        )
                                        if category == "index":
                                            person_dict["index"] = image_path
                                        elif category == "urls":
                                            person_dict["urls"].append(image_path)
                        albums[person] = person_dict
                tags_image = {}
                for tag in os.listdir(tags_directory):
                    tag_path = os.path.join(tags_directory, tag)
                    if os.path.isdir(tag_path):
                        tag_images = []
                        if os.path.isdir(tag_path):
                            for image in os.listdir(tag_path):
                                if image.lower().endswith(
                                    (".png", ".jpg", ".jpeg", ".gif", ".bmp")
                                ):
                                    image_path = os.path.join(
                                        "https://facei.top/static/allImages/tags",
                                        tag,
                                        image,
                                    )
                                    tag_images.append(image_path)
                        tags_image[tag] = tag_images
                        
                banner_directory = os.path.join(target_directory, "banner")
                banners=[]
                for banner in os.listdir(banner_directory):
                    # path = os.path.join(tags_directory, banner)
                    image_path = os.path.join(
                                        "https://facei.top/static/allImages/banner",
                                        banner,
                                    )
                    banners.append(image_path)
                return jsonify({
                    "albums": albums, "tags_image": tags_image,'banners':banners})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return {"error": "Albums directory not found"}, 404

    def post(self):
        # POST请求处理逻辑
        pass
