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
from gevent import os
from werkzeug.datastructures import FileStorage

from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import current_user

from utils import log

main = Blueprint('setting', __name__)


@main.route('/')
def index():
    u = current_user()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template("setting.html",
                               user=u,
                               bid=-1
                               )


@main.route('/image/change', methods=["POST"])
def change_image():
    avatar_add()
    return redirect(url_for('.index'))


@main.route('/username/change', methods=["POST"])
def change_username():
    form = request.form.to_dict()
    log('change_username_setting form', form)
    u = current_user()
    u.update(u.id, username=form['name'])
    u.update(u.id, signature=form['signature'])
    u.save()
    return redirect(url_for('.index'))


@main.route('/password/change', methods=["POST"])
def change_password():
    form = request.form.to_dict()
    log('change_password_setting form', form)

    old_pass = form['old_pass']
    old_pass_salt = User.salted_password(old_pass)

    new_pass = form['new_pass']
    new_pass_salt = User.salted_password(new_pass)

    u = current_user()
    log('change_password_setting password', u.password)
    log('change_password_setting old_pass', old_pass_salt)

    # 密码加过盐 判断注意一下
    if u.password != old_pass_salt:
        log('输入旧密码不正确')
    else:
        log('旧密码正确')
        u.update(u.id, password=new_pass_salt)
        u.save()
    return redirect(url_for('.index'))


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    # file = request.files['avatar']
    # filename = file.filename
    # ../../root/.ssh/authorized_keys
    # images/../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    if suffix not in ['gif', 'jpg', 'jpeg', 'png']:
        abort(400)
        log('不接受的后缀, {}'.format(suffix))
    else:
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        path = os.path.join('images', filename)
        file.save(path)

        log('filename', filename)
        u = current_user()
        User.update(u.id, image='/images/{}'.format(filename))
        log("test before redirect(url_for('index.profile'))")
        return redirect(url_for('index.profile'))



