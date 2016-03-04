from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import (LoginManager, login_required, login_user,
                         current_user, logout_user, UserMixin)
                         
from werkzeug import check_password_hash, generate_password_hash
from sqlalchemy import func, desc

from app import app
from app import db
from app.users.forms import RegisterForm, LoginForm, DataForm, SettingsForm, ListForm, PartnerForm
from app.users.models import User, Account, ExpenseList
from app.users.decorators import requires_login

from utils import check_balances
mod = Blueprint('users', __name__, url_prefix='/users')  

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
login_manager.init_app(app)
login_manager.login_view = "/login/"
login_manager.setup_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@login_manager.token_loader
def load_token(token):
    data = login_serializer.loads(token)
    user = load_user(data[0])
    if user and data[1] == user.password:
        return user
    else: return None
        
@mod.route('/me/')
def home():
    g.user=None
    user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        flash("user is logged")
    return render_template("index.html", guser=g.user)
    
@mod.route('/profile/', methods=['GET', 'POST'])
@requires_login
def profile():
    user = User.query.filter_by(id=session['user_id']).first()
    p1 = User.query.filter_by(email=user.partner1_email).first()
    p2 = User.query.filter_by(email=user.partner2_email).first()
    
    lists = ExpenseList.query.filter_by(user_id=session['user_id']).all()            
    if p1: 
        lists_p1 = ExpenseList.query.filter_by(user_id=p1.id).all()
        lists = lists + lists_p1
    if p2: 
        lists_p2 = ExpenseList.query.filter_by(user_id=p2.id).all()
        lists = lists + lists_p2
    
    unique_listnames = list(set([l.list_name for l in lists]))
    
    form = DataForm(request.form)    
    if form.validate_on_submit():
        # Edit an individual entry    
        edit_data = Account.query.filter_by(edit=True).first()
        if edit_data:   
            edit_data.date = form.date.data
            edit_data.spent = form.amount.data
            edit_data.description = form.description.data
            edit_data.edit = False
            db.session.add(edit_data)
            db.session.commit()
        else:
            data = Account(user_id=session['user_id'], list_name=user.current_list, 
                           user_name=user.name, date=form.date.data, description=form.description.data, \
                           spent=form.amount.data, edit=False)
            db.session.add(data)
            db.session.commit()
            
            unpay_lists = ExpenseList.query.filter_by(user_id=session['user_id'],list_name=user.current_list).all()

            if p1: 
                unpay_lists_p1 = ExpenseList.query.filter_by(user_id=p1.id,list_name=user.current_list).all()
                unpay_lists = unpay_lists +  unpay_lists_p1

            if p2: 
                unpay_lists_p2 = ExpenseList.query.filter_by(user_id=p2.id,list_name=user.current_list).all()
                unpay_lists = unpay_lists +  unpay_lists_p2
            
            for li in unpay_lists:
                if li.payed:
                    li.payed = False
                    db.session.add(li)
                    db.session.commit()
                if li.received:
                    li.received = False 
                    db.session.add(li)   
                    db.session.commit()  
        return redirect(url_for('users.profile'))
    
    # Save list as
    form_save = ListForm(request.form)
    if form_save.validate_on_submit():            
        # Change list name in all entries in current list
        list_all = Account.query.filter_by(user_id=session['user_id'], list_name=user.current_list).all()
        if p1:
            list_p1 = Account.query.filter_by(user_id=p1.id, list_name=user.current_list).all()
            list_all = list_all + list_p1
        if p2:
            list_p2 = Account.query.filter_by(user_id=p2.id, list_name=user.current_list).all()
            list_all = list_all + list_p2
                 
        for li in list_all:
            li.list_name = form_save.list_name.data
            db.session.add(li)
            db.session.commit()
        
        # Add list
        list_u = ExpenseList.query.filter_by(user_id=session['user_id'],list_name="new").first()
        new_list_u = ExpenseList(user_id=session['user_id'], list_name=form_save.list_name.data, \
                            archived=True, payed=list_u.payed, received=list_u.received)
        db.session.add(new_list_u)                      
        db.session.commit()      
        
        list_u.payed = False
        db.session.add(list_u)
        db.session.commit()
        
        if p1:
            list_p1 = ExpenseList.query.filter_by(user_id=p1.id,list_name="new").first()
            new_list_p1 = ExpenseList(user_id=p1.id, list_name=form_save.list_name.data, \
                               archived=True, payed=list_p1.payed, received=list_p1.received)
            db.session.add(new_list_p1)
            db.session.commit()
            
            list_p1.payed = False
            db.session.add(list_p1)
            db.session.commit()
            
        if p2: 
            list_p2 = ExpenseList.query.filter_by(user_id=p2.id,list_name="new").first()
            new_list_p2 = ExpenseList(user_id=p2.id, list_name=form_save.list_name.data, \
                               archived=True, payed=list_p2.payed, received=list_p2.received)
            db.session.add(new_list_p2)
            db.session.commit()
                
            list_p2.payed = False
            db.session.add(list_p2)
            db.session.commit()
                
        user.current_list = form_save.list_name.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.profile'))
              
    entries = Account.query.filter_by(user_id=session['user_id'], list_name=user.current_list) \
                            .order_by(desc(Account.trans_id)).all()
    bal = check_balances(current_list=user.current_list)
    
    if p1:
        p1_entries = Account.query.filter_by(user_id=p1.id, list_name=user.current_list) \
                                   .order_by(desc(Account.trans_id)).all()
        entries = entries + p1_entries
    if p2:
        p2_entries = Account.query.filter_by(user_id=p2.id, list_name=user.current_list) \
                                  .order_by(desc(Account.trans_id)).all()
        entries = entries + p2_entries
            
    return render_template("users/profile.html", user=user, form=form, lists=lists, unique_listnames=unique_listnames, \
           form_save = form_save, entries=entries, bal=bal, p1=p1, p2=p2, guser=g.user)
 
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
            login_user(user, remember=form.remember.data)
            return redirect(url_for('users.profile'))
        flash('Wrong email or password', 'login-error')
    return render_template("users/login.html", form=form)
          
