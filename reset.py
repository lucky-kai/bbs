from sqlalchemy import create_engine

import secret
from app import configured_app
from models.base_model import db
from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User


def reset_database():
    # 现在 mysql root 默认用 socket 来验证而不是密码
    url = 'mysql+pymysql://root:{}@localhost/?charset=utf8mb4'.format(
        secret.database_password
    )
    e = create_engine(url, echo=True)

    with e.connect() as c:
        c.execute('DROP DATABASE IF EXISTS web21')
        c.execute('CREATE DATABASE web21 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        c.execute('USE web21')

    db.metadata.create_all(bind=e)


def generate_fake_date():
    form = dict(
        username='lucky',
        password='1998',
        email='1215048219@qq.com'
    )
    u1 = User.register(form)

    form = dict(
        username='test',
        password='123',
        email='2576962124@qq.com'
    )
    u2 = User.register(form)

    # form = dict(
    #     title='全部'
    # )
    # Board.new(form)

    form = dict(
        title='编程'
    )
    Board.new(form)
    form = dict(
        title='音乐'
    )
    Board.new(form)
    form = dict(
        title='游戏'
    )
    Board.new(form)
    form = dict(
        title='动漫'
    )
    Board.new(form)
    form = dict(
        title='体育'
    )
    Board.new(form)
    form = dict(
        title='影视'
    )
    Board.new(form)
    with open('res/markdown_demo.md', encoding='utf8') as f:
        content = f.read()
    topic_form = dict(
        title='markdown demo',
        board_id=1,
        content=content,
    )
    for i in range(3):
        print('begin topic <{}>'.format(i))
        t = Topic.new(topic_form, u1.id)

        reply_form = dict(
            content='reply test',
            topic_id=t.id,
        )
        for j in range(3):
            Reply.new(reply_form, u2.id)

    create_topic('res/game_board_1.md', '哪些单机手机游戏让你玩两分钟就惊呼「太好玩了」？为什么？', 3, u1)
    create_topic('res/game_board_2.md', 'Steam 上有哪些必买游戏？', 3, u1)
    create_topic('res/game_board_3.md', '最让你震撼的游戏细节有哪些？', 3, u1)
    create_topic('res/code_board_3.md', '搞 Java 的年薪 40W 是什么水平？', 1, u1)
    create_topic('res/code_board_2.md', '如何系统地学习 C++ 语言？', 1, u1)
    create_topic('res/code_board_1.md', '编程零基础应当如何开始学习 Python？', 1, u2)
    create_topic('res/animation_board_1.md', '好看的动漫推荐', 4, u2)
    create_topic('res/animation_board_2.md', '《海贼王》空白的一百年到底发生什么？', 4, u2)
    create_topic('res/animation_board_3.md', '如何评价动画电影《哪吒之魔童降世》？', 4, u2)
    create_topic('res/sport_board_1.md', '科比为什么那么受欢迎？', 5, u2)
    create_topic('res/sport_board_2.md', '世界杯给你留下最深刻印象的瞬间是什么？', 5, u2)
    create_topic('res/music_board_1.md', '钢琴业余十级证书有什么用？', 2, u2)
    create_topic('res/movie_board_1.md', '《无间道》里有哪些值得深思的细节？', 6, u2)
    create_topic('res/movie_board_2.md', '有哪部电影让你受益良多？', 6, u2)


def create_topic(path, title, board_id, u):
    with open(path, encoding='utf8') as f:
        content = f.read()
    topic_form = dict(
        title=title,
        board_id=board_id,
        content=content,
    )
    Topic.new(topic_form, u.id)


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        reset_database()
        generate_fake_date()
