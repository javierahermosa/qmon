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
    current_list = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=False)
    
    def __init__(self, name=None, email=None, password=None, \
                 partner1_email=None, partner2_email=None, \
                 current_list="new", active=False):
        self.name = name
        self.email = email
        self.password = password
        self.partner1_email = partner1_email
        self.partner2_email = partner2_email
        self.current_list = current_list
        self.active = False
        
    def getStatus(self):
        return USER.STATUS[self.status]
        
    def getRole(self):
        return USER.ROLE[self.role]
    
    def __repr__(self):
        return '<User %r>' % (self.name)
    
    def is_active(self):
        return self.active
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True
    
    def get_auth_token(self):
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)


class Account(db.Model):
    
    __tablename__ = 'users_account'
    trans_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(50))
    date = db.Column(db.String(50))
    description=db.Column(db.String(120))
    spent = db.Column(db.Float)
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(50))
    edit = db.Column(db.Boolean, default=False)
    
    def __init__(self, list_name="new",  date=None, \
                 description=None, spent=0.0, user_id=None, user_name=None, \
                 edit=False, edit_list_name=False, delete_list=False):
   
        self.list_name = list_name
        
        if date: self.date = date 
        else:
            today = datetime.date.today()
            self.date = today.strftime('%d %b %Y')
             
        self.description = description
        self.spent = spent
        self.user_id = user_id
        self.user_name = user_name
        self.edit = edit

        
        
    
    