from app import db
from app.users import constants as USER
import datetime

class User(db.Model):
    
    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.SmallInteger, default=USER.USER)
    status = db.Column(db.SmallInteger, default=USER.NEW)
    partner1_email = db.Column(db.String(120))
    partner2_email = db.Column(db.String(120))
    
    def __init__(self, name=None, email=None, password=None, \
                 partner1_email=None, partner2_email=None):
        self.name = name
        self.email = email
        self.password = password
        self.partner1_email = partner1_email
        self.partner2_email = partner2_email
        
    def getStatus(self):
        return USER.STATUS[self.status]
        
    def getRole(self):
        return USER.ROLE[self.role]
    
    def __repr__(self):
        return '<User %r>' % (self.name)


class Account(db.Model):
    
    __tablename__ = 'users_account'
    trans_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    description=db.Column(db.String(120))
    spent = db.Column(db.Float)
    credit = db.Column(db.Float)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(50))
    def __init__(self, user_id=None, user_name=None, date=None, \
                 description=None, spent=0.0, credit=0.0,balance=0.0):
        self.user_id = user_id
        self.user_name = user_name
        
        if date: self.date = date 
        else:
            today = datetime.date.today()
            self.date = today.strftime('%d %b %Y')
             
        self.description = description
        
        if spent: self.spent = spent
        else: self.spent = 0.00
        
        if credit: self.credit = credit
        else: self.credit = 0.00
        
    
    