from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Product, LoginForm, RegisterForm, PriceTrackForm
from .extensions import db
from .functions import check_price_initial, send_mail

main = Blueprint('main', __name__)

# homepage
@main.route('/')
def index():
    return render_template('index.html')

# login page
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  #checks if form has been submitted
        user = User.query.filter_by(username=form.username.data).first() # getting user from form
        if user: # checks if the user exists in the database
            if check_password_hash(user.password, form.password.data):  # checks if password is correct (imported method)
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main.dashboard'))
        return redirect(url_for('main.login'))
    return render_template('login.html', form=form)

# signup page (similar to login route)
@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256') # hashing the password; sha236 generates a hash that is 80 characters long
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password) # creating a new user
        # adding and commit to database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('signup.html', form=form)

# dashboard page or the page with the price tracking form
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = PriceTrackForm()
    if form.validate_on_submit():        
        if (check_price_initial() == 0):  # check_price_initial() == 0 means that the price is under the budget and an email was sent
            return redirect(url_for('main.index'))
        else:
            form = PriceTrackForm()
            return render_template('dashboard.html', form=form) # price is higher than budget               
    return render_template('dashboard.html', form=form)

# wishlist page with list of user's tracking products
@main.route('/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist():
    id = current_user.id
    productList = Product.query.filter_by(userId=id).all()
    return render_template('wishlist.html', productList=productList)

# for removing an item from the wishlist
@main.route('/delete/<id>')
@login_required
def delete(id):
    remove_product = Product.query.filter_by(id=int(id)).first()
    db.session.delete(remove_product)
    db.session.commit()
    return redirect(url_for('main.wishlist'))

# for adjusting the budget for an item in the wishlist
@main.route('/budget/<id>', methods=['POST'])
@login_required
def budget(id):
    new_budget = request.form.get("new_budget")
    update_product = Product.query.filter_by(id=int(id)).first()    
    update_product.userBudget = new_budget
    db.session.commit()
    return redirect(url_for('main.wishlist'))

@main.route('/logout')
@login_required #cannot access directly must login first
def logout():
    logout_user() # method from flask-login
    return redirect(url_for('main.index'))