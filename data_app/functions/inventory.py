from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_

from .. import models


### LOAD FUNCTION ###
def get_locations_list(db: Session, user_id: int):
    locationsList = (
        db.query(models.Location)
        .filter(models.Location.user_id == user_id)
        .options(selectinload(models.Location.user))
        .all()
    )
    return locationsList


def get_orders_list(db: Session, user_id: int):
    ordersList = (
        db.query(models.Order)
        .filter(models.Order.user_id == user_id)
        .options(
            selectinload(models.Order.user),
            selectinload(models.Order.chemical),
            selectinload(models.Order.supplier),
            selectinload(models.Order.location),
        )
        .all()
    )
    return ordersList


### ADD LOCATION ###
def add_new_location(db: Session, locationName: str, user_id: int):
    db_location = models.Location(locationName=locationName, user_id=user_id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def check_duplicate_location(db: Session, locationName: str, user_id: int):
    location = (
        db.query(models.Location)
        .filter(
            and_(
                models.Location.locationName == locationName,
                models.Location.user_id == user_id,
            )
        )
        .first()
    )
    if location:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"{location.locationName} is already in your list of locations.",
        )
