from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from .. import models
from ..schemas import ChemicalIn, Chemical


def add_new_chemical(db: Session, chemical: ChemicalIn):
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


def patch_chemical_details(db: Session, chemical: Chemical):
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


def remove_chemical(db: Session, id: int):
    rm_chemical = db.query(models.Chemical).filter(models.Chemical.id == id).first()

    if not rm_chemical:
        raise HTTPException(status_code=404, detail="Chemical not found")

    db.delete(rm_chemical)
    db.commit()
