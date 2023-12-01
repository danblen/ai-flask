服务器A上安装Nginx，用作反向代理和负载均衡器
服务器A负责接收外部的请求，然后根据配置的负载均衡策略将请求转发到服务器B或其他服务器上。服务器B上运行的可以是任何能够处理HTTP请求的应用，以下通过flask作为接收。

服务器A（中转）
- ip：175.178.153.125

1、配置代理：
~/：sudo nano /etc/nginx/sites-available/default
修改配置文件：
# 负载均衡：
upstream myapp {
        server 42.194.195.96:5000;
        server 42.194.195.96:5001;
        # 可以添加权重等其他设置
}

#反代理
server{
    server_name 42.194.195.96;

    location / {
            proxy_pass http://myapp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
    }
}
2、运行Nginx
~/：systemctl start nginx
3、修改配置文件重新生（可选）
sudo systemctl reload nginx
4、目标服务器B（ip：42.194.195.96）
通过flask监测5000端口请求：
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
也可以通过fastapi：
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World---------port:5000"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)


当用户访问服务器A（http://175.178.153.125/），即可得到服务器B的回应

[图片]
[图片]
