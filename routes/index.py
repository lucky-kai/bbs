import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory,
)
from werkzeug.datastructures import FileStorage

from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import current_user

from utils import log

main = Blueprint('index', __name__)

"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""

import gevent
import time


@main.route("/")
def index():
    # t = threading.Thread()
    # t.start()
    # gevent.spawn()
    time.sleep(0.1)
    print('time type', time.sleep, gevent.sleep)
    u = current_user()
    return render_template("login.html", user=u)
    # return render_template("topic/index.html", user=u)


def created_topic(user_id):
    # O(n)
    ts = Topic.all(user_id=user_id)
    return ts
    #
    # k = 'created_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     ts = Topic.all(user_id=user_id)
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #     return ts


def replied_topic(user_id):
    # O(k)+O(m*n)
    rs = Reply.all(user_id=user_id)
    ts = []
    for r in rs:
        t = Topic.one(id=r.topic_id)
        ts.append(t)
    return ts
    #
    #     sql = """
    # select * from topic
    # join reply on reply.topic_id=topic.id
    # where reply.user_id=1
    # """
    # k = 'replied_topic_{}'.format(user_id)
    # if cache.exists(k):
    #     v = cache.get(k)
    #     ts = json.loads(v)
    #     return ts
    # else:
    #     # ts = Topic.select()
    #     #   .join(Reply, 'id', 'topic_id')
    #     #   .where(user_id=user_id)
    #     #   .all()
    #     rs = Reply.all(user_id=user_id)
    #     ts = []
    #     for r in rs:
    #         t = Topic.one(id=r.topic_id)
    #         ts.append(t)
    #
    #     v = json.dumps([t.json() for t in ts])
    #     cache.set(k, v)
    #
    #     return ts


@main.route('/profile')
def profile():
    print('running profile route')
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        created = created_topic(u.id)
        replied = replied_topic(u.id)
        return render_template(
            'profile.html',
            user=u,
            created=created,
            replied=replied
        )


@main.route('/user/<int:id>')
def user_detail(id):
    u = User.one(id=id)
    if u is None:
        abort(404)
    else:
        return render_template('profile.html', user=u)


@main.route('/signup')
def signup():
    return render_template("register.html")


@main.route('/signin')
def signin():
    return render_template("login.html")


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    log('request.form', request.form)
    form = form.to_dict()
    log('request.form form.to_dict()', form)
    u = User.validate_login(form)
    log('login user', u)
    if u is None:
        log('user is none', u)
        return redirect(url_for('.index'))
    else:
        # # session 中写入 user_id
        # session_id = str(uuid.uuid4())
        # key = 'session_id_{}'.format(session_id)
        # log('index login key <{}> user_id <{}>'.format(key, u.id))
        # cache.set(key, u.id)
        #
        # redirect_to_index = redirect(url_for('topic.index'))
        # response = current_app.make_response(redirect_to_index)
        # response.set_cookie('session_id', value=session_id)
        # # 转到 topic.index 页面
        # return response
        log('user is not none', u)
        session['user_id'] = u.id
        return redirect(url_for('topic.index'))


@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    # 用类函数来判断
    log('表单信息', form)
    u = User.register(form)
    log('该注册用户信息', u)
    # return redirect(url_for('.index', user=u))
    if u is None:
        return redirect(url_for('.signup'))
    else:
        return redirect(url_for('.signin'))


# 显示图片
@main.route('/images/<filename>')
def image(filename):
    # 不要直接拼接路由，不安全，比如
    # http://localhost:3000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    # if filename in os.listdir('images'):
    #     return
    log('文件名', filename)
    return send_from_directory('images', filename)


