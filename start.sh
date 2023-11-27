#!/bin/bash

export FLASK_APP=run.py
export FLASK_ENV=development

# 在启动之前执行的其他命令
# 例如：初始化数据库、运行迁移脚本等

flask run --host=0.0.0.0 --port=8080 --debug
