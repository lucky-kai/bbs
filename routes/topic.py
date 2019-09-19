import time

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.reply import Reply
from routes import *

from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)


@main.route("/")
@login_required
def index():
    visitor = current_user()
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    bs = Board.all()
    log('index Board.all()', bs)
    log('index Topic.all()', ms)
    ms = sorted(ms, key=lambda m: m.created_time, reverse=True)
    topics = sorted(ms, key=lambda m: m.views, reverse=True)

    for m in ms:
        m.updated_time = int(time.time())
    hot_topic = []
    i = 0
    for ht in topics:
        if i < 5:
            hot_topic.append(ht)
        i += 1
    log("ms<{}>, hot_topic<{}>".format(ms, hot_topic))
    return render_template("topic/index.html",
                           ms=ms,
                           bs=bs,
                           bid=board_id,
                           user=visitor,
                           hot_topic=hot_topic,
                           )


@main.route('/<int:id>')
def detail(id):
    m = Topic.get(id)
    u = current_user()
    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html", topic=m, user=u)


@main.route("/delete")
@login_required
@csrf_required
def delete():
    id = int(request.args.get('id'))
    u: User = current_user()
    log('删除 topic 用户是', u, id)

    topic: Topic = Topic.one(id=id)
    for reply in topic.replies():
        reply.delete(id=reply.id)

    Topic.delete(id)
    return redirect(url_for('topic.user_index', username=u.username))


@main.route("/new")
@login_required
def new():
    log('topic/new/request.args.get()', request.args.get('board_id'))
    board_id = int(request.args.get('board_id'))
    bs = Board.all()
    log('板块', bs)
    return render_template("topic/new.html", bs=bs, bid=board_id)


@main.route("/add", methods=["POST"])
@login_required
def add():
    form = request.form.to_dict()
    log('表单信息', form)
    u = current_user()
    m = Topic.add(form, user_id=u.id)

    # 添加话题的时候
    # 用当前添加时间做为创建时间
    m.created_time = int(time.time())
    m.save()
    # log('all tokens add', csrf_tokens)
    return redirect(url_for('.detail', id=m.id))


@main.route("/user/<string:username>")
# @login_required
def user_index(username):
    c_user = current_user()
    if c_user is None:
        log('游客用户')
        return redirect(url_for('index.index'))
    else:
        author = User.one(username=username)
        current_user_topics = Topic.all(user_id=author.id)
        log('查询此用户 topic', current_user_topics)
        current_time = int(time.time())

        # updated_time 当前用户的查看话题时 时间
        for r in current_user_topics:
            r.updated_time = current_time
            r.save()
        # 拿到所有回复的话题
        replies = Reply.all(user_id=author.id)
        log('查询此用户 replies', replies)

        replies_topics = []
        # 遍历 id 相同时 的所有
        for r in replies:
            r.updated_time = current_time
            r.save()
            topic = Topic.one(id=r.topic_id)
            replies_topics.append(topic)
            log('replies_topics<{}>,\n r.created_time<{}>, '.format(replies_topics, r))

        log('replies_topics xxx', replies_topics)
        log('current_user_topics xxx', current_user_topics)
        token = new_csrf_token()

        # 按照创建时间将 topics 逆序
        current_user_topics = sorted(current_user_topics, key=lambda m: m.created_time, reverse=True)
        if replies_topics is not None or replies_topics[0] is not None:
            replies_topics = sorted(replies_topics, key=lambda m: (m.updated_time-m.created_time), reverse=False)
        for r in replies_topics:
            log('话题回复', r)
        if c_user.username == username:
            log('当前用户是本人')
            return render_template("topic/user_index.html",
                                   token=token,
                                   user=author,
                                   current_user_topics=current_user_topics,
                                   replies_topics=replies_topics,
                                   bid=-1
                                   )
        else:
            log('当前用户非本人')
            return render_template("topic/other_user_index.html",
                                   user=c_user,
                                   author=author,
                                   current_user_topics=current_user_topics,
                                   replies_topics=replies_topics,
                                   bid=-1
                                   )


@main.route("/user/")
def user_error():
    return redirect(url_for('.index'))
