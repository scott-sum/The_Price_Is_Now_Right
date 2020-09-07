from functions import check_price_periodically
from models import Product

productList = Product.query.all()

for product in productList:
    check_price_periodically(product)