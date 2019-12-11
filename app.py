import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from bs4 import BeautifulSoup
import smtplib # mail protocol allows sending of email
import time

app = Flask(__name__)
app.config['DEBUG'] = True

#user agent gives info about browser
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

#################################################################################
def check_price(): 
    URL = request.form.get('product')   
    budget = request.form.get('budget')
    mail = request.form.get('email')
    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html')

    title = soup.find(id="productTitle").text.strip()

    price = soup.find(id="price_inside_buybox").text.strip()
    converted_price = float(price[5:8])

    if (converted_price < float(budget)):
        send_mail(mail, URL)

#############################################################################
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

#############################################################################
@app.route('/')
def index_get():
    return render_template('index.html')

############################################################################

@app.route('/', methods=['POST'])
def index_post():
    while(True):
        check_price()
        time.sleep(86400)
    
    return redirect(url_for('index_get'))

