from bson import ObjectId

def user_serializer(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["username"]
    }

def login_serializer(user):
    return{
        "username": user["username"],
        "role": user["role"]
    }

def product_serializer(product):
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "price": product["price"],
        "category": product["category"],
        "quantity": product["quantity"]
    }

def category_serializer(category):
    return {
        "id": str(category["_id"]),
        "name": category["name"]
    }

def order_serializer(order):
    return {
        "id": str(order["_id"]),
        "items": order["items"],
        "customer": order["customer"],
        "orderType": order["orderType"],
        "receiptNo": order["receiptNo"],
        "createdAt": str(order["createdAt"]),
        "createdBy": order["createdBy"],
        "revoked": order["revoked"],
        "paymentType": order["paymentType"],
        "paidTotal": order["paidTotal"]
    }
