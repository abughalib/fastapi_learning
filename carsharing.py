from routers.cars import car_router, BadTripException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from routers.users import user_router
from routers.auth import auth_router
from routers.web import web_router
from schemas import Car, Trip
from db import engine
import uvicorn


@asynccontextmanager
async def create_db_and_tables(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Car.metadata.create_all)
        await conn.run_sync(Trip.metadata.create_all)

    yield


app = FastAPI(title="Car Sharing", version="0.0.1", lifespan=create_db_and_tables)

app.include_router(car_router)
app.include_router(web_router)
app.include_router(user_router)
app.include_router(auth_router)


origins = [
    "http://localhost:8000",
    "http://localhost:8100",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BadTripException)
async def unicorn_exception_handler(
    request: Request, exc: BadTripException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "This trip is not possible"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8100)
