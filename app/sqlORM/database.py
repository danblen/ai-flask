# database.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
import pytz
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import sessionmaker
import atexit
from . import sql_model

SQLALCHEMY_DATABASE_URL = "sqlite:///./user-data.db"  # 或者其他数据库连接字符串

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 创建定时任务调度器
scheduler = BackgroundScheduler()

# 定义任务函数，用于定期检查并更新用户的 is_check 字段
def check_and_update_is_check():
    db = SessionLocal()
    try:
        # 查询所有用户
        users = db.query(sql_model.UserInfo).all()
        for user in users:
            now = datetime.now(pytz.timezone('Asia/Shanghai'))
            # 如果当前时间已经过凌晨，且 is_check 为 1，更新为 0
            if now.hour == 0 and now.minute == 0 and user.is_check == 1:
                user.is_check = 0
                print(f"User {user.user_id} checked in for today.")

        # 提交数据库事务
        db.commit()

    except Exception as e:
        print(f"Error in check_and_update_is_check: {str(e)}")
        db.rollback()

    finally:
        db.close()

# 添加定时任务，每天凌晨执行 check_and_update_is_check 函数
scheduler.add_job(check_and_update_is_check, trigger='cron', hour=0, minute=0)

# 启动定时任务调度器
scheduler.start()

# 在程序结束时关闭定时任务调度器
atexit.register(lambda: scheduler.shutdown())