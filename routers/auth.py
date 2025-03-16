from fastapi.security import (
    HTTPBasic,
    # HTTPBasicCredentials,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import select
from schemas import UserOutput, User
from typing import Annotated
from starlette import status
from db import get_session


security = HTTPBasic()


URL_PREFIX = "/auth"
auth_router = APIRouter(prefix=URL_PREFIX, tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{URL_PREFIX}/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserOutput:

    query = select(User).where(User.username == token)
    user = (await session.exec(query)).one_or_none()

    if user:
        return UserOutput.model_validate(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


@auth_router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    query = select(User).where(User.username == form_data.username)

    user = (await session.exec(query)).one_or_none()

    if user and user.verify_password(form_data.password):
        return {"access_token": user.username, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


# async def get_current_user(
#     credentials: Annotated[HTTPBasicCredentials, Depends(security)],
#     session: Annotated[AsyncSession, Depends(get_session)],
# ) -> UserOutput:

#     query = select(User).where(User.username == credentials.username)
#     user = (await session.exec(query)).one_or_none()

#     if user and user.verify_password(credentials.password):
#         return UserOutput.model_validate(user)
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#         )
