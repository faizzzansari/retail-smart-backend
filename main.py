from fastapi import FastAPI
from routes import products, billing, reports

app = FastAPI()

app.include_router(products.router)
app.include_router(billing.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"message": "RetailSmart Backend Running"}