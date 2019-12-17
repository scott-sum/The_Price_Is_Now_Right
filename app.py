import requests

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bs4 import BeautifulSoup
import smtplib
import time



app = Flask(__name__) 
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://scottsum:mysequelpassword@localhost/site_db'

SQLALCHEMY_TRACK_MODIFICATIONS = False # no sqlalchemy warnings in console
bootstrap = Bootstrap(app) # allows use of flask-bootstrap
db = SQLAlchemy(app) # database
mysql://b6aaca6de66f53:a00378e5@us-cdbr-iron-east-05.cleardb.net/heroku_931737ac09f87b4?reconnect=true
app.config['MYSQL_DATABASE_USER'] = 'b6aaca6de66f53'
app.config['MYSQL_DATABASE_PASSWORD'] = 'a00378e5'
app.config['MYSQL_DATABASE_DB'] = 'heroku_931737ac09f87b4'
app.config['MYSQL_DATABASE_HOST'] = 'us-cdbr-iron-east-05.cleardb.net'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model): # creating table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('gmail', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

# user agent gives info about browser
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

########################################################################################################################################################
# gets information from price tracking form, parses the amazon page and finds the price
# if the price is under the budget, an email is sent to the user
def check_price(): 
    URL = request.form.get('product')   
    budget = request.form.get('budget')
    mail = request.form.get('email')

    # essentially downloads the page
    page = requests.get(URL, headers=headers)
    # uses bs4 and lxml parser
    soup = BeautifulSoup(page.content, 'lxml')
    
    price = soup.find(id="price_inside_buybox").text.strip()
    converted_price = float(price[5:8])
    
    # only send the email if price is under budget
    if (converted_price < float(budget)):
        send_mail(mail, URL)
        return 0
    else:
        return 1
        

# sends an email to address with the link to the product
def send_mail(address, link):   
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    #ehlo establishes connection to email
    server.ehlo()
    #tls encrypts
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
    
    # remember to leave the server when finished sending email
    server.quit()
    

##########################################################################################################################################################################3

# homepage
@app.route('/')
def index():
    return render_template('index.html')

##################################################################

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return redirect(url_for('login'))

    return render_template('login.html', form=form)

#########################################################################
# signup page (similar to login route)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))    

    return render_template('signup.html', form=form)

########################################################################################################3

# dashboard page or the page with the price tracking form
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.email) # gets the email of the user that is currently logged in


@app.route('/dashboard', methods=['POST'])
@login_required
def submission():
    while(True):        
        if (check_price() == 0):  # check_price() == 0 means that the price is under the budget and an email was sent
            break # since the email was sent, we can exit the loop
        time.sleep(86400)  # keeps checking until the price falls below the budget   
    return redirect(url_for('index'))

########################################################################################

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
