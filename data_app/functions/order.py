from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, selectinload

from .. import models
from ..schemas import OrderIn, Order


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


def get_orders_list_by_query(db: Session, query_string: str, query_type: str):
    if query_type == "string":
        ordersList = (
            db.query(models.Order, models.Chemical, models.User, models.Supplier)
            .join(models.Chemical, models.Order.chemical_id == models.Chemical.id)
            .join(models.User, models.Order.user_id == models.User.id)
            .join(models.Supplier, models.Order.supplier_id == models.Supplier.id)
            .filter(
                or_(
                    models.Chemical.chemicalName.ilike(f"%{query_string}%"),
                    models.User.full_name.ilike(f"%{query_string}%"),
                    models.Chemical.CAS.ilike(f"%{query_string}%"),
                )
            )
            .options(
                selectinload(models.Order.user),
                selectinload(models.Order.chemical),
                selectinload(models.Order.supplier),
                selectinload(models.Order.location),
            )
            .all()
        )

    if query_type == "structure":
        ordersList = (
            db.query(models.Order, models.Chemical, models.User, models.Supplier)
            .join(models.Chemical, models.Order.chemical_id == models.Chemical.id)
            .join(models.User, models.Order.user_id == models.User.id)
            .join(models.Supplier, models.Order.supplier_id == models.Supplier.id)
            .filter(models.Chemical.inchi == query_string)
            .options(
                selectinload(models.Order.user),
                selectinload(models.Order.chemical),
                selectinload(models.Order.supplier),
                selectinload(models.Order.location),
            )
            .all()
        )

    ## ordersList is a list of tuples
    # [ ( <models.Order object>, <models.Chemical object> ), ... ]
    # for order, chemical in ordersList:
    # each iteration, the models.Order object gets mapped to order,
    # and the models.Chemical object gets mapped to chemical

    # Manually combining the data into a list of dictionaries
    formatted_orders_list = []

    for order, chemical, user, supplier in ordersList:
        formatted_order = {
            "id": order.id,
            "amount": order.amount,
            "amountUnit": order.amountUnit,
            "isConsumed": order.isConsumed,
            "status": order.status,
            "supplierPN": order.supplierPN,
            "orderDate": order.orderDate,
            "CAS": chemical.CAS,
            "chemicalName": chemical.chemicalName,
            "full_name": user.full_name,
            "supplierName": supplier.supplierName,
        }

        formatted_orders_list.append(formatted_order)
    return formatted_orders_list


def add_new_order(db: Session, user_id: int, order: OrderIn):
    db_order = models.Order(
        user_id=user_id,
        chemical_id=order.chemical_id,
        supplier_id=order.supplier_id,
        amount=order.amount,
        amountUnit=order.amountUnit,
        supplierPN=order.supplierPN,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def patch_order_status(db: Session, id: int, status: str):
    patch_order = db.query(models.Order).filter(models.Order.id == id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found")

    patch_order.status = status
    db.commit()


def patch_order_details(db: Session, order: Order):
    patch_order = db.query(models.Order).filter(models.Order.id == order.id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found")

    patch_order.amount = order.amount
    patch_order.amountUnit = order.amountUnit
    patch_order.isConsumed = order.isConsumed
    patch_order.supplierPN = order.supplierPN
    db.commit()


def remove_order(db: Session, id: int):
    rm_order = db.query(models.Order).filter(models.Order.id == id).first()

    if not rm_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(rm_order)
    db.commit()
