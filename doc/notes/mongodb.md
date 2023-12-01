sudo systemctl start mongod
sudo systemctl status mongod
db.version()
show dbs
use myapp

db.users.insert({ name: "张三", email: "zhangsan@example.com" })
db.image_index.insert({ image_id: "img123", description: "示例图片" })
db.createCollection("users")
db.createCollection("image_index")
