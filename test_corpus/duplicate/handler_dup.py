
class UserHandler:
    def get(self, id):
        return db.get_user(id)
    def create(self, data):
        return db.create_user(data)

class ProductHandler:
    def get(self, id):
        return db.get_product(id)
    def create(self, data):
        return db.create_product(data)
