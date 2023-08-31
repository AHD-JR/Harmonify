from fastapi import APIRouter, status, HTTPException, Depends
from app.schema import Product, User
from app.db import db
from bson import ObjectId
from fastapi.responses import JSONResponse
from app.serializers import product_serializer
from typing import List
from app.api.category import categoryTable
from app.utils import oauth2, permissions

router = APIRouter(
    tags=['Product'],
    prefix='/api'
)


productTable = db['products']


@router.post('/product', response_description='Add a new product', response_model=Product)
def create_product(req: Product, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    product = productTable.find_one({'name': req.name})
    if product:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail={'msg': 'Product already exist!'})
    category = categoryTable.find_one({'name': req.category})
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'Category does not exist!'})
    try:
        product_object = req.dict()
        product_id_ref = productTable.insert_one(product_object)
        new_product = productTable.find_one({"_id": product_id_ref.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=product_serializer(new_product))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str)


@router.get('/products', response_description='get all products')
def get_all_products(page: int, current_user: User = Depends(oauth2.get_current_user)):
    try:
        """users = productTable.find({})
        users_list = [user for user in users]
        return users_list"""
        products = list(productTable.find({}).skip((page-1) * 20).limit(20))
        res = {
            "products": [product_serializer(product) for product in products],
            "total": productTable.count_documents({}),
            "page": page,
            "limit": 20
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete('/product/{product_id}', response_description='Delete a product', response_model=Product)
def delete_product(product_id: str, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        product = productTable.find_one({'_id': ObjectId(product_id)})
        if product:
            productTable.delete_one({'_id': ObjectId(product_id)})
            return JSONResponse(status_code=status.HTTP_200_OK, content=product_serializer(product))
        else: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'No such product to delete!'})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.put('/product/{product_id}', response_description='Update a product', response_model=Product)
def update_product(product_id: str, req: Product, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        product = productTable.find_one({'_id': ObjectId(product_id)})
        if product:
            updated_result = productTable.update_one({'_id': ObjectId(product_id)}, {'$set': req.dict()})
            if updated_result.matched_count != 0:
                updated_product = productTable.find_one({"_id": ObjectId(product_id)})
                return JSONResponse(status_code=status.HTTP_200_OK, content=product_serializer(updated_product))
            else: 
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'msg': 'Product failed to be updated!'})
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'No such product to update'})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.get('/product/{product_id}', response_description='get a single product', response_model=Product)
def get_product(product_id: str, current_user: User = Depends(oauth2.get_current_user)):
    try:
        product = productTable.find_one({'_id': ObjectId(product_id)})
        if product:
                return JSONResponse(status_code=status.HTTP_200_OK, content=product_serializer(product))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'Product not found!'})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    
@router.get('/products/bycat/{category_id}', response_description='Get products by category')
def get_products_bycat(category_id: str, current_user: User = Depends(oauth2.get_current_user)):
    try:
        category = categoryTable.find_one({"_id": ObjectId(category_id)})
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "Category does not exist!"})
        products = list(productTable.find({"category": category["name"]}))
        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": f"No product in {category['name']} category!"})
        res = {
            "products": [product_serializer(product) for product in products]
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post('/products/search', response_description="search for a product")
def search_products(keyword: str, current_user: User = Depends(oauth2.get_current_user)):
    try:
        products = list(productTable.find({"name": {"$regex": f".*{keyword}.*", "$options": "i"}}))
        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": f"No product with the keyword: {keyword}!"})
        res = {
            "products": [product_serializer(product) for product in products]
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.put('/product/stock/{product_id}', response_description="Update the quantity of a product in stock")
def update_stock(product_id: str, quantity: int, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        product = productTable.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"msg": "No product found!"})
        modified_result = productTable.update_one({"_id": ObjectId(product_id)}, {"$set": {"quantity": int(product["quantity"]) + quantity}}) 
        if modified_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"msg": "Stock not updated!"})
        modified_product = productTable.find_one({"_id": ObjectId(product_id)})
        return JSONResponse(status_code=status.HTTP_200_OK, content=product_serializer(modified_product))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    