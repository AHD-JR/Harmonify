from fastapi import HTTPException, status, Depends
from app.utils import jwt, oauth2

def is_admin(token: str = Depends(oauth2.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail={'msg': 'User is not an admin!'}, 
        headers={"WWW-Authenticate": "Bearer"}
    )
    token_data = jwt.decode_token(token, credentials_exception)
    role = token_data['info']['role']
    if role == 0:
        raise credentials_exception
    return True