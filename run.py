from app import app
import os


def startup_tasks():
    # 在这里执行启动任务
    # 例如：检查环境变量、初始化数据库、运行迁移脚本等
    print("Performing startup tasks...")

if __name__ == '__main__':
    # 设置环境变量（仅适用于开发环境）
    os.environ['FLASK_ENV'] = 'development'

    startup_tasks()
    # app.run(host="0.0.0.0", port=8080, debug=True)