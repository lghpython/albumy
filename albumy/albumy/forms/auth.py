from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms import StringField,SubmitField,PasswordField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,URL,Regexp,EqualTo
from albumy.models import User

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,20), Regexp('^[a-zA-Z0-9]*$')])
    email = StringField('Email', validators=[DataRequired(),Email(), Length(1,254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,128) ])
    password2 = PasswordField('Confirmed Password', validators=[DataRequired(), Length(8,128) ])
    submit = SubmitField()

    def validate_username(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('The email is already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')



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
    password = PasswordField('Password', validators=[DataRequired(), Length(8,128), EqualTo('password2')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField()
