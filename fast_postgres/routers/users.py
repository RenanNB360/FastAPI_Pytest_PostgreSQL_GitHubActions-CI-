from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_postgres.database import get_session
from fast_postgres.models import User
from fast_postgres.schema import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)
from fast_postgres.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_202_ACCEPTED, response_model=UserList)
async def read_users(
    session: T_Session,
    limit: int = 10,
    offset: int = 0,
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@router.get('/{user_id}', response_model=UserPublic)
def read_user(
    user_id: int,
    session: T_Session,
):
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Not Found'
        )

    return db_user


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permission',
        )

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = get_password_hash(user.password)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not enough permission',
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User Deleted'}


@router.post(
    '/', status_code=status.HTTP_201_CREATED, response_model=UserPublic
)
async def create_user(
    user: UserSchema,
    session: T_Session,
):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail='Method Not Allowed',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail='Method Not Allowed',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user
