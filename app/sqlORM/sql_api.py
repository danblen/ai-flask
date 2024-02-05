from .database import engine
from .database import SessionLocal
from .sql_model import UserSqlData, UserInfo, Base
from sqlalchemy.orm import Session, attributes
from sqlalchemy.orm import class_mapper
from sqlalchemy import delete, or_, func
from .sql_model import PhotoImage
from PIL import Image
import os
import re
import base64
import json
import uuid
from flask_restful import Resource, reqparse
import time
import datetime
from datetime import datetime
from flask import Flask, request,jsonify
import requests

project_root = "/home/ubuntu/code/ai-flask"

Base.metadata.create_all(bind=engine)


def is_base64(s):
    if not isinstance(s, str):
        return False
    pattern = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$"
    return re.fullmatch(pattern, s) is not None


def is_base64_data_uri(s):
    # 检查字符串是否以 "data:image/" 开头
    if not isinstance(s, str) or not s.startswith("data:image/"):
        return False, s  # 保持原始的 s 不变

    # 检查 "base64," 是否存在
    if "base64," in s:
        # 提取 Base64 部分
        s = s.split("base64,")[1]
        # 正则表达式用来匹配 base64 编码的模式
        pattern = "^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$"
        # 检查 Base64 部分是否匹配模式
        is_valid_base64 = re.fullmatch(pattern, s) is not None
        return is_valid_base64, s
    else:
        return False, s  # 保持原始的 s 不变

def serialize_query_result(query_result, orm_class):
    serialized_result = []
    for item in query_result:
        item_dict = {}
        for column in class_mapper(orm_class).columns:
            if isinstance(getattr(item, column.key), datetime):
                item_dict[column.key] = getattr(item, column.key).strftime('%Y-%m-%d %H:%M:%S')
            else:
                item_dict[column.key] = getattr(item, column.key)
        serialized_result.append(item_dict)
    return serialized_result

def save_image_to_sql(request):
    db = SessionLocal()
    try:
        print("save image to sql 获取数据库信息：", request.get("request_id"))
        # print("save image to sql 获取数据库信息：", request.get("result"))

        records = (
            db.query(UserSqlData)
            .filter(UserSqlData.request_id == request.get("request_id"))
            .all()
        )
        records_user_info = (
            db.query(UserInfo).filter(UserInfo.user_id == request.get("user_id")).all()
        )
        image_list = request.get("result").get("images")

        # 遍历图像列表并保存每个图像
        if records:
            for idx, image_data_base64 in enumerate(image_list):
                images_dir = os.path.join(project_root, "sd_make_images/output")
                images_dir = os.path.join(images_dir, request.get("user_id"))
                images_dir = os.path.join(images_dir, datetime.now().strftime("%Y%m%d"))
                os.makedirs(images_dir, exist_ok=True)

                image_data = base64.b64decode(image_data_base64)
                for record in records:
                    img_filename = f"image_{record.user_id}_{record.request_id}_inx_{idx}.jpg"  # 使用 record
                    full_img_path = os.path.join(images_dir, img_filename)  # 生成完整的文件路径
                    with open(full_img_path, "wb") as img_file:
                        img_file.write(image_data)

                    record.output_image_path = full_img_path
                    record.request_status = request.get("status")
                    record.befor_process_time = request.get("befor_process_time")
                    record.process_time = request.get("process_time")
                    if records_user_info:
                        for record_user in records_user_info:
                            record_user.points = record_user.points - 1
                            if record_user.points < 0:
                                record_user.points = 0
                            # print("用户积分:", record_user.finished_works)
                            # record_user.finished_works.append(record.output_image_path)
                            # record_user.pending_works  = record_user.pending_works - 1
                # 提交更新到数据库
                db.commit()
                print("输出图像成功")
        else:
            print("未找到匹配的记录")
    finally:
        db.close()


