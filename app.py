from extension import *
from Model import *

login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(pk):
    user = Customer.query.get(pk)
    if user is not None:
        return user

    seller = Seller.query.get(pk)
    if seller is not None:
        return seller


@app.route("/",methods=['GET'])
def index():
    return render_template('index.html')


@login_manager.unauthorized_handler
def unauthorized():
    return jsonify(
        {
            "user_logged_in_status": False,
            "message": "Unauthorized user / User not logged in",
        }
    )


def user_type_required(user_type):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if isinstance(current_user, user_type):
                return func(*args, **kwargs)
            else:
                return jsonify({"error": "Access denied"})

        return decorated_function

    return decorator


# Buyer Part
# register
@app.route("/api/addCustomer", methods=["POST"])
def addCustomer():
    try:
        data = request.get_json()
        name = data["name"]
        email = data["email"]
        mobile_no = data["mobile_no"]
        address = data["address"]
        password = data["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        customerEmail = Customer.query.filter_by(email=email).all()
        customerMobile = Customer.query.filter_by(mobile_no=mobile_no).all()
        print(customerEmail, customerMobile)
        if customerEmail:
            return jsonify({"msg": "User already exists with this mail id"})
        elif customerMobile:
            return jsonify({"msg": "User already exists with this mobile number"})
        else:
            newCustomer = Customer(
                name=name,
                email=email,
                mobile_no=mobile_no,
                address=address,
                password=hashed_password,
            )
            db.session.add(newCustomer)
            db.session.commit()
            return jsonify({"msg": "Register sucessful"})
    except Exception as e:
        return jsonify(str(e))


# login
@app.route("/api/customerLogin", methods=["POST"])
def customerLogin():
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        cust = Customer.query.get(email)
        if cust is not None:
            if bcrypt.check_password_hash(cust.password, password):
                login_user(cust)
                return jsonify({"msg": "Login sucessful", "name": current_user.name})
            else:
                return jsonify({"msg": "Please enter correct password.."})
        else:
            return jsonify({"msg": "User is not registered..Please register to login"})
    except Exception as e:
        return jsonify(str(e))


# logout
@app.route("/api/customerLogout", methods=["POST"])
@login_required
def customerLogout():
    try:
        logout_user()
        return jsonify("Logout Successful")
    except Exception as e:
        return jsonify(str(e))


# all products list
@app.route("/api/products", methods=["GET"])
def products():
    try:
        products = Product.query.all()
        productsList = []
        for product in products:
            productsList.append(product.as_dict())
        return jsonify(productsList)
    except Exception as e:
        return jsonify(str(e))


# add_to_cart
@app.route("/api/addToCart", methods=["POST"])
@login_required
@user_type_required(Customer)
def addToCart():
    try:
        data = request.get_json()
        customerEmail = current_user.email
        productId = data["productId"]
        productQty = 1
        existingProduct = Cart.query.filter_by(
            customerEmail=customerEmail, productId=productId
        ).first()
        # print(type(existingProduct))
        if existingProduct is not None:
            productQty = existingProduct.productQty + 1
            existingProduct.productQty = productQty
            db.session.add(existingProduct)
            db.session.commit()
            db.session.refresh(existingProduct)
            return jsonify(existingProduct.as_dict())
        else:
            cart = Cart(
                customerEmail=customerEmail, productId=productId, productQty=productQty
            )
            db.session.add(cart)
            db.session.commit()
            return jsonify(cart.as_dict())
    except Exception as e:
        # print(e)
        return jsonify(str(e))


# view_cart
@app.route("/api/viewCart", methods=["GET", "POST"])
@login_required
@user_type_required(Customer)
def viewCart():
    try:
        print(current_user.email)
        cartList = Cart.query.filter_by(customerEmail=current_user.email).all()
        print("in")
        productList = []
        if cartList:
            print(cartList)
            for cart in cartList:
                productId = cart.productId
                product = Product.query.get(productId)
                prodDict = product.as_dict()
                prodDict["qty"] = cart.productQty
                productList.append(prodDict)
            return jsonify(productList)
        else:
            return jsonify({"msg": "Cart is empty"})
    except Exception as e:
        return jsonify({"error": str(e)})


# delete_product from cart
@app.route("/api/deleteProduct", methods=["POST"])
@login_required
@user_type_required(Customer)
def deleteProduct():
    try:
        data = request.get_json()
        print(data)
        productId = data["productId"]
        product = Cart.query.filter(
            and_(Cart.customerEmail == current_user.email, Cart.productId == productId)
        ).first()
        if product is not None:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"msg": "Product Deleted Successfully"})
        else:
            return jsonify({"msg": "Not authenticate user to delete product"})
    except Exception as e:
        return jsonify({"error":True,"errorMessage":str(e)})


