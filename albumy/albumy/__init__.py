# -*- coding=utf-8 -*-
import os 
import click

from flask import Flask, register_blueprint
from albumy.blueprints.admin import admin_bp
from albumy.blueprints.main import main_bp
from albumy.blueprints.user import user_bp
from albumy.blueprints.auth import auth_bp
from albumy.blueprints.ajax import ajax_bp
from albumy.extensions import db, bootstrap, login_manager, mail
from albumy.settings import config
from albumy.models import Role

def create_app(config_name=None):

    if config_name is None:
        config_name=os.getenv('FLASK_CONFIG', 'development')

    app = Flask('albumy')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandlers(app)
    register_shell_context(app)
    register_template_context(app)

    return app

def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(ajax_bp, url_prefix='/ajax')

def register_commands(app):
    @app.cli.command()
    def init():
        """ 初始化Albumy"""

        click.echo('初始化 roles 和 permissions 数据库')
        Role.init_role()
        click.echo('完成')

def register_errorhandlers(app):
    pass

def register_shell_context(app):
    @app.shell_context_processor
    def  make_shell_context():
        return dict(db=db)

def register_template_context(app):
    pass