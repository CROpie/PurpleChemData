from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models
from ..schemas.input import NewUser, NewSupplier
from ..schemas.admin import PatchChemical, PatchOrder


### CREATE A NEW USER ###
def check_duplicate_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"{user.username} is already in the database.",
        )


def add_new_user(db: Session, user: NewUser):
    db_user = models.User(id=user.id, username=user.username, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


### ADD A SUPPLIER ###
def check_duplicate_supplier(db: Session, supplierName: str):
    supplier = (
        db.query(models.Supplier)
        .filter(models.Supplier.supplierName == supplierName)
        .first()
    )
    if supplier:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"{supplier.supplierName} is already in the database.",
        )


def add_new_supplier(db: Session, supplier: NewSupplier):
    db_supplier = models.Supplier(
        supplierName=supplier.supplierName,
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


### PATCH STATUS ###
def patch_order_status(db: Session, id: int, status: str):
    patch_order = db.query(models.Order).filter(models.Order.id == id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found")

    patch_order.status = status
    db.commit()


### PATCH USER ###
def patch_user_details(db: Session, id: int, full_name: str):
    patch_user = db.query(models.User).filter(models.User.id == id).first()

    if not patch_user:
        raise HTTPException(status_code=404, detail="User not found")

    patch_user.full_name = full_name
    db.commit()


### PATCH CHEMICAL ###
def patch_chemical_details(db: Session, chemical: PatchChemical):
    patch_chemical = (
        db.query(models.Chemical).filter(models.Chemical.id == chemical.id).first()
    )

    if not patch_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    patch_chemical.CAS = chemical.CAS
    patch_chemical.chemicalName = chemical.chemicalName
    patch_chemical.MW = chemical.MW
    patch_chemical.MP = chemical.MP
    patch_chemical.BP = chemical.BP
    patch_chemical.density = chemical.density
    db.commit()


### PATCH SUPPLIER ###
def patch_supplier_details(db: Session, id: int, supplierName: str):
    patch_supplier = db.query(models.Supplier).filter(models.Supplier.id == id).first()

    if not patch_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    patch_supplier.supplierName = supplierName
    db.commit()


### PATCH ORDER ###
def patch_order_details(db: Session, order: PatchOrder):
    patch_order = db.query(models.Order).filter(models.Order.id == order.id).first()

    if not patch_order:
        raise HTTPException(status_code=404, detail="Order not found")

    patch_order.amount = order.amount
    patch_order.amountUnit = order.amountUnit
    patch_order.isConsumed = order.isConsumed
    patch_order.supplierPN = order.supplierPN
    db.commit()


### DELEETE USER
def delete_user_details(db: Session, id: int):
    to_delete_user = db.query(models.User).filter(models.User.id == id).first()

    if not to_delete_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(to_delete_user)
    db.commit()


### DELETE SUPPLIER ###
def delete_supplier_details(db: Session, id: int):
    to_delete_supplier = (
        db.query(models.Supplier).filter(models.Supplier.id == id).first()
    )

    if not to_delete_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    db.delete(to_delete_supplier)
    db.commit()


### DELETE CHEMICAL ###
def delete_chemical_details(db: Session, id: int):
    to_delete_chemical = (
        db.query(models.Chemical).filter(models.Chemical.id == id).first()
    )

    if not to_delete_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    db.delete(to_delete_chemical)
    db.commit()


### DELETE ORDER ###
def delete_order_details(db: Session, id: int):
    to_delete_order = db.query(models.Order).filter(models.Order.id == id).first()

    if not to_delete_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(to_delete_order)
    db.commit()
