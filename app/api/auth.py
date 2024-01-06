from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.utils import jwt
from app.api.user import userTable
from app.utils.hashing import hash, verify
from app.serializers import user_serializer, try_user_serializer


router = APIRouter(
    tags= ['Authentication'],
    prefix= '/auth'
)


@router.post('/login', response_description='User login')
def login(req: OAuth2PasswordRequestForm = Depends()):
    admin = userTable.find_one({'role': 1})
    if admin is None:
        user = first_migration(req.username, req.password)
    else:
        user = userTable.find_one({'username': req.username})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'msg': 'Account not found!'})
        if not verify(req.password, user['password']):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={'msg': 'Incorrect password!'})
    
    
    access_token = jwt.create_access_token(data={'info': try_user_serializer(user)})

    res = {
        'access_token': access_token,
        'token_type': 'bearer'
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=res)

def first_migration(username: str, password: str):
    hashed_password = hash(password)
    first_migration_data = {
            "username": username,
            "password": hashed_password,
            "name": "First Migration",
            "role": 1
    }
    try:
        first_migration_ref = userTable.insert_one(first_migration_data)
        first_admin = userTable.find_one(first_migration_ref.inserted_id)
        JSONResponse(status_code=status.HTTP_200_OK, content=user_serializer(first_admin))
        return first_admin
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))