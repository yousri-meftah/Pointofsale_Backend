from fastapi import FastAPI
import uvicorn
from api.v1 import employee,auth , session, product, order,dashboard, order_line, customer , category , pricelist , program , program_item , pricelist_line


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title='PointOfSell',
    description='FastApi PointOfSell Project',
    version='1.0.0',
    docs_url='/',
)
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#finished
app.include_router(employee.router, prefix="/employee", tags=["employee"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(product.router, prefix="/products", tags=["products"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(category.router, prefix="/categories", tags=["categories"])
app.include_router(program.router, prefix="/programs", tags=["programs"])
app.include_router(session.router, prefix="/sessions", tags=["sessions"])





#not yet
app.include_router(order.router, prefix="/orders", tags=["orders"]) #create order is done , but this module should be the last one to be done


#app.include_router(order_line.router, prefix="/order_lines", tags=["order lines"])
app.include_router(customer.router, prefix="/customers", tags=["customers"])

app.include_router(pricelist.router, prefix="/pricelists", tags=["pricelists"])

#[TODO] still don't know what are the functions should be here
#app.include_router(program_item.router, prefix="/program_items", tags=["program items"])


app.include_router(pricelist_line.router, prefix="/pricelist" , tags=["pricelist lines"])




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
