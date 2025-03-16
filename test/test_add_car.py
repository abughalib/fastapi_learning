from fastapi.testclient import TestClient
from routers.cars import add_car
from schemas import CarInput, User, Car
from unittest.mock import AsyncMock
from carsharing import app
import pytest


pytest_plugins = ("pytest_asyncio",)


client = TestClient(app)


def test_add_car():
    response = client.post(
        "/api/cars",
        json={"doors": 7, "size": "xxl"},
        headers={"Authorization": "Bearer abugh"},
    )

    assert response.status_code == 201
    car = response.json()
    assert car["doors"] == 7
    assert car["size"] == "xxl"


@pytest.mark.asyncio
async def test_add_car_with_mock_session():

    mock_session = AsyncMock()

    mock_response = AsyncMock()

    input = CarInput(doors=2, size="xl")

    user = User(username="abugh")

    result = await add_car(
        car=input, session=mock_session, user=user, response=mock_response
    )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert isinstance(result, Car)
    assert result.doors == 2
    assert result.size == "xl"
