from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.schema import Category, User
from app.db import db
from app.serializers import category_serializer
from bson import ObjectId
from app.utils import oauth2, permissions

router = APIRouter(
    prefix='/api',
    tags=['Category']
)


categoryTable = db['categories']


@router.post('/category', response_description='Add category', response_model=Category)
def create_category(req: Category, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        category = categoryTable.find_one({'name': req.name})
        if category:
            raise HTTPException(status_code=status.HTTP_226_IM_USED, detail={'msg': 'Category already exists'})
        category_object = req.dict()
        category_id_ref = categoryTable.insert_one(category_object)
        new_categroy = categoryTable.find_one({'_id': category_id_ref.inserted_id})
        return JSONResponse(status_code=status.HTTP_200_OK, content=category_serializer(new_categroy))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.get('/categories', response_description='List of all categories')
def get_all_categories(page: int, current_user: User = Depends(oauth2.get_current_user)):
    try:
        categories = list(categoryTable.find({}).skip((page-1) * 10).limit(10))
        res = {
            "categories": [category_serializer(category) for category in categories],
            "total": categoryTable.count_documents({}),
            "page": page,
            "limit": 10
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
        """ catigories = categoryTable.find({})
        category_list = [category for category in catigories]
        return category_list"""
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    
@router.put('/category/{category_id}', response_description='Edit a category', response_model=Category)
def update_category(category_id: str, req: Category, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        category = categoryTable.find_one({'_id': ObjectId(category_id)})
        if category:
            updated_result = categoryTable.update_one({'_id': ObjectId(category_id)}, {'$set': req.dict()})
            if updated_result.modified_count != 0:
                updated_category = categoryTable.find_one({"_id": ObjectId(category_id)})
                return JSONResponse(status_code=status.HTTP_200_OK, content=category_serializer(updated_category))
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'msg': 'Can not update user!'})
        else: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'No such category to update!'})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    
@router.delete('/category/{category_id}', response_description='Delete an existing category', response_model=Category)
def delete_category(category_id: str, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        category = categoryTable.find_one({'_id': ObjectId(category_id)})
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'No such category to delete!'})
        categoryTable.delete_one({'_id': ObjectId(category_id)})
        return JSONResponse(status_code=status.HTTP_200_OK, content=category_serializer(category))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))