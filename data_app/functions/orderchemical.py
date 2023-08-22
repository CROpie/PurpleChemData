from sqlalchemy.orm import Session

from .. import models
from ..schemas.input import NewChemical, NewOrder


def get_chemical_by_ChemName(db: Session, chemName: str):
    chemical = (
        db.query(models.Chemical)
        .filter(models.Chemical.chemicalName == chemName)
        .first()
    )
    if chemical:
        return chemical


### GET CHEMICAL ID OR ADD NEW CHEMICAL ###
def get_chemical_by_CAS(db: Session, CAS: str):
    chemical = db.query(models.Chemical).filter(models.Chemical.CAS == CAS).first()
    if chemical:
        return chemical


def add_new_chemical(db: Session, chemical: NewChemical):
    db_chemical = models.Chemical(
        CAS=chemical.CAS,
        chemicalName=chemical.chemicalName,
        MW=chemical.MW,
        MP=chemical.MP,
        BP=chemical.BP,
        density=chemical.density,
        smile=chemical.smile,
        inchi=chemical.inchi,
    )
    db.add(db_chemical)
    db.commit()
    db.refresh(db_chemical)
    return db_chemical


### ORDER CHEMICAL ###
def add_new_order(db: Session, user_id: int, order: NewOrder):
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
