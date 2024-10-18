from extension import UserMixin, db, Identity,json


class Customer(db.Model, UserMixin):
    _tablename_ = "customer"
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), primary_key=True)
    mobile_no = db.Column(db.String(10), nullable=False, unique=True)
    address = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    products = db.relationship("Cart", back_populates="customer",cascade="all, delete-orphan")
    orders=db.relationship("Order",backref="customer",cascade="all, delete-orphan")

    def get_id(self):
        return str(self.email)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Seller(db.Model, UserMixin):
    __tablename__ = "seller"
    seller_id = db.Column(
        db.Integer, Identity(start=1, cycle=True), primary_key=True, autoincrement=True
    )
    name = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    products = db.relationship(
        "Product", backref="seller", cascade="all, delete-orphan"
    )

    def __init__(self, name, address, phone_number, email, password):
        self.name = name
        self.address = address
        self.phone_number = phone_number
        self.email = email
        self.password = password

    def get_id(self):
        return str(self.seller_id)


class Product(db.Model):
    _tablename_ = "product"
    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(50), nullable=False)
    brandName = db.Column(db.String(50),nullable=False)
    description = db.Column(db.String(500))
    availableQty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    productImage = db.Column(db.String(60))
    sellerId = db.Column(db.Integer, db.ForeignKey("seller.seller_id"), nullable=False)
    customers = db.relationship("Cart", back_populates="product",cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerEmail = db.Column(db.String(50), db.ForeignKey("customer.email"))
    productId = db.Column(db.Integer, db.ForeignKey("product.id"))
    productQty = db.Column(db.Integer, nullable=False)
    customer = db.relationship("Customer", back_populates="products")
    product = db.relationship("Product", back_populates="customers")

    def __init__(self, customerEmail, productId, productQty):
        self.customerEmail = customerEmail
        self.productId = productId
        self.productQty = productQty

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerEmail=db.Column(db.String(50), db.ForeignKey("customer.email"))
    productIds=db.Column(db.Text)
    totalCost=db.Column(db.Float(precision=3))

    def __init__(self, customerEmail, productIds, totalCost):
        self.customerEmail = customerEmail
        self.productIds = json.dumps(productIds)
        self.totalCost = totalCost