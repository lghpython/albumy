from email.headerregistry import DateHeader
from sqlite3 import Date
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField,TextAreaField,EmailField,URLField
from wtforms.validators import DataRequired,Length,Email,URL,Regexp,EqualTo


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,20), Regexp('^[a-zA-Z0-9]*$')])
    email = EmailField('Email', validators=[DataRequired(),Email(), Length(1,254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,128) ])
    password2 = PasswordField('Confirmed Password', validators=[DataRequired(), Length(8,128) ])
    submit = SubmitField()


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField()


class ForgetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1,254)])
    submit = SubmitField()


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1,254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,128), EqualTo(password2)])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()
