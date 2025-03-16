from fastapi import Depends, HTTPException, APIRouter, status, Response
from schemas import Car, CarInput, CarOutput, Trip, TripInput, User
from sqlmodel.ext.asyncio.session import AsyncSession
from routers.auth import get_current_user
from typing import Annotated, Sequence
from sqlmodel import select
from db import get_session


car_router = APIRouter(prefix="/api/cars", tags=["cars"])


class BadTripException(Exception):
    pass


@car_router.get("/")
async def get_all_cars(
    session: Annotated[AsyncSession, Depends(get_session)],
    size: str | None = None,
    doors: int | None = None,
) -> Sequence[Car]:
    """Get a list of all the Cars"""

    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors >= doors)
    cars = await session.exec(query)

    return cars.fetchall()


@car_router.get("/{id}")
async def get_car(
    session: Annotated[AsyncSession, Depends(get_session)], id: int
) -> CarOutput:
    """Get a car by id"""

    car = await session.get(Car, id)

    if car:
        return CarOutput.model_validate(car)
    else:
        raise HTTPException(status_code=404, detail="Car not found")


@car_router.post("/", response_model=CarOutput)
async def add_car(
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
    car: CarInput,
    response: Response,
) -> Car:
    """Add a car"""

    try:
        new_car = Car.model_validate(car)
        session.add(new_car)
        await session.commit()
        await session.refresh(new_car)
        response.status_code = status.HTTP_201_CREATED
        return new_car
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Not able add car")


@car_router.post("/{car_id}/trips")
async def add_trip(
    session: Annotated[AsyncSession, Depends(get_session)], car_id: int, trip: TripInput
) -> Trip:
    """Add a trip"""

    car = await session.get(Car, car_id)

    if car:
        new_trip = Trip.model_validate(trip, update={"car_id": car_id})
        if new_trip.end < new_trip.start:
            raise BadTripException("Trip end before start")
        car.trips.append(new_trip)
        await session.commit()
        await session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@car_router.delete("/{id}", status_code=204)
async def remove_car(
    session: Annotated[AsyncSession, Depends(get_session)], id: int, response: Response
) -> None:

    car = await session.get(Car, id)

    if car:
        await session.delete(car)
        await session.commit()
        response.status_code = status.HTTP_200_OK
        return
    else:
        raise HTTPException(status_code=404, detail=f"Car not found with id={id}")


@car_router.put("/{id}")
async def change_car(
    session: Annotated[AsyncSession, Depends(get_session)], id: int, new_data: CarInput
) -> Car:

    car = await session.get(Car, id)

    if car:
        car.fuel = new_data.fuel
        car.transmission = new_data.transmission
        car.doors = new_data.doors
        car.size = new_data.size
        await session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail=f"Car not found with id={id}")
