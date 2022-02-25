from functools import wraps
from flask import Markup, flash, url_for, redirect
from flask_login import current_user


def conform_required(func):
    @wraps(func)
    def decorated_function(*args,**kwargs):
        if not current_user.confirmed:
            message = Markup(
                '请确认你的账户,是否收到邮件?'
                '<a class="alert-link" href="%s"> 重新发送验证邮件 </a>' %
                url_for('auth.resend_confirm_email')
            )
            flash(message, 'warning')
            redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_function
