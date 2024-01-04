# models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    ARRAY,
    Text,
    DateTime,
    Float,
    func,
    Boolean,
)
from .database import Base
from sqlalchemy import event
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import pytz


class UserSqlData(Base):
    __tablename__ = "user_process_image_data"
    user_id = Column(Integer, index=True)
    main_image_path = Column(String)
    roop_image_path = Column(String)
    img2imgreq_data = Column(Text)  # 存储JSON格式的img2imgreq数据
    output_image_path = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(pytz.timezone("Asia/Shanghai")),
    )
    befor_process_time = Column(Float)
    process_time = Column(Float)
    image_type = Column(String)
    request_id = Column(String, unique=True, primary_key=True)
    request_status = Column(String, default="no-data")


class UserInfo(Base):
    __tablename__ = "user_info"
    user_id = Column(String, primary_key=True, index=True)
    points = Column(
        Integer,
        default=0,
    )
    history_operations = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')))
    last_login_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')))
    # finished_works = Column(String, default="[]")  # 存放已完成作品的 URL，你也可以使用其他方式存储
    # pending_works = Column(String, default="[]")
    is_check = Column(String)


class PhotoImage(Base):
    __tablename__ = "image_sql"
    path = Column(String, unique=True, primary_key=True)
    upload_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(pytz.timezone("Asia/Shanghai")),
    )  # 上传日期
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(Integer)

    def __repr__(self):
        return f"Image(filename='{self.filename}', description='{self.description}', upload_date='{self.upload_date}')"