# def update_request_status_sql(res):
#     db = SessionLocal()
#     try:
#         print("update_to_sql 获取数据库信息：", res.get("request_id"))
#         records = db.query(UserSqlData).filter(UserSqlData.request_id == res.get("request_id")).all()
#         if records:
#             for record in records:
#                 record.request_status = res.get("status")
#                 record.befor_process_time = res.get("befor_process_time")
#             # 提交更新到数据库
#             db.commit()
#         else:
#             print("未找到匹配的记录")
#     finally:
#         db.close()


def process_data(item, user_id, save_directory, image_paths, json_data, key=None):
    if isinstance(item, dict):
        for key, value in item.items():
            process_data(value, user_id, save_directory, image_paths, json_data, key)
    elif isinstance(item, list):
        json_list = []
        for element in item:
            is_valid, base64_data = is_base64_data_uri(element)
            if isinstance(element, str) and is_valid and len(element) > 1000:
                print(element[:10])
                print(element[-10:])
                img_data = base64.b64decode(base64_data)
                img_filename = f"{user_id}_image_{key if key else 0}_{len(element)}.jpg"
                full_img_path = os.path.join(save_directory, img_filename)  # 生成完整的文件路径
                with open(full_img_path, "wb") as img_file:
                    img_file.write(img_data)
                image_paths.append(full_img_path)
            else:
                #     process_data(element, user_id, save_directory, image_paths, list_item)
                json_list.append(element)
        if key:
            json_data[key] = json_list
        else:
            print("list none key")
        # else:
        #     json_data.append(json_list)
    else:
        is_valid, base64_data = is_base64_data_uri(item)
        if isinstance(item, str) and is_valid and len(item) > 1000:
            print(item[:10])
            print(item[-10:])
            img_data = base64.b64decode(item)
            img_filename = f"{user_id}_image_{key if key else 0}_{len(item)}.jpg"
            full_img_path = os.path.join(save_directory, img_filename)  # 生成完整的文件路径
            with open(full_img_path, "wb") as img_file:
                img_file.write(img_data)
            image_paths.append(full_img_path)
        else:
            if key:
                # print("save dict:", key, item)
                json_data[key] = item
            else:
                print("no key str")
                # json_data.append(item)


def forward_to_gpu(data, api_path):
    gpu_server_url = f"http://lyg.blockelite.cn:22164{api_path}"  # 构建访问接口的完整 URL

    print("gpu_server_url", gpu_server_url)
    response = requests.post(gpu_server_url, json=data, verify=False)

    # 获取 GPU 服务器的响应并返回
    if response.status_code == 201:
        return response.json()
    else:
        return {"error": "Unable to forward data to GPU"}, 404


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_user_info_sql(args, request_id):
    db = SessionLocal()
    try:
        user_id = args.get("user_id")
        if user_id is None:
            print("can not find user_id")
            db.close()
            return None
        print("user_id:", user_id)
        images_dir = os.path.join(project_root, "sd_make_images")
        images_dir = os.path.join(images_dir, datetime.now().strftime("%Y%m%d"))
        os.makedirs(images_dir, exist_ok=True)

        all_save_image_path = []
        processed_json_data = {}
        process_data(
            args, user_id, images_dir, all_save_image_path, processed_json_data, None
        )

        print("保存的图片路径：", all_save_image_path)
        json_string = json.dumps(processed_json_data)
        # print(json_string)
        # 处理数据库操作
        print("保存用户信息：", user_id, request_id)
        db_task = UserSqlData(
            user_id=user_id,
            image_type="img2img",
            request_id=request_id,
            request_status="pending",
            main_image_path=all_save_image_path[0] if all_save_image_path else None,
            roop_image_path=all_save_image_path[1]
            if len(all_save_image_path) > 1
            else None,
            img2imgreq_data=json_string,
        )

        records_user_info = db.query(UserInfo).filter(UserInfo.user_id == user_id).all()
        if not records_user_info:
            for record_user in records_user_info:
                record_user.pending_works = record_user.pending_works + 1
        db.add(db_task)
        db.commit()
        if db_task.user_id:
            print("保存成功")
        else:
            print("保存失败，没有生成 ID")

    except Exception as e:
        # 处理数据库查询错误
        print("查询数据时发生错误：", str(e))
        raise e
        db.close()
        return None


