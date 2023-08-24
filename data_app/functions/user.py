from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from .. import models
from ..schemas import User


def check_duplicate_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"{user.username} is already in the database.",
        )


def add_new_user(db: Session, user: User):
    db_user = models.User(id=user.id, username=user.username, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def patch_user_details(db: Session, user: User):
    patch_user = db.query(models.User).filter(models.User.id == user.id).first()

    if not patch_user:
        raise HTTPException(status_code=404, detail="User not found")

    patch_user.full_name = user.full_name
    db.commit()
