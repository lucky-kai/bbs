#!/usr/bin/env python3
import time

from flask import Flask

import secret
import config
from models.base_model import db

from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.board import main as board_routes
from routes.message import main as mail_routes
from routes.reset import main as reset_routes
from routes.setting import main as setting_routes
from utils import log


def count(input):
    log('count using jinja filter')
    return len(input)


def format(t):
    if t < 60:
        s = '最近'
        t = ''
    elif t >= 60:
        s = '分钟前'
        t = t // 60
        if t > 60:
            s = '小时前'
            t = t // 60
            if t > 24:
                s = '天前'
                t = t // 24
                if t > 30:
                    s ='个月前'
                    t = t // 30
                    if t > 12:
                        s = '年前'
                        t = t // 12
    result = str(t) + s
    return result


def format_time(unix_timestamp):
    # enum Year():
    #     2013
    #     13
    # f = Year.2013
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def register_routes(app):
    """
    在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
    蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
    用法如下
    """
    # 注册蓝图
    # 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(board_routes, url_prefix='/board')
    app.register_blueprint(mail_routes, url_prefix='/message')
    app.register_blueprint(reset_routes, url_prefix='/reset')
    app.register_blueprint(setting_routes, url_prefix='/setting')

    app.template_filter()(count)
    app.template_filter()(format_time)
    app.template_filter()(format)


def configured_app():
    # web framework
    # web application
    # __main__
    app = Flask(__name__)
    # 设置 secret_key 来使用 flask 自带的 session
    # 这个字符串随便你设置什么内容都可以
    app.secret_key = secret.secret_key
    uri = 'mysql+pymysql://root:{}@localhost/web21?charset=utf8mb4'.format(
        secret.database_password
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    register_routes(app)
    return app