def find_images_in_directory(directory, db: Session):
    """遍历指定目录，查找所有图片文件。"""
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                try:
                    img_path = os.path.join(root, file)
                    existing_image = (
                        db.query(PhotoImage).filter(PhotoImage.path == img_path).first()
                    )
                    with Image.open(img_path) as img:
                        width, height = img.size
                    file_size = os.path.getsize(img_path) // 1000
                    if (
                        existing_image
                        and existing_image.width == width
                        and existing_image.height == height
                        and existing_image.file_size == file_size
                    ):
                        pass
                    else:
                        db_task = PhotoImage(
                            path=img_path,
                            file_size=file_size,
                            width=width,
                            height=height,
                        )
                        db.add(db_task)
                except IOError:
                    print(f"无法打开或读取文件：{img_path}")


def query_sql_data_by_dict(query: dict):
    db = SessionLocal()
    try:
        # 构建查询条件
        filters = []
        for key, value in query.items():
            filters.append(getattr(UserSqlData, key) == value)

        # 执行查询
        query_result = db.query(UserSqlData).filter(*filters).all()

        if not query_result:
            print("当前用户没有作品", query_result)
            db.close()
            return None

        serialized_result = serialize_query_result(query_result, UserSqlData)

        db.close()
        return serialized_result
    except Exception as e:
        # 处理数据库查询错误
        print("查询数据时发生错误：", str(e))
        db.close()
        raise(e)
        return None


def query_photo_image_sql_data_by_dict(query: dict):
    db = SessionLocal()
    try:
        # 构建查询条件
        filters = []
        for key, value in query.items():
            filters.append(getattr(PhotoImage, key) == value)

        # 执行查询
        query_result = db.query(PhotoImage).filter(*filters).all()

        if not query_result:
            print("没有找到数据", query_result)
            db.close()
            return None

        serialized_result = serialize_query_result(query_result, PhotoImage)

        db.close()
        return serialized_result
    except Exception as e:
        print("查询数据时发生错误：", str(e))
        db.close()
        return None


def queue_process_api(args):
    start_time = time.time()
    api_path = "/sdapi/v1/queue-process"  # 指定要访问的接口路径
    ret = forward_to_gpu(args, api_path)  # 转发前端请求，向 GPU 发送请求
    print("queue_process_api forward_to_gpu:", ret)
    if "error" in ret:
        return {
            "error_info": ret,
            "type": "img2img",
        }
    request_id = ret.get("request_id")
    print("request_id:", request_id)
    update_user_info_sql(args, request_id)
    elapsed_time = time.time() - start_time
    print("queue_process_api handle time:", elapsed_time)
    return {
        "request_id": request_id,
        "status": "pending",
        "type": "img2img",
    }


def queue_query_result(query: dict):
    response = forward_to_gpu(query, "/sdapi/v1/queue-query-result")
    if response.get("status") == "finishing":
        save_image_to_sql(response)
    return response

def delete_all_images_by_user_id(query: dict):
    db = SessionLocal()
    try:
        user_id = query.get("user_id")
        # 获取所有需要删除的文件路径
        records = db.query(UserSqlData).filter(UserSqlData.user_id == user_id).all()

        # 删除文件
        # for record in records:
        #     if record and record.output_image_path:
        #         file_path = record.output_image_path
        #         if os.path.exists(file_path):
        #             os.remove(file_path)
        #     if record and record.roop_image_path:
        #         file_path = record.roop_image_path
        #         if os.path.exists(file_path):
        #             os.remove(file_path)
        #     if record and record.main_image_path:
        #         file_path = record.main_image_path
        #         if os.path.exists(file_path):
        #             os.remove(file_path)

        # 执行删除操作
        delete_statement = delete(UserSqlData).where(UserSqlData.user_id == user_id)
        db.execute(delete_statement)
        db.commit()

        return {"message": f"用户 {user_id} 的所有图像已删除"}
    except Exception as e:
        print("删除数据时发生错误：", str(e))
        db.rollback()
        return None
    finally:
        db.close()

