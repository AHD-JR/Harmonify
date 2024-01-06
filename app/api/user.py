from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.schema import User, GetUser
from app.db import db
from app.utils.hashing import hash
from bson import ObjectId
from app.serializers import user_serializer
from app.utils import oauth2, permissions

router = APIRouter(
    prefix='/api',
    tags=['User']
) 

userTable = db['users']


@router.post('/register', response_description="Add a user", response_model=User)
def create_user(req: User, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    user = userTable.find_one({'username': req.username})
    if user:
        raise HTTPException(status_code=status.HTTP_226_IM_USED, detail=f"{user['username']} is taken!!")
    try:
        user_object = req.dict()
        user_object['password'] = hash(user_object['password'])
        user_id_ref = userTable.insert_one(user_object)
        new_user = userTable.find_one({"_id": user_id_ref.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=user_serializer(new_user))
    #except DuplicateKeyError:
    #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{user_object['username']} exists!!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    
@router.get('/users', response_description='All usres')
def get_all_users(page: int, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):    
    try:
        """users = userTable.find({})
        users_list = [user for user in users]
        return users_list"""
        users = list(userTable.find({}).skip((page-1) * 10).limit(10))
        res = {
            "users": [user_serializer(user) for user in users],
            "total": userTable.count_documents({}),
            "pages": page,
            "limit": 10
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    
@router.get('/user/{user_id}', response_description='All users', response_model=GetUser)
def get_user(user_id: str, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        user = userTable.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User not found!')
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    
@router.delete('/user/{user_id}', response_description='Delete a user')
def delete_user(user_id: str, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        user = userTable.find_one({'_id': ObjectId(user_id)})
        if user:
            userTable.delete_one({'_id': ObjectId(user_id)})
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={'msg': 'User has been deleted!'})
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such user to delete!')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    
@router.put('/user/{user_id}', response_description='Update a user', response_model=User)
def update_user(user_id: str, req: User, current_user: User = Depends(oauth2.get_current_user), role: User = Depends(permissions.is_admin)):
    try:
        user = userTable.find_one({'_id': ObjectId(user_id)})
        if user:
            updated_result = userTable.update_one({'_id': ObjectId(user_id)}, {'$set': req.dict()})
            if updated_result.modified_count != 0:
                updated_user = userTable.find_one({"_id": ObjectId(user_id)})
                return JSONResponse(status_code=status.HTTP_201_CREATED, content=user_serializer(updated_user))
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'msg': 'Can not update user!'})
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'User not found!'})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))