# update cart quantity
@app.route("/api/updateCartQuantity", methods=["POST"])
@login_required
@user_type_required(Customer)
def updateCartQuantity():
    try:
        data = request.get_json()
        product_id = data["id"]
        quantity = data["productQty"]
        customerEmail = current_user.email

        if quantity == 0:
            product = Cart.query.filter_by(
                productId=product_id, customerEmail=customerEmail
            ).first()
            db.session.delete(product)
            db.session.commit()
            return jsonify({"msg": "product deleted successfully"})
        else:
            product = Cart.query.filter_by(
                productId=product_id, customerEmail=customerEmail
            ).first()
            product.productQty = quantity
            db.session.add(product)
            db.session.commit()
            return jsonify({"msg": "Quantity updated successfully"})
    except Exception as e:
        return jsonify(str(e))


# Update Customer Information
@app.route("/api/updateCustomerInfo", methods=["POST"])
@login_required
@user_type_required(Customer)
def updateCustomerInfo():
    try:
        data = request.get_json()
        customer = Customer.query.get(current_user.email)
        if customer is not None:
            if "mobileNumber" in data.keys():
                mobileNumber = data["mobileNumber"]
                customerMobile = Customer.query.filter(
                    and_(
                        Customer.mobile_no == mobileNumber,
                        Customer.email != current_user.email,
                    )
                ).first()
                print(customerMobile)
                if customerMobile is not None:
                    db.session.commit()
                    return jsonify(
                        {"msg": "Mobile number already exists..You can not update.."}
                    )
                else:
                    customer.mobile_no = mobileNumber
            if "name" in data.keys():
                customer.name = data["name"]
            if "address" in data.keys():
                customer.address = data["address"]
            if "password" in data.keys():
                hashed_password = bcrypt.generate_password_hash(
                    data["password"]
                ).decode("utf-8")
                customer.password = hashed_password
            # db.session.add(customer)
            db.session.commit()
            return jsonify({"msg": "Customer updated successfully"})
    except Exception as e:
        return jsonify(str(e))


# place order
@app.route("/api/placeOrder", methods=["GET"])
@login_required
@user_type_required(Customer)
def placeOrder():
    try:
        productIds = []
        cartDetails = Cart.query.filter_by(customerEmail=current_user.email).all()
        if cartDetails:
            totalCost = 0
            for cart in cartDetails:
                productIds.append(cart.productId)
                totalCost += orderDetails(cart.productId, cart.productQty)
            gst_rate = 0.18
            deliveryCharges = 100
            totalCost += totalCost * gst_rate
            if totalCost < 999:
                totalCost += deliveryCharges
            order = Order(
                customerEmail=current_user.email,
                productIds=productIds,
                totalCost=totalCost,
            )
            db.session.add(order)
            db.session.commit()

            for cart in cartDetails:
                db.session.delete(cart)
            db.session.commit()
            return jsonify({"msg": "Order Placed Successfully"})
        else:
            return jsonify({"msg": "Nothing in cart to place order"})
    except Exception as e:
        return jsonify(str(e))


def orderDetails(productId, productQty):
    product = Product.query.get(productId)
    price = productQty * product.price
    product.availableQty = product.availableQty - productQty
    return price


