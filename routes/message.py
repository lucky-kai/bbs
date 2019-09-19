from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.message import Messages
main = Blueprint('mail', __name__)


@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    sender = current_user()
    receiver_id = int(form['receiver_id'])
    log('sender.id, receiver_id', sender.id, receiver_id)
    # 发邮件
    Messages.send(
        title=form['title'],
        content=form['content'],
        sender_id=sender.id,
        receiver_id=receiver_id
    )
    return redirect(url_for('.index'))


@main.route('/')
def index():
    u = current_user()
    log('当前用户', u)
    if u is not None:
        send = Messages.all(sender_id=u.id)
        received = Messages.all(receiver_id=u.id)

        t = render_template(
            'mail/index.html',
            send=send,
            received=received,
            user=u,
            bid=-1,
        )
        return t
    else:
        return redirect(url_for('index.index'))


@main.route('/view/<int:id>')
def view(id):
    message = Messages.one(id=id)
    u = current_user()
    # if u.id == mail.receiver_id or u.id == mail.sender_id:
    if u.id in [message.receiver_id, message.sender_id]:
        return render_template('mail/detail.html', message=message, user=u)
    else:
        return redirect(url_for('.index'))
