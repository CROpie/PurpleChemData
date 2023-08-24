from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from .. import models


def get_locations_list(db: Session, user_id: int):
    locationsList = (
        db.query(models.Location)
        .filter(models.Location.user_id == user_id)
        .options(selectinload(models.Location.user))
        .all()
    )
    return locationsList


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


def remove_location(db: Session, user_id: int, location_id: int):
    rm_location = (
        db.query(models.Location)
        .filter(models.Location.user_id == user_id, models.Location.id == location_id)
        .first()
    )

    if not rm_location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(rm_location)
    db.commit()
