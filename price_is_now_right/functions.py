import requests
from flask import request
from flask_login import current_user
from bs4 import BeautifulSoup # needed for web scraping
import smtplib
import time
from .extensions import db
from .models import User, Product


# user agent gives info about browser (search 'my user agent')
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}

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