from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField, FloatField, validators
from wtforms.validators import Required, EqualTo, Email, Length
from werkzeug.datastructures import MultiDict

class LoginForm(Form):
    email = TextField('Email address', [Required(), Email()])
    password = PasswordField('Password', [Required()])
    remember = BooleanField('Remember Me')
    
class RegisterForm(Form):
    name = TextField('Name', [Required(), Length(min=4, max=15)])
    email = TextField('Email address', [Required(), Email()])
    password = PasswordField('Password', [Required(), Length(min=8, max=12)])
    confirm = PasswordField('Password', [
            Required(),
            EqualTo('password', message='Passwords must match')
            ])
    remember = BooleanField('Remember Me')
    #recaptcha = RecaptchaField()
          
class DataForm(Form):
    date = TextField('Date')
    description = TextField('Description')
    amount = FloatField('Amount')
    earned = BooleanField('Earned!')

class SettingsForm(Form):
    change_name = TextField('Name',[Length(min=4, max=15)])
    change_pwd =  PasswordField('Password')
    change_pwd_confirm = PasswordField('Password', [
            EqualTo('change_pwd', message='Passwords must match')
            ])          
    partner1 = TextField('Partner 1')
    partner2 = TextField('Partner 2')
    
    
    
