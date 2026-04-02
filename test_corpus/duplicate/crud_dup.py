
def get_user(user_id):
    return db.query(User).filter(User.id == user_id).first()

def get_product(product_id):
    return db.query(Product).filter(Product.id == product_id).first()

def get_order(order_id):
    return db.query(Order).filter(Order.id == order_id).first()
