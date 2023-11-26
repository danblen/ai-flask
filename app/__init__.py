from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os, re

app = Flask(__name__)
static_directory = "/home/ubuntu/static/"
app.env = "development"


def safe_path(path):
    # 只允许字母数字字符、斜杠和下划线
    return re.sub(r"[^a-zA-Z0-9/_]", "", path)


@app.route("/list-files", methods=["GET", "POST"])
def list_files():
    sub_path = request.args.get("path", "")  # 获取URL参数中的子路径
    # secure_sub_path = safe_path(sub_path)  # 确保路径安全
    target_directory = os.path.join(static_directory, sub_path)
    # print(target_directory, sub_path)
    if os.path.exists(target_directory) and os.path.isdir(target_directory):
        try:
            files = os.listdir(target_directory)
            return jsonify(files)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid path"}), 400

    # @app.route("/get_all_images", methods=["GET", "POST"])
    # def get_all_images():
    #     sub_path = request.args.get("path", "")  # 获取URL参数中的子路径
    #     # secure_sub_path = safe_path(sub_path)  # 确保路径安全
    #     target_directory = os.path.join(static_directory, "allImages")
    #     albums_directory = os.path.join(target_directory, "albums")
    #     tags_directory = os.path.join(target_directory, "tags")
    #     print(target_directory, sub_path)
    #     albums = {}
    #     if os.path.exists(target_directory) and os.path.isdir(target_directory):
    #         try:
    #             albums_directory = os.listdir(albums_directory)
    #             alubms=albums_directory
    #             for album_directory in alubms_directory:
    #                 alubms[].push(
    #                     os.listdir(os.path.join(albums_directory, album_directory))
    #                 )

    #             tags = os.listdir(tags_directory)

    #             return jsonify(files)
    #         except Exception as e:
    #             return jsonify({"error": str(e)}), 500
    #     else:
    #         return jsonify({"error": "Invalid path"}), 400


@app.route("/get_images", methods=["GET", "POST"])
def get_images():
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
                                    print(1212, image_path)
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
                                print(1212, image)
                                tag_images.append(image_path)
                    tags_image[tag] = tag_images
            return jsonify({"albums": albums, "tags_image": tags_image})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Albums directory not found"}), 404


@app.route("/wechat_login", methods=[ "POST"])
def wechat_login(request):
    if request.method == "POST":
        # 这样拿不到code
        # code = request.POST.get('code')
        request_data = request.body.decode("utf-8")
        data = json.loads(request_data)
        code = data.get("code")
        # 向微信服务器发送请求以获取访问令牌和用户信息 小程序 js_code  公众号 code
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

        return JsonResponse(response_data)

    return JsonResponse({"error": "Invalid request method"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)


from app import routes
