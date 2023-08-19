from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models
from ..schemas.input import NewUser, NewSupplier


### CREATE A NEW USER ###
def check_duplicate_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail=f"{user.username} is already in the database.",
        )


def add_new_user(db: Session, user: NewUser):
    db_user = models.User(username=user.username, full_name=user.full_name)
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
    return db_supplier.id
