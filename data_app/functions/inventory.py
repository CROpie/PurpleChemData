from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_

from .. import models
from ..schemas.inventory import PatchAmountLocation


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
    print("user_id: ", user_id)

    if user_id == "all":
        ordersList = (
            db.query(models.Order)
            .options(
                selectinload(models.Order.user),
                selectinload(models.Order.chemical),
                selectinload(models.Order.supplier),
                selectinload(models.Order.location),
            )
            .all()
        )
    else:
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


### DELETE LOCATION ###
def delete_location_details(db: Session, user_id: int, location_id: int):
    to_delete_location = (
        db.query(models.Location)
        .filter(models.Location.user_id == user_id, models.Location.id == location_id)
        .first()
    )

    if not to_delete_location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(to_delete_location)
    db.commit()


### PATCH AMOUNT AND/OR LOCATION ###
def patch_amount_andor_location(db: Session, order: PatchAmountLocation):
    patch_order = db.query(models.Order).filter(models.Order.id == order.id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found")

    patch_order.amount = order.amount
    patch_order.location_id = order.location_id
    patch_order.isConsumed = order.isConsumed
    db.commit()
    print("after commit: ", patch_order)
    return patch_order


### PATCH STATUS TO RECEIVED ###
def force_status_received(db: Session, order_id: int):
    print("order_id: ", order_id)
    patch_order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found")

    patch_order.status = "received"
    db.commit()
