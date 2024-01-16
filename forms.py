from wtforms import Form, StringField, DecimalField, IntegerField, TextAreaField, PasswordField, validators

class RegisterForm(Form):
    name = StringField('Full Name', [validators.DataRequired(), validators.length(min=1,max=50)])
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=1, max=50)])
    email = StringField('email', [validators.DataRequired(), validators.Length(min=1, max=50)])
    password = PasswordField('password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match!')])
    confirm = PasswordField('Confirm Password')

