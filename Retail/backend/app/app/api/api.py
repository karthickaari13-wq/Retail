from fastapi import APIRouter
from .endpoints import login,user,category,store,product,payment,dashboard,supplier,order
api_router = APIRouter()

api_router.include_router(login.router, tags=["Login"], prefix="/login")

api_router.include_router(user.router,tags=["User"],prefix="/user")

api_router.include_router(store.router,tags=["Store"],prefix="/store")

api_router.include_router(supplier.router,tags=["Supplier"],prefix="/supplier")


api_router.include_router(category.router,tags=["Category"],prefix="/category")



api_router.include_router(product.router,tags=["Product"],prefix="/product")

api_router.include_router(order.router,tags=["Order"],prefix="/order")

api_router.include_router(payment.router,tags=["Payment"],prefix="/payment")

api_router.include_router(dashboard.router,tags=["Dashboard"],prefix="/dashboard")















