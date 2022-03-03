from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, AnonymousUserMixin
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_dropzone import Dropzone
from flask_wtf import CSRFProtect
from flask_whooshee import Whooshee
from flask_moment import Moment
from flask_avatars import Avatars


db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
mail = Mail()
csrf = CSRFProtect()
dropzone = Dropzone()
whooshee = Whooshee()
moment = Moment()
avatars = Avatars()


@login_manager.user_loader
def load_user(user_id):
    from albumy.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'

login_manager.login_message_category = 'warning'

login_manager.refresh_view = 'auth.re_authenticate'

login_manager.needs_refresh_message_category = 'warning'


class Guest(AnonymousUserMixin):
    """ 避免 匿名用户 current_user 无法调用 can() 方法"""
    @property
    def is_admin(self):
        return False
    
    def can(self, perission_name):
        return False

login_manager.anonymous_user = Guest


