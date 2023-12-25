from app import app
import os
from app.sqlORM.database import SessionLocal
from app.sqlORM.sql_model import UserSqlData
from app.sqlORM.sql_api import find_images_in_directory


def startup_tasks():
    db = SessionLocal()
    try:
        # 查询所有 status 为 "pending或processing" 的记录
        pending_and_processing_records = (
            db.query(UserSqlData)
            .filter(UserSqlData.request_status.in_(["pending", "processing"]))
            .all()
        )

        for record in pending_and_processing_records:
            db.delete(record)

        find_images_in_directory("/home/ubuntu/static/images", db)

        # 提交更改
        db.commit()
    except Exception as e:
        # 处理数据库操作中的错误
        db.rollback()
        print("清空数据时发生错误：", str(e))
    finally:
        # 关闭数据库会话
        db.close()
    # 在这里执行启动任务
    # 例如：检查环境变量、初始化数据库、运行迁移脚本等
    print("Performing startup tasks...")


if __name__ == "__main__":
    # 设置环境变量（仅适用于开发环境）
    os.environ["FLASK_ENV"] = "development"

    startup_tasks()
    app.run(host="0.0.0.0", port=8080, debug=True)