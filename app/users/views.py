from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import func, desc

from app import db
from app.users.forms import RegisterForm, LoginForm, DataForm, SettingsForm
from app.users.models import User
from app.users.models import Account
from app.users.decorators import requires_login


mod = Blueprint('users', __name__, url_prefix='/users')

def check_balances():
    balances = {}
    total_spent = (db.session.query(func.sum(Account.spent))\
                   .filter_by(user_id=session['user_id']).first())[0]
    total_earned = (db.session.query(func.sum(Account.credit))\
                    .filter_by(user_id=session['user_id']).first())[0]
                    
    if not total_spent: total_spent = 0.0
    if not total_earned: total_earned = 0.0
    balances['ts_user'] = total_spent
    balances['te_user'] = total_earned
    balances['t_user'] = balances['te_user'] - balances['ts_user']
    
    total_spent_user = total_spent
    total_earned_user = total_earned
    
    user = User.query.filter_by(id=session['user_id']).first()
    
    # Get the info for Partner 1
    partner1 = User.query.filter_by(email=user.partner1_email).first()
    if partner1:
        total_spent_partner1 = (db.session.query(func.sum(Account.spent))\
                            .filter_by(user_id=partner1.id).first())[0]
        #total_earned_partner1 = (db.session.query(func.sum(Account.credit))\
         #                   .filter_by(user_id=partner1.id).first())[0]  
                                                  
        if not  total_spent_partner1: total_spent_partner1 = 0.0
        #if not  total_earned_partner1: total_earned_partner1 = 0.0
        balances['ts_p1'] =  total_spent_partner1
        #balances['te_p1'] = total_earned_partner1
        #balances['t_p1'] = balances['te_p1'] - balances['ts_p1']
        
     # Get the info for Partner 2
    partner2 = User.query.filter_by(email=user.partner2_email).first()
    if partner2:
          total_spent_partner2 = (db.session.query(func.sum(Account.spent))\
                            .filter_by(user_id=partner2.id).first())[0]
          #total_earned_partner2 = (db.session.query(func.sum(Account.credit))\
           #                 .filter_by(user_id=partner2.id).first())[0]  
                                                  
          if not  total_spent_partner2: total_spent_partner2 = 0.0
          #if not  total_earned_partner2: total_earned_partner2 = 0.0
          balances['ts_p2'] =  total_spent_partner2
          #balances['te_p2'] = total_earned_partner2
          #balances['t_p2'] = balances['te_p2'] - balances['ts_p2']
          
    if partner1 and not partner2:
         balances['ts'] = balances['ts_user'] + balances['ts_p1']
         #balances['te'] = balances['te_user'] + balances['te_p1']
         if balances['ts_user'] < balances['ts_p1']:
             balances['ower'] = user.name
             balances['receiver'] = partner1.name
         else:
             balances['ower'] = partner1.name
             balances['receiver'] = user.name
         balances['amount_owned'] = 0.5 * (balances['ts_user'] - balances['ts_p1'])    
         #balances['surplus'] = 0.5 * (balances['te'] - balances['ts'])      
         
    elif partner1 and partner2:
         balances['ts'] = balances['ts_user'] + balances['ts_p1'] + balances['ts_p2']
         #balances['te'] = balances['te_user'] + balances['te_p1'] + balances['te_p2']
         
         #mean = 0.3333333*(balances['ts'] - balances['te'])
         mean = 0.3333333*(balances['ts'])
         diff_u = mean - balances['ts_user']
         diff_p1 = mean - balances['ts_p1']
         diff_p2 = mean - balances['ts_p2']    
         
         big_spender = min(balances['ts_user'], balances['ts_p1'], balances['ts_p2'])
         if big_spender == balances['ts_user']: 
             balances['receiver'] = user.name    
             balances['ower'] = partner1.name
             balances['amount_owned'] = diff_p1
             balances['ower2'] = partner2.name 
             balances['amount_owned2'] = diff_p2
         elif big_spender == balances['ts_p1']: 
             balances['receiver'] = partner1.name
             balances['ower'] = user.name
             balances['amount_owned'] = diff_u
             balances['ower2'] = partner2.name 
             balances['amount_owned2'] = diff_p2 
         else: 
            balances['receiver'] = partner2.name
            balances['ower'] = user.name
            balances['amount_owned'] = diff_u
            balances['ower2'] = partner1.name 
            balances['amount_owned2'] = diff_p1
         #balances['surplus'] = 0.333333 * (balances['te'] - balances['ts'])  
               
    elif not partner1 and partner2:
         balances['ts'] = balances['ts_user'] + balances['ts_p2']
         #balances['te'] = balances['te_user'] + balances['te_p2']
         if balances['ts_user'] < balances['ts_p2']:
             balances['ower'] = user.name
             balances['receiver'] = partner2.name
         else:
             balances['ower'] = partner2.name
             balances['receiver'] = user.name
         balances['amount_owned'] = 0.5 * (balances['ts_user'] - balances['ts_p2'])  
         #balances['surplus'] = 0.5 * (balances['te'] - balances['ts'])  
    else:
         balances['ts'] = balances['ts_user'] 
         #balances['te'] = balances['te_user'] 
         balances['amount_owned'] = 0.0
         #balances['surplus'] = 0.5 * (balances['te'] - balances['ts'])  
         
    #balances['tot'] =  balances['te'] -  balances['ts']
    balances['tot'] =  balances['ts']
    return balances, partner1, partner2
    
