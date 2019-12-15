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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
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

#user agent gives info about browser
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

########################################################################################################################################################
def check_price(): 
    URL = request.form.get('product')   
    budget = request.form.get('budget')
    mail = request.form.get('email')
    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html')

    price = soup.find(id="price_inside_buybox").text.strip()
    converted_price = float(price[5:8])

    if (converted_price < float(budget)):
        send_mail(mail, URL)
        


def send_mail(address, link):   
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    #ehlo establishes connection to email
    server.ehlo()
    #tls encrypts
    server.starttls()
    server.ehlo()

    server.login('scotttnsum@gmail.com', 'cpmhhoretmxmajmk')

    subject = 'Price fell down! The price is now right!'
    body = f'Check the amazon link! {link}'

    msg = f"Subject: {subject}\n\n{body}"
    
    server.sendmail(
        'scotttnsum@gmail.com',
        address,
        msg
    )

    print('Email sent')
    
    server.quit()
    

##########################################################################################################################################################################3

@app.route('/')
def index():
    return render_template('index.html')

##################################################################

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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.email)


@app.route('/dashboard', methods=['POST'])
@login_required
def submission():
    while(True):
        check_price()
        time.sleep(86400)    
    return redirect(url_for('index'))

########################################################################################

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