def delete_select_images_by_file_name(images_info: dict):
    if not images_info:
        return {"message": "没有要删除的数据。"}
    db = SessionLocal()
    try:
        for image_info in images_info:
            request_id = image_info.get("request_id")
            if request_id:
                # 查询数据库获取文件路径
                record = db.query(UserSqlData).filter(UserSqlData.request_id == request_id).first()
                # 删除文件
                # if record and record.output_image_path:
                #     file_path = record.output_image_path
                #     if os.path.exists(file_path):
                #         os.remove(file_path)
                # if record and record.roop_image_path:
                #     file_path = record.roop_image_path
                #     if os.path.exists(file_path):
                #         os.remove(file_path)
                # if record and record.main_image_path:
                #     file_path = record.main_image_path
                #     if os.path.exists(file_path):
                #         os.remove(file_path)
                # 删除数据库记录
                db.query(UserSqlData).filter(UserSqlData.request_id == request_id).delete()

        db.commit()

        db.close()
        return {"message": f" 选中图像已删除"}
    except Exception as e:
        print("删除数据时发生错误：", str(e))
        db.rollback()
        return None
    finally:
        db.close()

def update_user_process_info_by_dict(data: dict):
    db = SessionLocal()
    try:
        request_id = data.get("request_id")

        records = db.query(UserSqlData).filter(UserSqlData.request_id == request_id).all()
        if records:
            for record in records:
                for key, value in data.items():
                    # 检查数据库模型中是否存在与data中键对应的属性
                    if hasattr(record, key):
                        setattr(record, key, value)

            db.commit()
            return {"success": "UpdateUserProcessInfo"}, 200
        else:
            print(f"No records found for request_id: {request_id}")
            return {"success": "No records found for request_id"}, 200
    except Exception as e:
        print("update_user_process_info_by_dict 更新数据时发生错误:", str(e))
        return {"error": "Exception error" + str(e)}, 500
    finally:
        db.close()
# def query_finished_works(url: str):
#     db = SessionLocal()
#     try:
#         query_result = db.query(UserInfo).filter(UserInfo.finished_works.contains([url])).all()

#         if not query_result:
#             print("没有找到数据", query_result)
#             db.close()
#             return None

#         db.close()
#         return query_result
#     except Exception as e:
#         print("查询数据时发生错误：", str(e))
#         db.close()
#         return None

# class QueryUserFinishedWorksAPI(Resource):
#     def post(self):
#         data = request.json
#         print("QueryUserFinishedWorksAPI", data)
#         return query_finished_works(data)

class QueueProcessAPI(Resource):
    def post(self):
        data = request.json
        return queue_process_api(data)


class QueryResultAPI(Resource):
    def post(self):
        data = request.json
        print("QueryResultAPI", data)
        return queue_query_result(data)


class QueryUserPcocessDataAPI(Resource):
    def post(self):
        data = request.json
        return query_sql_data_by_dict(data)

class QueryPhotoImagesAPI(Resource):
    def post(self):
        data = request.json
        print("QueryPhotoImagesAPI", data)
        return query_photo_image_sql_data_by_dict(data)

class DeleteAllImages(Resource):
    def post(self):
        data = request.json
        print("DeleteAllImages",data)
        delete_all_images_by_user_id(data)
        return {"suceess": "DeleteAllImages"}, 200

class DeleteSelectImages(Resource):
    def post(self):
        data = request.json
        print("DeleteSelectImages",data)
        delete_select_images_by_file_name(data)
        return {"suceess": "DeleteAllImages"}, 200

class UpdateUserProcessInfo(Resource):
    def post(self):
        data = request.json
        return update_user_process_info_by_dict(data)