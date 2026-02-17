# Just noise
class Product:
    def __init__(self, sku, price, title):
        self.sku = sku
        self.price = price
        self.title = title
        
    def in_stock(self):
        return True
