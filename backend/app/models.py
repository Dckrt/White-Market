# Represents the core data entities for White Market

class User:
    def __init__(self, id, username, email, role, rating=5.0):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.rating = rating


class Product:
    def __init__(
        self,
        id,
        title,
        description,
        price,
        category,
        status,
        seller_id,
        image_url=None,
        created_at=None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.price = price
        self.category = category
        self.status = status
        self.seller_id = seller_id
        self.image_url = image_url
        self.created_at = created_at