from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.user import User
from models.message import Messages
from routes import new_reset_token,  reset_required
from routes import current_user

from utils import log

main = Blueprint('reset', __name__)

# data = {}


@main.route('/forget')
def forget():
    log("@main.route('/forget')")
    u = current_user()
    return render_template("forget.html", user=u)


@main.route('/send', methods=["POST"])
def reset_password_send():
    form = request.form.to_dict()
    log('reset_password_send form, request.url', form, request.url)
    s = request.url.split('/send')[0]
    log('reset_password_send url', s)
    u = User.one(username=form['username'])
    if u is None:
        return redirect(url_for('index.index'))
    else:
        # 存 id 和 token 对应关系
        # token = str(uuid.uuid4())
        # data[token] = u.id

        token = new_reset_token(u)
        log('reset_password_send() new_reset_token(u) token ', token)
        # reset_link = '{}/view?username={}&token={}'.format(s, u.username, token)
        reset_link = 'https://luckyk.club//reset/view?username={}&token={}'.format(u.username, token)

        content = '你好，{}:\n点击此链接重置密码：{}'.format(
            u.username,
            reset_link,
        )

        Messages.send(
            title='重置密码',
            content=content,
            sender_id=u.id,
            receiver_id=u.id,
        )

        return "邮件已经发送, 请检查你的收件箱(注意很可能在垃圾箱中)"


@main.route('/view')
@reset_required
def reset_password_view():
    query = request.query_string
    if query is not None:
        log('reset_password_view', query, type(query))
        encoding = "utf-8"
        query = str(query, encoding)
        log('reset_password_view', query, type(query))
        query = query.split('=')[1]
        query = query.split('&')[0]
        return render_template('reset.html', username=query)
    else:
        return redirect(url_for('index.index'))


@main.route('/update', methods=["POST"])
def reset_password_update():
    form = request.form
    log('表单信息', form)
    log('用户名, 密码', form['username'], form['password'])
    name = form['username']
    u = User.one(username=name)
    new_password = User.salted_password(form['password'])
    u.update(id=u.id, password=new_password)
    return redirect(url_for('index.index'))