@mod.route('/me/')
def home():
    g.user=None
    username=''
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        flash("user is logged")
        user = User.query.filter_by(id=session['user_id']).first()
        if user: username = user.name
        return redirect(url_for('users.profile'))
    return render_template("index.html", user=username, guser=g.user)


@mod.route('/profile/', methods=['GET', 'POST'])
@requires_login
def profile():
    user = User.query.filter_by(id=session['user_id']).first()
    form = DataForm(request.form)
    if form.validate_on_submit():
        if form.earned.data:
            credit = form.amount.data
            spent = 0.0
        else:
            credit = 0.0
            spent = form.amount.data
        data = Account(user_id=session['user_id'], user_name=user.name, date=form.date.data, \
                       description=form.description.data, \
                       spent=spent, credit=credit)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('users.profile'))
        
    entries = Account.query.filter_by(user_id=session['user_id']).order_by(desc(Account.trans_id)).all()
    bal, p1, p2 = check_balances()
    if p1: p1_entries = Account.query.filter_by(user_id=p1.id).order_by(desc(Account.trans_id)).all()
    if p2: p2_entries = Account.query.filter_by(user_id=p2.id).order_by(desc(Account.trans_id)).all()
    
    if p1:
        entries = entries + p1_entries
        if p2:
            entries = entries + p2_entries
            
    return render_template("users/profile.html", user=user.name, form=form, \
           entries=entries, bal=bal, p1=p1, p2=p2, guser=g.user)
 
@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
      
@mod.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash('Welcome %s' % user.name)
            return redirect(url_for('users.profile'))
        flash('Wrong email or password', 'login-error')
    return render_template("users/login.html", form=form)
    
@mod.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        check_user = User.query.filter_by(email=form.email.data).first()
        if check_user: 
            flash('A user with email %s already exists.' % form.email.data, "unique-user")
        else:
            user = User(name=form.name.data, email=form.email.data, \
                        password=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            flash('Thanks for registering')
            return redirect(url_for('users.profile'))
    return render_template("users/register.html", form=form)

@mod.route('/logout')
@requires_login
def logout():
    session.pop('user_id', None)
    session.clear()
    flash('You were succesfully logged out.')
    return redirect(url_for('users.home'))

@requires_login
@mod.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    trans = Account.query.filter_by(trans_id=entry_id).first()
    if trans.user_id == session['user_id']:
        db.session.delete(trans)
        db.session.commit()
    else: flash('Oops, you can only delete your own entries.', 'delete')
    return redirect(url_for('users.profile'))
    
@requires_login
@mod.route('/settings/', methods=['GET', 'POST'])
def settings():
    if 'user_id' in session:
        flash("user is logged")
        user_data = User.query.filter_by(id=session['user_id']).first()
    else: 
        g.user=None
        user=None
    form = SettingsForm(request.form)
    if form.validate_on_submit():
        # Change Name
        if form.change_name.data:
            if form.change_name.data != user_data.name:
                user_data.name = form.change_name.data
                db.session.add(user_data)
                db.session.commit()
                flash("Your name has been succesfully updated.", "change-settings")
                return redirect(url_for('users.settings'))
        # Change Password
        if form.change_pwd.data:
            user_data.password = generate_password_hash(form.change_pwd.data)
            db.session.add(user_data)
            db.session.commit()
            flash("Your password has been succesfully updated.", "change-settings")
            return redirect(url_for('users.settings'))
            
        if form.partner1.data:
            if form.partner1.data != user_data.partner1_email and form.partner1.data != user_data.partner2_email:
                user_data.partner1_email = form.partner1.dats
                db.session.add(user_data)
                db.session.commit()
                flash("Your Partner 1 info has been succesfully updated.", "add-partner")
            else:
                flash("Information is up-to-date", "add-partner")
            return redirect(url_for('users.settings'))
            
        if form.partner2.data:
            user_data.partner2_email = form.partner2.data   
            db.session.add(user_data)
            db.session.commit()
            flash("Your Partner 2 info has been succesfully updated.", "add-partner")
            return redirect(url_for('users.settings'))
              
    return render_template("users/settings.html", user=user_data.name, duser=user_data, \
                            guser=g.user, form=form)
    
    
@requires_login
@mod.route('/delete_user/')
def delete_user():
    user= User.query.filter_by(id=session['user_id']).first()
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id', None)
    session.clear()
    return redirect(url_for('users.home'))
   
@mod.route('/about/')
def about():
    user = User.query.filter_by(id=session['user_id']).first()
    return render_template("about.html", user=user.name, guser=g.user) 
    