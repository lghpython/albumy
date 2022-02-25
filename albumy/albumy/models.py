from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from albumy.extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.Integer(30))
    website = db.Column(db.String(255))
    avatar_l = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_raw = db.Column(db.String(64))
    avatar_s = db.Column(db.String(64))
    bio = db.Column(db.String(120))
    location = db.Column(db.String(50))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)

    confirmed = db.Column(db.Boolean, default=False)
    locked = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    receive_collection_notification = db.Column(db.Boolean, default=True)
    receive_comment_notification = db.Column(db.Boolean, default=True)
    receive_follow_notification = db.Column(db.Boolean, default=True)
    public_collections= db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, ForeignKey='role.id')
    role = db.relationship('Role', back_populates='users')
    photos = db.relationship('Photo', back_populates='author', cascade='all')

    def set_password(self, password):
        self.password_hash=generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs) -> None:
        super(User, self).__init__( **kwargs)
        self.set_role()

    def set_role(self):
        if self.role is None:
            if self.email == current_app.config['ALBUMY_ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(name='User').first()
            db.session.commit()
            


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64))
    filename_m = db.Column(db.String(64))
    filename_s = db.Column(db.String(64))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    can_comment = db.Column(db.Boolean, default=False)
    flag = db.Column(db.Integer)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='photos')


roles_permissions=db.Table('roles_permissions',
    db.Column('role_id', ForeignKey='role.id'),
    db.Column('permission_id', ForeignKey='permission.id')
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')
    users = db.relationship('User', back_populates='roles')

    @staticmethod
    def init_role(self):
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
                db.sesssion.add(role)
            role.permissions=[]
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()



class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    role = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')