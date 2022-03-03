from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Optional, DataRequired, Length


class DescriptionForm(FlaskForm):
    description = TextAreaField('Description', validators=[Optional(), Length(0,500)])
    submit = SubmitField()


class TagForm(FlaskForm):
    tag = StringField('Add Tag (user space to separate)', validators=[Optional(), Length(0,64)])
    submit = SubmitField()


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField()
