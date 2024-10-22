from fastapi import FastAPI
from routers import review

app = FastAPI()

app.include_router(review.router)
