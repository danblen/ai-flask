from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.myapp

# 为所有用户添加points字段
# db.users.update_many({}, {"$set": {"points": 10}})
# db.users.update_many({}, {"$set": {"is_check": False}})
db.users.insert_one({"is_check": False})
# db.createUser(
#     {
#         user: "ubuntu",
#         pwd: "Zxc123456",
#         roles: [{role: "userAdminAnyDatabase", db: "myapp"}],
#     }
# )
