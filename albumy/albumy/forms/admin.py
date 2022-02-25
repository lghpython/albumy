from sqlite3 import Date
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,BooleanField,TextAreaField,EmailField,URLField
from wtforms.validators import DataRequired,Length,Email,URL,Regexp


class User(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,20), Regexp('^[a-zA-Z0-9]*$')])
    email = EmailField('Email', validators=[DataRequired(),Email(), Length(1,254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8,128) ])
    password2 = PasswordField('Confirmed Password', validators=[DataRequired(), Length(8,128) ])
    submit = SubmitField()
