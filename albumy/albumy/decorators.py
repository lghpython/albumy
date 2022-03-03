from functools import wraps
from flask import Markup, flash, url_for, redirect, abort
from flask_login import current_user


def confirm_required(func):
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


def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args,**kwargs):
            """要求访问权限"""
            if not current_user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    """只对管理员开放"""
    return permission_required('ADMINISTER')(func)
