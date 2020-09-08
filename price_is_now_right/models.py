from flask_login import UserMixin
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from .extensions import db

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
    url = StringField('URL on eBay', validators=[InputRequired()])
    userBudget = StringField('My Budget', validators=[InputRequired()])