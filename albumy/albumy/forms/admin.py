from wtforms import ValidationError
from wtforms import SelectField, StringField,SubmitField,PasswordField,BooleanField,TextAreaField
from wtforms.validators import DataRequired, Email, Length
from albumy.forms.user import EditProfileForm
from albumy.models import Role, User

class EditProfileAdminForm(EditProfileForm):
    email = StringField('Email', validators=[DataRequired(),Email(), Length(1,254)])
    role = SelectField('role', coerce=int)
    active = BooleanField('Active')
    confirmed = BooleanField('Confirmed')
    submit = SubmitField()

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(**kwargs)
        self.role.choices =[(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user=user
    
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('The username is already in use.')

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('The email is already in use.')
