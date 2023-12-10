from flask_restful import Resource, reqparse
from user import db


def query_sql_data_by_dict(self, query: models.QueryData):
    try:
        # 构建查询条件
        filters = []
        for key, value in query.sql_query.items():
            filters.append(getattr(UserSqlData, key) == value)

        # 执行查询
        query_result = db.query(UserSqlData).filter(*filters).all()

        if not query_result:
            raise HTTPException(status_code=404, detail="User data not found")

        db.close()
        return query_result
    except Exception as e:
        # 处理数据库查询错误
        print("查询数据时发生错误：", str(e))
        db.close()
        return None


def find_documents(query):
    try:
        # 使用 find 方法查询文档
        result = collection.find(query)
        # 返回查询结果
        return list(result)  # 将 Cursor 对象转换为列表返回
    except Exception as e:
        print(f"Error finding documents: {e}")
        return None


def query_photo_image_sql_data_by_dict(self, query: models.QueryData):
    db = SessionLocal()
    try:
        # 构建查询条件
        filters = []
        for key, value in query.sql_query.items():
            filters.append(getattr(PhotoImage, key) == value)

        # 执行查询
        query_result = db.query(PhotoImage).filter(*filters).all()

        if not query_result:
            raise HTTPException(status_code=404, detail="User data not found")

        db.close()
        return query_result
    except Exception as e:
        print("查询数据时发生错误：", str(e))
        db.close()
        return None


async def queue_process_api(
    self,
    img2imgreq: models.StableDiffusionImg2ImgProcessingAPI,
    db: Session = Depends(get_db),
):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    temp_request = {
        "type": "img2img",
        "payload": img2imgreq,
        "status": "pending",
        "request_id": request_id,
        "user_id": img2imgreq.user_id,
        "enqueue_time": start_time,
    }
    ret = reqq.add_req_queue(self.request_queue, temp_request)
    if ret < 0:
        return {
            "request_id": request_id,
            "error_info": "retry error, queue full",
            "type": "img2img",
        }
    await update_user_info_sql(img2imgreq, request_id, db)
    elapsed_time = time.time() - start_time
    print("queue_process_api handle time:", elapsed_time)
    return {
        "request_id": request_id,
        "status": "pending",
        "type": "img2img",
    }


def queue_query_result(self, query: models.QueryData):
    return reqq.get_result(
        query.request_id, self.request_queue, self.monitor.ad_api_handle
    )


def get_user_data(self, query: models.QueryData):
    db = SessionLocal()
    try:
        print("获取数据库信息：", query.user_id, query.request_id)
        # 查询数据库中符合条件的记录
        records = (
            db.query(UserSqlData).filter(UserSqlData.user_id == query.user_id).all()
        )

        if not records:
            raise HTTPException(status_code=404, detail="User data not found")

        # 根据需求构造返回数据
        result = []
        for record in records:
            result.append(
                {
                    "user_id": record.user_id,
                    "main_image_path": record.main_image_path,
                    "roop_image_path": record.roop_image_path,
                    "img2imgreq_data": record.img2imgreq_data,
                }
            )
    finally:
        db.close()

    return {"data": result}


class ImagesProcess(Resource):
    def get(self):
        # 处理 GET 请求的逻辑
        pass

    def post(self):
        parser = reqparse.RequestParser()
        pass
