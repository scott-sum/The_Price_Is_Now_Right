import requests
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bs4 import BeautifulSoup # needed for web scraping
import smtplib
import time

# Instantiation
app = Flask(__name__) 

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # location of database
SQLALCHEMY_TRACK_MODIFICATIONS = False # no sqlalchemy warnings in console
bootstrap = Bootstrap(app) # allows use of flask-bootstrap
db = SQLAlchemy(app) # database
migrate = Migrate(app, db)

# Initialization
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# user agent gives info about browser (search 'my user agent')
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}

# Database Tables
class User(UserMixin, db.Model): # UserMixin provides default implementations for the methods flask-login expects users to have
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    title = db.Column(db.String(), nullable=False)
    productURL = db.Column(db.String(), nullable=False)
    currentPrice = db.Column(db.Integer)
    userBudget = db.Column(db.Integer, nullable=False)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Gmail', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class PriceTrackForm(FlaskForm):
    url = StringField('URL on Amazon', validators=[InputRequired()])
    userBudget = StringField('My Budget', validators=[InputRequired()])

########################################################################################################################################################
# connects flask-login and database
# provide user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def send_mail(address, link):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # ehlo establishes connection to email
    server.ehlo()
    # tls encrypts
    server.starttls()
    server.ehlo()

    # google two factor authentication
    server.login('scotttnsum@gmail.com', 'cpmhhoretmxmajmk')

    # configuring the contents of the email
    subject = 'Price fell down! The price is now right!'
    body = f'Check the amazon link! {link}'
    msg = f"Subject: {subject}\n\n{body}"    
    server.sendmail(
        'scotttnsum@gmail.com',
        address,
        msg
    )
    print('Email sent')    
    server.quit() # remember to leave the server when finished sending email


# gets information from price tracking form, parses the amazon page and finds the price
# if the price is under the budget, an email is sent to the user
# performed initially after filling out form on dashboard
def check_price_initial():
    URL = request.form.get('url')
    budget = request.form.get('userBudget')
    mail = User.query.filter_by(id=current_user.id).first().email
    print(mail)
    page = requests.get(URL, headers=headers) # essentially downloads the page    
    soup = BeautifulSoup(page.content, 'lxml') # uses bs4 and lxml parser
    # need to account for different types of amazon product pages
    if soup.find(id="price_inside_buybox") != None:
        price = soup.find(id="price_inside_buybox").text.strip()
    elif soup.find(id="priceblock_ourprice") != None:
        price = soup.find(id="priceblock_ourprice").text.strip()
    else:
        price = soup.find(id="priceblock_dealprice").text.strip()
    converted_price = float(price[5:10])
    productTitle = soup.find(id="productTitle").text.strip() # get the title as well to send to wishlist

    # send the email if price is under budget
    # otherwise, create an entry in the user's wishlist
    if (converted_price < float(budget)):
        send_mail(mail, URL)
        return 0
    else:
        new_product = Product(userId=current_user.id, title=productTitle, productURL=URL, currentPrice=converted_price, userBudget=budget)
        db.session.add(new_product)
        db.session.commit()
        return 1

# a bit different than check_price_initial(); this function is for periodically checking for changes in price
# mainly used in the pricetracker.py script for heroku scheduler
def check_price_periodically(product):
    URL = product.productURL
    budget = product.userBudget
    mail = User.query.filter_by(id=product.userId).first().email    
    page = requests.get(URL, headers=headers) # essentially downloads the page    
    soup = BeautifulSoup(page.content, 'lxml') # uses bs4 and lxml parser
    # need to account for different types of amazon product pages
    if soup.find(id="price_inside_buybox") != None:
        price = soup.find(id="price_inside_buybox").text.strip()        
    elif soup.find(id="priceblock_ourprice") != None:
        price = soup.find(id="priceblock_ourprice").text.strip()
    else:
        price = soup.find(id="priceblock_dealprice").text.strip()
    converted_price = float(price[5:10])
    
    product.currentPrice = converted_price
    db.session.commit()

    # send the email if price is under budget
    # otherwise, create an entry in the user's wishlist
    if (converted_price < float(budget)):
        send_mail(mail, URL)
        return 0
    else:        
        return 1
##########################################################################################################################################################################3

# homepage
@app.route('/')
def index():
    return render_template('index.html')

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  #checks if form has been submitted
        user = User.query.filter_by(username=form.username.data).first() # getting user from form
        if user: # checks if the user exists in the database
            if check_password_hash(user.password, form.password.data):  # checks if password is correct (imported method)
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

# signup page (similar to login route)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256') # hashing the password; sha236 generates a hash that is 80 characters long
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password) # creating a new user
        # adding and commit to database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

# dashboard page or the page with the price tracking form
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = PriceTrackForm()
    if form.validate_on_submit():        
        if (check_price_initial() == 0):  # check_price_initial() == 0 means that the price is under the budget and an email was sent
            return redirect(url_for('index'))
        else:
            form = PriceTrackForm()
            return render_template('dashboard.html', form=form) # price is higher than budget               
    return render_template('dashboard.html', form=form)

# wishlist page with list of user's tracking products
@app.route('/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist():
    id = current_user.id
    productList = Product.query.filter_by(userId=id).all()
    return render_template('wishlist.html', productList=productList)

# for removing an item from the wishlist
@app.route('/delete/<id>')
@login_required
def delete(id):
    remove_product = Product.query.filter_by(id=int(id)).first()
    db.session.delete(remove_product)
    db.session.commit()
    return redirect(url_for('wishlist'))

# for adjusting the budget for an item in the wishlist
@app.route('/budget/<id>', methods=['POST'])
@login_required
def budget(id):
    new_budget = request.form.get("new_budget")
    update_product = Product.query.filter_by(id=int(id)).first()    
    update_product.userBudget = new_budget
    db.session.commit()
    return redirect(url_for('wishlist'))

@app.route('/logout')
@login_required #cannot access directly must login first
def logout():
    logout_user() # method from flask-login
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
