from fastapi import FastAPI
from routes import products, billing, reports, user_routes
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.include_router(products.router)
app.include_router(billing.router)
app.include_router(reports.router)
app.include_router(user_routes.router)

if not os.path.exists("static/images"):
    os.makedirs("static/images")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "RetailSmart Backend Running"}