# -------------------------------------------------------------------------------------------------------------------------------
# Seller Part
# Register
@app.route("/api/addSeller", methods=["POST"])
def addSeller():
    try:
        data = request.get_json()
        name = data["name"]
        email = data["email"]
        mobileNumber = data["mobileNumber"]
        address = data["address"]
        password = data["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        sellerEmail = Seller.query.filter_by(email=email).all()
        sellerMobile = Seller.query.filter_by(phone_number=mobileNumber).all()
        if sellerEmail:
            return jsonify({"msg": "User already exists with this mail id"})
        elif sellerMobile:
            return jsonify({"msg": "User already exists with this mobile number"})
        else:
            seller = Seller(
                name=name,
                address=address,
                phone_number=mobileNumber,
                email=email,
                password=hashed_password,
            )
            db.session.add(seller)
            db.session.commit()
            return jsonify({"msg": "Registration successful! You can now log in."})
    except Exception as e:
        return jsonify({"msg": str(e)})


# login
# login
@app.route("/api/sellerLogin", methods=["POST"])
def sellerLogin():
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        seller = Seller.query.filter_by(email=email).first()
        if seller is not None:
            print(seller)
            if bcrypt.check_password_hash(seller.password, password):
                login_user(seller)
                return jsonify({"msg": "Login sucessful", "name": current_user.email})
            else:
                return jsonify({"msg": "Please enter correct password.."})
        else:
            return jsonify({"msg": "User is not registered..Please register to login"})
    except Exception as e:
        return jsonify(str(e))


# seller update(seller info)
@app.route("/api/updateSellerInfo", methods=["POST"])
@login_required
@user_type_required(Seller)
def updateSellerInfo():
    try:
        data = request.get_json()
        seller = Seller.query.get(current_user.seller_id)
        if seller is not None:
            if "name" in data.keys():
                seller.name = data["name"]
            if "address" in data.keys():
                seller.address = data["address"]
            if "mobileNumber" in data.keys():
                mobileNumber = data["mobileNumber"]
                sellerMobile = Seller.query.filter(
                    and_(
                        Seller.phone_number == mobileNumber,
                        Seller.seller_id != current_user.seller_id,
                    )
                ).first()
                if sellerMobile is not None:
                    return jsonify(
                        {"msg": "Mobile number already exists..You can not update.."}
                    )
                else:
                    seller.phone_number = mobileNumber
            if "email" in data.keys():
                email = data["email"]
                sellerEmail = Seller.query.filter(
                    and_(
                        Seller.email == email,
                        Seller.seller_id != current_user.seller_id,
                    )
                ).first()
                if sellerEmail is not None:
                    return jsonify(
                        {"msg": "Email already exists..You can not update.."}
                    )
                else:
                    seller.email = email
            if "password" in data.keys():
                hashed_password = bcrypt.generate_password_hash(
                    data["password"]
                ).decode("utf-8")
                seller.password = hashed_password
            db.session.add(seller)
            db.session.commit()
            return jsonify({"msg": "seller updated successfully"})
    except Exception as e:
        return jsonify(str(e))


# seller update(product info)
@app.route("/api/updateSellerProduct", methods=["POST"])
@login_required
@user_type_required(Seller)
def updateSellerProduct():
    try:
        productId = request.form.get("productId")
        product = Product.query.filter(
            and_(Product.sellerId == current_user.seller_id, Product.id == productId)
        ).first()
        if product is not None:
            if "productName" in request.form:
                product.productName = request.form.get("productName")
            if "brandName" in request.form:
                product.brandName = request.form.get("brandName")
            if "description" in request.form:
                product.description = request.form.get("description")
            if "availableQty" in request.form:
                product.availableQty = request.form.get("availableQty")
            if "price" in request.form:
                product.price = request.form.get("price")
            if "file" in request.files:
                image = request.files["file"]
                if image.filename != "":
                    image_name_uuid = str(uuid.uuid4())
                    extension = image.filename.split(".")[-1]
                    if extension not in app.config["IMAGE_EXTENSIONS"]:
                        return jsonify(
                            {"msg": "Image extension should be png or jpg or jpeg"}
                        )
                    image.filename = image_name_uuid + "." + extension
                    productImagePath = "/static/" + image.filename
                    if product.productImage is not None:
                        deletedImage = product.productImage.split("/")[-1]
                        os.remove(f"build/static/{deletedImage}")
                    product.productImage = productImagePath
                    image.save(f"build/static/{image.filename}")
                else:
                    deletedImage = product.productImage.split("/")[-1]
                    os.remove(f"build/static/{deletedImage}")
                    product.productImage = None

            db.session.add(product)
            db.session.commit()
            return jsonify({"msg": "Product Information updated succesfully"})
        else:
            return jsonify({"msg": "Not authenticate user to update product info"})
    except Exception as e:
        return jsonify(str(e))


# delete product(seller part)
@app.route("/api/deleteSellerProduct", methods=["POST"])
@login_required
@user_type_required(Seller)
def deleteSellerProduct():
    try:
        data = request.get_json()
        productId = data["productId"]
        product = Product.query.filter(
            and_(Product.sellerId == current_user.seller_id, Product.id == productId)
        ).first()
        if product is not None:
            if product.productImage is not None:
                deletedImage = product.productImage.split("/")[-1]
                os.remove(f"build/static/{deletedImage}")
            db.session.delete(product)
            db.session.commit()
            return jsonify({"msg": "Product deleted successfully"})
        else:
            return jsonify({"msg": "Not authenticate user to delete product"})
    except Exception as e:
        return jsonify(str(e))


# test seller api
@app.route("/api/sellerTest", methods=["GET"])
@login_required
@user_type_required(Seller)
def sellerTest():
    return jsonify("This is sellers test api")


@app.route("/api/seller/addProduct", methods=["POST"])
@login_required
@user_type_required(Seller)
def addProduct():
    try:
        # data = request.get_json()
        # image = request.files["file"]
        productName = request.form.get("productName")
        brandName = request.form.get("brandName")
        description = request.form.get("description")
        availableQty = request.form.get("availableQty")
        price = request.form.get("price")

        # initailly setting image values to None (None values are required if image is not uploaded)
        image_name_uuid = None
        productImagePath = None

        image = request.files.get("image")
        if image is not None:
            image_name_uuid = str(uuid.uuid4())
            extension = image.filename.split(".")[-1]
            if extension not in app.config["IMAGE_EXTENSIONS"]:
                return jsonify({"msg": "Image extension should be png or jpg or jpeg"})
            image.filename = image_name_uuid + "." + extension
            productImagePath = "/static/" + image.filename

        new_product = Product(
            productName=productName,
            brandName=brandName,
            description=description,
            availableQty=availableQty,
            price=price,
            productImage=productImagePath,
            sellerId=current_user.seller_id,
        )

        db.session.add(new_product)
        db.session.commit()
        if image is not None:
            image.save(f"build/static/{image.filename}")

        return jsonify({"msg": "Product added successfully"})
    except Exception as e:
        print(e)
        return jsonify(str(e))


@app.route("/api/viewSellerProduct", methods=["GET"])
@login_required
@user_type_required(Seller)
def viewSellerProduct():
    try:
        productsList = []
        products = Product.query.filter_by(sellerId=current_user.seller_id).all()
        for product in products:
            productsList.append(product.as_dict())
        return jsonify(productsList)
    except Exception as e:
        return jsonify(str(e))


@app.route("/api/searchProduct", methods=["POST"])
def searchProduct():
    try:
        data = request.get_json()
        searchString = data["searchString"]
        products = Product.query.filter(
            (Product.productName.ilike(f"%{searchString}%"))
            | (Product.brandName.ilike(f"%{searchString}%"))
        ).all()

        productsOutputList = []
        for product in products:
            productsOutputList.append(product.as_dict())
        return jsonify({"msg": productsOutputList})
    except Exception as e:
        return jsonify(str(e))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run("0.0.0.0", debug=True)
