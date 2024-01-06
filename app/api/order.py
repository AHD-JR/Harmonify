from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.schema import Order, User
from app.db import db
from app.serializers import order_serializer
from bson import ObjectId
from app.utils import oauth2, permissions

router = APIRouter(
    prefix='/api',
    tags=['Order']
)

orderTable = db['orders'] 

@router.post('/order', response_description='Place an order', response_model=Order)
def create_order(req: Order, current_user: User = Depends(oauth2.get_current_user)):
    try:
        order_object = req.dict()
        order_count = orderTable.count_documents({}) + 1 
        costumer = order_object["customer"] or ("Customer #" + str(order_count))
        order_object["customer"] = costumer
        order_object["receiptNo"] = order_count
        order_object['createdBy'] = current_user['id']
        customer_id_ref = orderTable.insert_one(order_object)
        new_order = orderTable.find_one({'_id': customer_id_ref.inserted_id})
        return JSONResponse(status_code=status.HTTP_200_OK, content=order_serializer(new_order))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get('/orders', response_description="Get all orders")
def get_all_orders(page: int, current_user: User = Depends(oauth2.get_current_user)):
    try:
        orders = list(orderTable.find({}).skip((page-1) * 10).limit(10))

        res = {
            "orders": [order_serializer(order) for order in orders], 
            "total": orderTable.count_documents({}), 
            "page": page, 
            "limit": 10
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
       
        
@router.put('/order/{order_id}', response_description='Update an order!')
def update_order(order_id: str, req: Order, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        order = orderTable.find_one({'_id': ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'Order does not exist!'})
        updated_result = orderTable.update_one({"_id": ObjectId(order_id)}, {"$set": req.dict()})
        if  updated_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'msg': 'Order not updated!'})
        updated_order = orderTable.find_one({"_id": ObjectId(order_id)})
        return JSONResponse(status_code=status.HTTP_200_OK, content=order_serializer(updated_order))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.put('/order/revoke/{order_id}', response_description="Revoke an order")
def revoke_order(order_id: str, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        order = orderTable.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "Order does not exist!"})
        revoked_result = orderTable.update_one({"_id": ObjectId(order_id)}, {"$set": {"revoked": True}})
        if revoked_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'msg': 'Order not updated!'})
        revoked_order = orderTable.find_one({"_id": ObjectId(order_id)})
        return JSONResponse(status_code=status.HTTP_200_OK, content=order_serializer(revoked_order))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    
