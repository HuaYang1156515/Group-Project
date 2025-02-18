from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from services import dbText

class PromotionStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, products):
        pass

class BuyXGetYFreeStrategy(PromotionStrategy):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    # calculate products
    def calculate_discount(self, products):
        total_discount = Decimal('0.00')
        products_sorted = sorted(products, key=lambda p: p['price'])
        total_quantity = sum(p['product_amount'] for p in products_sorted)
        discount_quantity = total_quantity // self.x * self.y

        if discount_quantity > 0:
            for product in products_sorted:
                if discount_quantity <= 0:
                    break

                if product['product_amount'] <= discount_quantity:
                    discount = product['price'] * Decimal(product['product_amount'])
                    total_discount += discount
                    discount_quantity -= product['product_amount']
                else:
                    discount = product['price'] * Decimal(discount_quantity)
                    total_discount += discount
                    discount_quantity = 0

        return total_discount

# get uers' cart product
def get_cart_products(user_id):
    
    query = f"""
    SELECT o.*, p.product_name,pic.pic_url from order_cart o join product_info p on o.product_id = p.product_id join product_pic_info pic on p.product_id = pic.product_id where o.selected = 1 and pic.is_master = 0 and o.user_id = '{user_id}' and o.if_paid = 1
    """
    
    products = dbText.query_all(query)
    
    return products

def calculate_promotion_discount(user_id, promotion_strategy):
    products = get_cart_products(user_id)
    total_discount = promotion_strategy.calculate_discount(products)
    return total_discount