#@mod.route('/login/', methods=['GET', 'POST'])
#def login():
#    form = LoginForm(request.form)
#    if form.validate_on_submit():
#        user = User.query.filter_by(email=form.email.data).first()
#        if user and check_password_hash(user.password, form.password.data):
#            session['user_id'] = user.id
#            flash('Welcome %s' % user.name)
#            return redirect(url_for('users.profile'))
#        flash('Wrong email or password', 'login-error')
#    return render_template("users/login.html", form=form)
    
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
            
            first_list = ExpenseList(user_id=session['user_id'], list_name="new")
            db.session.add(first_list)
            db.session.commit()
            return redirect(url_for('users.profile'))
        
    return render_template("users/register.html", form=form)

@mod.route('/logout')
@requires_login
def logout():
    logout_user()
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
@mod.route('/edit/<int:entry_id>')
def edit_entry(entry_id):
    trans = Account.query.filter_by(trans_id=entry_id).first()
    trans.edit = True
    if trans.user_id == session['user_id']:
        db.session.add(trans)
        db.session.commit()
    else: flash('Oops, you can only edit your own entries.', 'delete')
    return redirect(url_for('users.profile'))
    
@requires_login
@mod.route('/settings/', methods=['GET', 'POST'])
def settings():
    if 'user_id' in session:
        flash("user is logged")
        user = User.query.filter_by(id=session['user_id']).first()
        entries = Account.query.filter_by(user_id=session['user_id']).all()
    else: 
        g.user=None
        user=None
    form = SettingsForm(request.form)
    if form.validate_on_submit():
        # Change Name
        if form.change_name.data:
            if form.change_name.data != user.name:
                user.name = form.change_name.data
                db.session.add(user)
                db.session.commit()
                
                for entry in entries:
                    entry.user_name = form.change_name.data
                    db.session.add(entry)
                    db.session.commit()
                flash("Your name has been succesfully updated.", "change-settings")
                return redirect(url_for('users.settings'))
        # Change Password
        if form.change_pwd.data:
            user.password = generate_password_hash(form.change_pwd.data)
            db.session.add(user)
            db.session.commit()
            flash("Your password has been succesfully updated.", "change-settings")
            return redirect(url_for('users.settings'))
        
    pform = PartnerForm(request.form)
    if pform.validate_on_submit():    
        if pform.partner1.data:
            if pform.partner1.data != user.partner1_email and pform.partner1.data != user.partner2_email:
                user.partner1_email = pform.partner1.data
                db.session.add(user)
                db.session.commit()
                flash("Your Partner 1 info has been succesfully updated.", "add-partner")
          
        if pform.partner2.data:
             if pform.partner2.data != user.partner1_email and pform.partner2.data != user.partner2_email:    
                user.partner2_email = pform.partner2.data   
                db.session.add(user)
                db.session.commit()
                flash("Your Partner 2 info has been succesfully updated.", "add-partner")
             
        return redirect(url_for('users.settings'))              
    return render_template("users/settings.html", user=user, guser=g.user, form=form, pform=pform)
     
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
    return render_template("about.html", guser=g.user) 

