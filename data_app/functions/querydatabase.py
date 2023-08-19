from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from .. import models


def get_orders_list_query(db: Session, query: str):
    print("Inside function, query: ", query)
    ordersList = (
        db.query(models.Order, models.Chemical, models.User, models.Supplier)
        .join(models.Chemical, models.Order.chemical_id == models.Chemical.id)
        .join(models.User, models.Order.user_id == models.User.id)
        .join(models.Supplier, models.Order.supplier_id == models.Supplier.id)
        .filter(
            or_(
                models.Chemical.chemicalName.ilike(f"%{query}%"),
                models.User.full_name.ilike(f"%{query}%"),
                models.Chemical.CAS.ilike(f"%{query}%"),
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
            "fullname": user.full_name,
            "supplierName": supplier.supplierName,
        }

        formatted_orders_list.append(formatted_order)
    return formatted_orders_list

    # supplierName: str
