from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

def generate(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data={ 'id': user.id, 'operation': operation}
    data.update(**kwargs)

    return s.dumps(data)

def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    
    except (SignatureExpired, BadSignature):
        return False

    if data.get('operation') != operation or data.get('id') != user.id:
        return False

    if operation == Operation.CONFIRM:
        user.confirmed = True
    elif operation == Operation.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operation.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is None:
            user.email = new_email

    else:
        return false
    db.session.commit()
    return True
    