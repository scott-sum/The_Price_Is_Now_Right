from app import *

productList = Product.query.all()

for product in productList:
    check_price_periodically(product)