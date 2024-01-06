from fastapi import FastAPI
from app.db import client
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.product import router as product_router
from app.api.category import router as category_router
from app.api.order import router as order_router
from app.api.summary import router as summary_router



app = FastAPI()

try:
    client.server_info()
    print("Connected to MongoDB 🚀")
except:
    print("Could not connect to MongoDB")


@app.get('/')
def get_root():
    return {'msg': 'Up and running...'}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(order_router)
app.include_router(summary_router)