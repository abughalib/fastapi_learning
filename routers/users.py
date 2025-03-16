from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas import User, UserOutput, UserSignUp
from routers.auth import get_current_user
from typing import Annotated
from sqlmodel import select
from db import get_session

user_router = APIRouter(prefix="/api/users", tags=["users"])


@user_router.get("/me")
async def get_me(user: Annotated[UserOutput, Depends(get_current_user)]):
    """Get current user"""

    return user


@user_router.post("/signup")
async def signup(
    session: Annotated[AsyncSession, Depends(get_session)], user: UserSignUp
):
    """Sign up a new user"""

    try:
        new_user = User.model_validate(user)

        # Check if user already exists

        query = select(User).where(User.username == user.username)
        existing_user = (await session.exec(query)).one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )

        new_user.set_password(user.password)
        session.add(new_user)
        await session.commit()

        await session.refresh(new_user)
        return UserOutput.model_validate(new_user)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not able to add user"
        )