@requires_login
@mod.route('/delete_new/')
def delete_new():
    user = User.query.filter_by(id=session['user_id']).first()
    p1 = User.query.filter_by(email=user.partner1_email).first()
    p2 = User.query.filter_by(email=user.partner2_email).first()
    
    list_u = ExpenseList.query.filter_by(user_id=session['user_id'],list_name=user.current_list).first()
    if p1: list_p1 = ExpenseList.query.filter_by(user_id=p1.id,list_name=user.current_list).first()
    if p2: list_p2 = ExpenseList.query.filter_by(user_id=p2.id,list_name=user.current_list).first()
    
    trans = Account.query.filter_by(user_id=session['user_id'], list_name=user.current_list).all()
    if p1: 
        trans_p1 = Account.query.filter_by(user_id=p1.id, list_name=user.current_list).all()
        trans = trans + trans_p1        
    if p2: 
        trans_p2 = Account.query.filter_by(user_id=p2.id, list_name=user.current_list).all()
        trans = trans + trans_p2 
    if trans:           
        for tran in trans:
            db.session.delete(tran)
            db.session.commit()
        
    user.current_list = "new"
    db.session.add(user)
    db.session.commit()
    
    if p1: 
        p1.current_list = "new"
        db.session.add(p1)
        db.session.commit()
    if p2: 
        p1.current_list = "new"
        db.session.add(p2)
        db.session.commit()

    
    if list_u and list_u.list_name != "new":
        db.session.delete(list_u)
        db.session.commit()
    if p1: 
        if list_p1 and list_p1.list_name != "new": 
            db.session.delete(list_p1)
            db.session.commit()
    if p2: 
        if list_p2 and list_p2.list_name != "new": 
            db.session.delete(list_p2)
            db.session.commit()
    
    return redirect(url_for('users.profile'))
    
@requires_login
@mod.route('/current_list/<list_name>')
def current_list(list_name):
    user = User.query.filter_by(id=session['user_id']).first()
    user.current_list = list_name
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('users.profile'))

@requires_login
@mod.route('/delete_partner/<partner_email>')
def delete_partner(partner_email):
    user = User.query.filter_by(id=session['user_id']).first()
    if user.partner1_email == partner_email:
        user.partner1_email = None
    if user.partner2_email == partner_email:
        user.partner2_email = None
    flash(partner_email, "add_partner")
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('users.settings'))
    
@requires_login
@mod.route('/mark_payed/<listname>/<payed_by>/<receiver>')
def mark_payed(listname, payed_by, receiver):
    user = User.query.filter_by(id=session['user_id']).first()
    p1 = User.query.filter_by(email=user.partner1_email).first()
    p2 = User.query.filter_by(email=user.partner2_email).first()
            
    lis = ExpenseList.query.filter_by(user_id=payed_by,list_name=listname).first()   
    if lis.payed:
        lis.payed = False
    else:    
        lis.payed = True
    db.session.add(lis)
    db.session.commit()
    
    lis_r = receiver = ExpenseList.query.filter_by(user_id=receiver,list_name=listname).first() 
    if lis_r.received:
        lis_r.received = False
    else: 
        lis_r.received = True       
    db.session.add(lis_r)
    db.session.commit()
    return redirect(url_for('users.profile'))