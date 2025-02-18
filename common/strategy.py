from collections import namedtuple

Customer = namedtuple('Customer', 'name fidelity')


class LineItem:

    def __init__(self, product, quantity, price):
        self.price = price
        self.quantity = quantity
        self.product = product

    def total(self):
        return self.price * self.quantity


class Order:
    def __init__(self, customer, cart, promotion=None):
        self.promotion = promotion
        self.cart = cart
        self.customer = customer

    def total(self):
        if not hasattr(self, '__total'):
            self.__total = sum(item.total() for item in self.cart)
        return self.__total

    def due(self):
        if self.promotion is None:
            discount = 0
        else:
            discount = self.promotion(self)
        return self.total() - discount

    def __repr__(self):
        fmt = '<Order total: {:.2f} due: {:2f}>'
        return fmt.format(self.total(), self.due())


def FidelityPromo(order):
    '''有 1000 或以上积分的顾客，每个订单享 5% 折扣'''
    return order.total() * .05 if order.customer.fidelity >= 1000 else 0


def BulkItemPromo(order):
    '''同一订单中，单个商品的数量达到 20 个或以上，享 10% 折扣'''

    discount = 0
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * .1
    return discount


def LargeOrderPromo(order):
    '''订单中的不同商品达到 10 个或以上，享 7% 折扣'''

    distinct_items = {item.product for item in order.cart}
    if len(distinct_items) >= 10:
        return order.total() * .07
    return 0

def BuyThreeGetOneFreePromo(order):
    '''每购买三件商品，其中一件商品免费'''
    discount = 0
    # 统计购物车中每种商品的数量
    product_quantity_map = {}
    for item in order.cart:
        product_quantity_map[item.product] = product_quantity_map.get(item.product, 0) + item.quantity
    
    # 遍历每种商品，计算免费数量
    for product, quantity in product_quantity_map.items():
        free_items = quantity // 3  # 计算免费商品的数量
        discount += free_items * order.cart[0].price  # 假设免费的商品价格与第一个商品相同
    
    return discount

# 在 Order 类中添加新的促销策略
order = Order(Customer('Alice', 1200), [LineItem('apple', 4, 0.5), LineItem('banana', 6, 0.3)], BuyThreeGetOneFreePromo)


joe = Customer('John Doe', 0)
ann = Customer('Ann Smith', 1100)
cart = [LineItem('banana', 4, .5), LineItem('apple', 10, 1.5), LineItem('watermellon', 5, 5.0)]

result = Order(joe, cart, FidelityPromo)
print(f'result -> {result}')

result = Order(ann, cart, FidelityPromo)
print(f'result -> {result}')

banana_cart = [LineItem('banana', 30, 5), LineItem('apple', 10, 1.5)]
result = Order(joe, banana_cart, BulkItemPromo)
print(f'result -> {result}')

long_order = [LineItem(str(item_code), 1, 1.0) for item_code in range(10)]
result = Order(joe, long_order, LargeOrderPromo)
print(f'result -> {result}')

