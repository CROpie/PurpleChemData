from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from .. import models
from ..schemas import InventoryPatch


def patch_inventory_amount_location(db: Session, order: InventoryPatch):
    patch_order = db.query(models.Order).filter(models.Order.id == order.id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found ??")

    patch_order.amount = order.amount
    patch_order.location_id = order.location_id
    patch_order.isConsumed = order.isConsumed
    db.commit()
    return patch_order


def patch_inventory_status(db: Session, order_id: int):
    print("order_id: ", order_id)
    patch_order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found")

    patch_order.status = "received"
    db.commit()
