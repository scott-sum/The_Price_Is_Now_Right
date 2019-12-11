#requests allows us to access a url and pull out the data from the website
import requests, cgi
from bs4 import BeautifulSoup
import smtplib #mail protocol allows sending of email
import time

data = cgi.FieldStorage()

URL = data.getvalue('link')
#https://www.amazon.ca/QuietComfort-Wireless-Headphones-Cancelling-Control/dp/B0756CYWWD/ref=sr_1_3?keywords=bose+qc35ii&qid=1575824446&sr=8-3

#user agent gives info about browser
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

def check_price():
    budget = data.getvalue('price')
    mail = data.getvalue('email')
    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html')

    title = soup.find(id="productTitle").text.strip()

    price = soup.find(id="priceblock_ourprice").text
    converted_price = float(price[5:8])

    if (converted_price < float(budget)):
        send_mail()
    

def send_mail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    #ehlo establishes connection to email
    server.ehlo()
    #tls encrypts
    server.starttls()
    server.ehlo()

    server.login('scotttnsum@gmail.com', 'cpmhhoretmxmajmk')

    subject = 'Price fell down!'
    body = f'Check the amazon link {URL}'

    msg = f"Subject: {subject}\n\n{body}"
    
    server.sendmail(
        'scotttnsum@gmail.com',
        mail,
        msg
    )

    print('Email sent')
    server.quit()

while(True):
    check_price()
    time.sleep(86400)


