import hashlib

from sqlalchemy import Column, String, Text

import config
import secret
from models.base_model import SQLMixin, db


class User(SQLMixin, db.Model):
    __tablename__ = 'User'
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    image = Column(String(100), nullable=False, default='/images/3.jpg')
    email = Column(String(50), nullable=False, default=config.test_mail)
    signature = Column(String(50), nullable=False, default='这家伙很懒，什么个性签名都没有留下。')

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        salted = hashlib.sha256((password + salt).encode('ascii')).hexdigest()
        return salted

    @classmethod
    def register(cls, form):
        name = form.get('username', '')
        email = form.get('email', '')
        print('register', form)
        # if len(name) > 2 and User.one(username=name) is None:
        if is_right_name(name) and is_right_email(email):
            # 错误，只应该 commit 一次
            # u = User.new(form)
            # u.password = u.salted_password(pwd)
            # User.session.add(u)
            # User.session.commit()
            print('通过检查')
            form['password'] = User.salted_password(form['password'])
            User.email = email
            u = User.new(form)
            return u
        else:
            print('未通过检查')
            return None

    @classmethod
    def validate_login(cls, form):
        query = dict(
            username=form['username'],
            password=User.salted_password(form['password']),
        )
        print('validate_login', form, query)
        return User.one(**query)


def is_right_name(name):
    return len(name) > 2 and User.one(username=name) is None


def is_right_email(email):
    print('email', email)
    return '@' in email and '.com' == email[len(email) - 4:]
