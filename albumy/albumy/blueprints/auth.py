from flask import Blueprint, url_for, flash, redirect,render_template
from flask_login import login_required, current_user, login_user,logout_user
from albumy.emails import send_register_mail, send_reset_password_mail
from albumy.forms.auth import ForgetPasswordForm, RegisterForm, LoginForm, ResetPasswordForm
from albumy.models import User
from albumy.extensions import db
from albumy.utils import generate_token, validate_token, redirect_back
from albumy.settings import Operations
from albumy.emails import send_confirm_mail

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        name = form.name.data
        email = form.email.data.lower()
        password = form.password.data
        user = User(name=name, username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user=user, operation=Operations.CONFIRM)
        send_confirm_mail(user, token)
        flash('激活邮件已发送到注册邮箱', 'info')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    
    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('激活成功', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('token过期或不可用', 'danger')
        return redirect(url_for('resend_confirmation'))


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    token = generate_token(user=current_user,operation=Operations.CONFIRM)
    send_confirm_mail(user=current_user, token=token)
    flash('新邮件已发送', 'info')
    return redirect(url_for('main.index'))
    

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('登录成功', ' info')
                return redirect_back()
            else:
                flash('账号被锁定','warning')
                return redirect(url_for('main.index'))
        else:
            flash('用户名或密码不可用', 'warning')
            redirect(url_for('.login'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/re-authenticate', methods=['GET', 'POST'])
@login_required
def re_authenticate():
    pass
            

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('退出账户成功', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/forget-password')
def forget_password():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first():
        if user:
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            send_reset_password_mail(user=user, token=token)
            flash('邮件已发送，请前往邮件重设密码', 'info')
            return redirect(url_for('.login'))
        flash('账号不存在', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower).first()
        if user is None:
            flash('邮箱未注册', 'warning')
            return redirect(url_for('main.index'))
        if validate_token(user=user,operation=Operations.RESET_PASSWORD,new_password=form.password.data):
            flash('密码已更新', 'info')
            return redirect(url_for('.login'))
        else:
            flash('链接已过期或不可用', 'danger')
            return redirect(url_for('forget_password'))
    return render_template('auth/reset_password.html', form=form)

