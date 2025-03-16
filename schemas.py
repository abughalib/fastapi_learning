from sqlmodel import Relationship, SQLModel, Field, VARCHAR, Column
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"])


class TripInput(SQLModel):
    start: int
    end: int
    description: str


class TripOutput(TripInput):
    id: int


class Trip(TripInput, table=True):
    id: int | None = Field(default=None, primary_key=True)
    car_id: int = Field(foreign_key="car.id")
    car: "Car" = Relationship(back_populates="trips")


class CarInput(SQLModel):
    size: str
    fuel: str = "Diesel"
    doors: int
    transmission: str = "Auto"


class Car(CarInput, table=True, tablename="Cars"):
    id: int | None = Field(default=None, primary_key=True)
    trips: list[Trip] = Relationship(
        back_populates="car", sa_relationship_kwargs={"lazy": "selectin"}
    )


class CarOutput(CarInput):
    id: int
    trips: list[TripOutput] = []


class User(SQLModel, table=True, tablename="Users"):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=Column(
            "username", VARCHAR(50), nullable=False, unique=True, index=True
        )
    )
    password_hash: str = Field(default="")

    def set_password(self, password: str):
        """Generates a password hash."""

        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verifies a password against the stored password hash."""

        return pwd_context.verify(password, self.password_hash)


class UserOutput(SQLModel):
    id: int
    username: str


class UserSignUp(SQLModel):
    username: str
    password: str
