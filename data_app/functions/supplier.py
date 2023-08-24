from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from .. import models
from ..schemas import SupplierIn, Supplier


def add_new_supplier(db: Session, supplier: SupplierIn):
    db_supplier = models.Supplier(
        supplierName=supplier.supplierName,
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


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


def patch_supplier_details(db: Session, supplier: Supplier):
    patch_supplier = (
        db.query(models.Supplier).filter(models.Supplier.id == supplier.id).first()
    )

    if not patch_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    patch_supplier.supplierName = supplier.supplierName
    db.commit()


def remove_supplier(db: Session, id: int):
    rm_supplier = db.query(models.Supplier).filter(models.Supplier.id == id).first()

    if not rm_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    db.delete(rm_supplier)
    db.commit()
