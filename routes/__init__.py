import functools
import uuid
from functools import wraps

import redis
from flask import session, request, abort, redirect, url_for
import flask as f
from kombu.utils import json

from models.user import User
from utils import log


# def current_user():
#     if 'session_id' in request.cookies:
#         session_id = request.cookies['session_id']
#         s = Session.one_for_session_id(session_id=session_id)
#         key = 'session_id_{}'.format(session_id)
#         user_id = int(cache.get(key))
#         log('current_user key <{}> user_id <{}>'.format(key, user_id))
#         u = User.one(id=user_id)
#         return u
#     else:
#         return None

def current_user():
    log('current_user session', session)
    uid = session.get('user_id', '')
    u: User = User.one(id=uid)
    # type annotation
    # User u = User.one(id=uid)
    return u
    # if 'session_id' in request.cookies:
    #     session_id = request.cookies['session_id']
    #     key = 'session_id_{}'.format(session_id)
    #     user_id = int(cache.get(key))
    #     log('current_user key <{}> user_id <{}>'.format(key, user_id))
    #     u = User.one(id=user_id)
    #     return u
    # else:
    #     return None


def login_required(route_function):
    """
    这个函数看起来非常绕，所以你不懂也没关系
    就直接拿来复制粘贴就好了
    """

    @functools.wraps(route_function)
    def f():
        log('login_required')
        u = current_user()
        if u is None:
            log('游客用户')
            return redirect(url_for('index.index'))
        else:
            log('登录用户', route_function)
            return route_function()

    return f

# csrf_tokens = dict()


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        log('csrf_required start')
        token = request.args['token']
        u = current_user()

        # log('csrf_required before pop ', csrf_tokens)
        # log('当前用户', type(u))
        # log('if token in csrf_tokens and csrf_tokens[token] == u.id:', csrf_tokens[token], u.id, type(csrf_tokens[token]))
        # if token in csrf_tokens and csrf_tokens[token] == u.id:
        #     csrf_tokens.pop(token)
        #     log('csrf_required after pop', csrf_tokens)
        #     return f(*args, **kwargs)

        # 缓存中
        log('csrf_required before pop', cache)
        log('传来的 token', token)
        log('cache 存在cache.exists(token)', cache.exists(token), type(cache.exists(token)))
        log('cache.get(token) 缓存中的数据', int(cache.get(token)))
        if cache.exists(token) == 1 and int(cache.get(token)) == u.id:
            log('token 在缓存中 缓存', cache)
            cache.delete(token)
            log('csrf_required after delete', cache)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def reset_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        log('reset_required start')
        token = request.args['token']

        # log('csrf_required before pop', csrf_tokens)
        # if token in csrf_tokens:
        #     # csrf_tokens.pop(token)
        #     log('csrf_required after pop', csrf_tokens)
        #     return f(*args, **kwargs)

        # 缓存中
        log('csrf_required before pop', cache)
        log('传来的 token', token)
        log('cache 存在cache.exists(token)', cache.exists(token), type(cache.exists(token)))
        log('cache.get(token) 缓存中的数据', int(cache.get(token)))
        if cache.exists(token) == 1:
            log('token 在缓存中 缓存', cache)
        #   cache.delete(token)
            log('csrf_required after delete', cache)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    log('current_user', u)
    token = str(uuid.uuid4())

    # csrf_tokens[token] = u.id
    # log('存储结束', csrf_tokens)

    k = token
    v = u.id
    cache.set(k, v)

    return token


def new_reset_token(u):
    token = str(uuid.uuid4())

    # csrf_tokens[token] = u.id
    # log('存储结束', csrf_tokens)

    k = token
    v = u.id
    cache.set(k, v)

    return token


cache = redis.StrictRedis()
