import os
from datetime import datetime
from distutils.command.build_scripts import first_line_re
from fileinput import filename
from importlib.resources import path
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin
from flask_avatars import Identicon
from albumy.extensions import db, whooshee


roles_permissions=db.Table(
    'roles_permissions',
    db.Column('role_id', db.ForeignKey('role.id')),
    db.Column('permission_id', db.ForeignKey('permission.id'))
)

tagging = db.Table('tagging',
    db.Column('Photo', db.Integer, db.ForeignKey('photo.id')),
    db.Column('Tag', db.Integer, db.ForeignKey('tag.id'))
)    

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    users = db.relationship('User', back_populates='role')
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')

    @staticmethod
    def init_role():
        roles_permissions_map={
            'Locked': ['FOLLOW', 'COLLECT'],
            'User':['FOLLOW','COLLECT','COMMENT','UPLOAD'],
            'Moderator':['FOLLOW','COLLECT','COMMENT','UPLOAD','MODERATE'],
            'Administrator':['FOLLOW','COLLECT','COMMENT','UPLOAD','MODERATE','ADMINISTER']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions=[]
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()
    

@whooshee.register_model('description')
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    filename_m = db.Column(db.String(64)) # 图片裁剪， 存储中型尺寸的图片
    filename_s = db.Column(db.String(64)) # 图片裁剪， 存储小型尺寸的图片
    description = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=False)
    flag = db.Column(db.Integer) # 被举报计数， 超过限定做相关处理

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='photos')
    comments = db.relationship('Comment', back_populates='photo', cascade='all')
    collectors = db.relationship('Collect', back_populates='collected', cascade='all')
    tags = db.relationship('Tag', secondary=tagging, back_populates='photos')


@whooshee.register_model('name')
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    photos = db.relationship('Photo', secondary=tagging, back_populates='tags')


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship('Role', secondary=roles_permissions, \
        back_populates='permissions')

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__


class Follow(db.Model):
    """relationship 对象"""
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # 引用粉丝的用户 Follow.follower， 粉丝用户引用偶像 User. following
    follower = db.relationship('User', foreign_keys=[follower_id], \
        back_populates='following', lazy='joined') 
    # 引用关注用户 Follow.followed,  被关注用户引用  User.Followers
    followed = db.relationship('User', foreign_keys=[followed_id], \
        back_populates='followers', lazy='joined') # 被关注  lazy='joined'联结的加载记录


class Collect(db.Model): 
    # relationship 对象， 收藏者为用户， 被收藏的是图片
    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    collected_id = db.Column(db.Integer, db.ForeignKey('photo.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # lazy='joined' 使用联结加载记录
    collector = db.relationship('User', back_populates='collections', lazy='joined')
    collected = db.relationship('Photo', back_populates='collectors', lazy='joined')


@whooshee.register_model('username')
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    name = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(120))
    location = db.Column(db.String(50))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    avatar_raw = db.Column(db.String(64))

    confirmed = db.Column(db.Boolean, default=False)
    locked = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    public_collections = db.Column(db.Boolean, default=True)
    receive_comment_notification = db.Column(db.Boolean, default=True)
    receive_follow_notification = db.Column(db.Boolean, default=True)
    receive_collect_notification = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    role = db.relationship('Role', back_populates='users')
    photos = db.relationship('Photo', back_populates='author',cascade='all')
    comments = db.relationship('Comment', back_populates='author', cascade='all')
    notifications = db.relationship('Notification', back_populates='receiver', cascade='all')
    collections = db.relationship('Collect', back_populates='collector', cascade='all')
    following = db.relationship('Follow', foreign_keys=[Follow.follower_id], \
        back_populates='follower', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],\
        back_populates='followed', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()
        self.follow(self)
        self.set_role()

    def set_password(self,password):
        self.password_hash= generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_role(self):
        if self.role is None:
            if self.email == current_app.config['ALBUMY_ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(name='User').first()
            db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()
    
    def unfollow(self, user):
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self,user):
        if user.id is None:
            return False
        return self.following.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.following.filter_by(follower_id=user.id).first() is not None

    @property
    def followed_photos(self):
        return Photo.query.join(Follow, Follow.followed_id==Photo.author_id).filter_by(Follow.follower_id==self.id)

    def collect(self, photo):
        if not self.is_collecting(photo):
            collect = Collect(collector=self, collected=photo)
            db.session.add(collect)
            db.session.commit()
    
    def uncollect(self, photo):
        collect = Collect.query.with_parent(self).filter_by(collected_id=photo.id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()
        
    def is_collecting(self, photo):
        return Collect.query.with_parent(self).filter_by(collected_id=photo.id).first() is not None

    def lock(self):
        self.locked=True
        self.role=Role.query.filter_by(name='Locked').first()
        db.session.commit()
    
    def unlock(self):
        self.locked = False
        self.role = Role.query.filter_by(name="User").first()
        db.session.commit()

    def blocked(self):
        self.active = False
        db.session.commit()

    def unblocked(self):
        self.active = True
        db.session.commit()

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.username)
        self.avatar_s = filenames[0]
        self.avatar_m = filenames[1]
        self.avatar_l = filenames[2]
        db.session.commit()

    @property
    def is_admin(self):
        return self.role.name == 'Administrator'

    @property
    def is_active(self):
        return self.active
    
    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission and self.role and permission in self.role.permissions


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)

    replied_id = db.Column('Comment', db.ForeignKey('comment.id'))
    author_id = db.Column('User', db.ForeignKey('user.id'))
    photo_id = db.Column('Photo', db.ForeignKey('photo.id'))

    photo = db.relationship('Photo', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    # 一级回复 relies (级联删除),  二级回复 replied
    replies = db.relationship('Comment', back_populates='replied', cascade='all')
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    """ 通知类和用户类关联 
    Notification.receiver_id --> User.id
    Notifiation.receiver  :::  User.notifications
    """
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.relationship('User', back_populates='notifications')


# 监听事件 删除头像和图片
@db.event.listens_for(User, 'after_delete', named=True)
def delete_avatars(**kwargs):
    target = kwargs['target']
    for filename in [target.avatar_s, target.avatar_m, target.avatar_l, target.avatar_raw]:
        if filename is not None:  # avatar_raw may be None
            path = os.path.join(current_app.config['AVATAR_SAVE_PATH'], filename)
            if os.path.exists(path):
                os.remove(path)

@db.event.listens_for(Photo, 'after_delete', named=True)
def delete_photos(**kwargs):
    target=kwargs['target']
    for filename in [target.filename_s, target.filename_m, target.filename]:
        if filename is not None:
            path = os.path.join(current_app.config['ALBUMY_PHOTO_PATH'], filename)
            if os.path.exists(path):
                os.remove(path)