from flask.ext.wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField, FloatField, validators
from wtforms.validators import Required, EqualTo, Email, Length, NumberRange, optional
from werkzeug.datastructures import MultiDict
from models import User

def strip_string(string):
    if string == None: pass
    else: return string.strip()
    
class LoginForm(Form):
    email = TextField('Email address', [Required(), Email()], filters=[strip_string])
    password = PasswordField('Password', [Required()])
    remember = BooleanField('Remember Me')
    
    
class RegisterForm(Form):
    name = TextField('Name', [Required(), Length(min=4, max=15)], filters=[strip_string])
    email = TextField('Email address', [Required(), Email()], filters=[strip_string])
    password = PasswordField('Password', [Required(), Length(min=8, max=12)])
    confirm = PasswordField('Password', [
            Required(),
            EqualTo('password', message='Passwords must match')
            ])
    remember = BooleanField('Remember Me')
    #recaptcha = RecaptchaField()
          
class DataForm(Form):
    date = TextField('Date')
    description = TextField('Description', filters=[strip_string])
    amount = FloatField('Amount', [NumberRange(min=0)])
    edit = BooleanField('Edit')

class SettingsForm(Form):
    change_name = TextField('Name',[Length(min=4, max=15)], filters=[strip_string])
    change_pwd =  PasswordField('Password')
    change_pwd_confirm = PasswordField('Password', [
            EqualTo('change_pwd', message='Passwords must match')
            ])
            
class PartnerForm(Form):          
    partner1 = TextField('Partner 1', [optional(), Email()], filters=[strip_string])
    partner2 = TextField('Partner 2', [optional(), Email()], filters=[strip_string])

class ListForm(Form):
    list_name = TextField('List Name',[Length(min=1, max=15)], filters=[strip_string])
    