from fastapi import Depends, FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from typing import Annotated

from . import models
from .database import SessionLocal, engine

from .schemas.input import (
    NewUser,
    NewLocation,
    OutLocation,
    NewChemical,
    OutChemical,
    NewSupplier,
    NewOrder,
)
from .schemas.load import (
    LoadSupplier,
    LoadLocationsAndOrdersLists,
    LoadOrder,
    LoadUser,
    LoadLocation,
    LoadChemical,
)
from .schemas.admin import (
    PatchStatus,
    PatchUser,
    PatchChemical,
    PatchSupplier,
    PatchOrder,
    DeleteAny,
)
from .schemas.query import QueryOrder
from .schemas.inventory import PatchAmountLocation, OutPatchOrder
from .schemas.orderchemical import Chemical
from .schemas.csv import CSVUserData, CSVChemical, CSVSupplier, CSVOrder, CSVGlobal

from .functions.auth import validate_current_user, validate_current_admin
from .functions.orderchemical import (
    get_chemical_by_CAS,
    get_chemical_by_ChemName,
    add_new_chemical,
    add_new_order,
)
from .functions.inventory import (
    add_new_location,
    check_duplicate_location,
    get_locations_list,
    get_orders_list,
    force_status_received,
    patch_amount_andor_location,
    delete_location_details,
)
from .functions.admin import (
    add_new_user,
    check_duplicate_user,
    add_new_supplier,
    check_duplicate_supplier,
    patch_order_status,
    patch_user_details,
    patch_chemical_details,
    patch_supplier_details,
    patch_order_details,
    delete_user_details,
    delete_supplier_details,
    delete_chemical_details,
    delete_order_details,
)
from .functions.querydatabase import get_orders_list_by_query

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Allowing access from localhost frontend
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# -----USER PAGES----- #

## <- ORDER CHEMICAL -> ##


### LOAD FUNCTION ###
@app.get("/orderchemicalload/", response_model=list[LoadSupplier])
async def get_orderchemical_load(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    suppliersList = db.query(models.Supplier).all()
    data = suppliersList
    return data


### CHECK IF NON-COMMONCHEM CAS IS IN DATABASE ###
@app.get("/getchemicalbycas/", response_model=Chemical)
async def get_query_chemical(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
    CAS: str = Query(None),
):
    chemical = get_chemical_by_CAS(db=db, CAS=CAS)
    if not chemical:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT, detail="Not in the database."
        )
    data = chemical
    return data


### CHECK IF NON-COMMONCHEM CHEMICALNAME IS IN DATABASE ###
@app.get("/getchemicalbychemname/", response_model=Chemical)
async def get_query_chemical_name(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
    chemName: str = Query(None),
):
    chemical = get_chemical_by_ChemName(db=db, chemName=chemName)
    if not chemical:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT, detail="Not in the database."
        )
    data = chemical
    return data


### GET CHEMICAL ID OR ADD NEW CHEMICAL ###
@app.post("/addchemical/", response_model=OutChemical)
def add_chemical(
    chemicalData: NewChemical,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    chemical = get_chemical_by_CAS(db=db, CAS=chemicalData.CAS)

    if not chemical:
        chemical = add_new_chemical(db=db, chemical=chemicalData)

    data = chemical
    return data


### ORDER CHEMICAL ###
@app.post("/addorder/")
def add_order(
    orderData: NewOrder,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    add_new_order(db=db, user_id=current_user.id, order=orderData)


## <- INVENTORY -> ##


### LOAD FUNCTION ###
@app.get("/inventoryload/", response_model=LoadLocationsAndOrdersLists)
async def get_inventory_load(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    locationsList = get_locations_list(db=db, user_id=current_user.id)
    ordersList = get_orders_list(db=db, user_id=current_user.id)

    data = {"locationsList": locationsList, "ordersList": ordersList}
    return data


### ADD LOCATION ###
@app.post("/addlocation/", response_model=OutLocation)
def add_location(
    locationData: NewLocation,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    check_duplicate_location(
        db=db, locationName=locationData.locationName, user_id=current_user.id
    )

    location = add_new_location(
        db=db, locationName=locationData.locationName, user_id=current_user.id
    )
    data = location
    return data


### DELETE LOCATION ###
@app.delete("/deletelocation/")
def delete_location(
    location: DeleteAny,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    delete_location_details(db=db, user_id=current_user.id, location_id=location.id)


### FORCE STATUS UPDATE ###
@app.patch("/forcereceived/")
def patch_status_to_received(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
    query: str = Query(None),
):
    force_status_received(db=db, order_id=query)


### MODIFY AMOUNT AND/OR LOCATION ###
@app.patch("/patchamountlocation/", response_model=OutPatchOrder)
def modify_amount_andor_location(
    orderData: PatchAmountLocation,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    patched_order = patch_amount_andor_location(db=db, order=orderData)
    data = patched_order
    return data


## <- QUERY DATABASE -> ##


### QUERY BY STRING ###
@app.get("/getordersbyquery/", response_model=list[QueryOrder])
async def get_orders_by_query(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
    queryType: str = Query(None),
    queryString: str = Query(None),
):
    orders_list = get_orders_list_by_query(
        db=db, query_string=queryString, query_type=queryType
    )
    data = orders_list
    return data


# -----ADMIN PAGES----- #


### ADD THE FIRST USER (NO ADMIN REQUIRED) ###
@app.post("/seeddataadmin/")
def add_first_user(
    user: NewUser,
    db: Session = Depends(get_db),
):
    add_new_user(db=db, user=user)


### CREATE A NEW USER ###
@app.post("/adduser/")
def add_user(
    new_user: NewUser,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    check_duplicate_user(db, username=new_user.username)

    add_new_user(db=db, user=new_user)


### ADD A SUPPLIER ###
@app.post("/addsupplier/")
def add_supplier(
    supplierData: NewSupplier,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    check_duplicate_supplier(db=db, supplierName=supplierData.supplierName)

    add_new_supplier(db=db, supplier=supplierData)


### MODIFY ORDER LOAD ###
@app.get("/modifyorderload/", response_model=list[LoadOrder])
def get_order_load(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    ordersList = get_orders_list(db=db, user_id="all")

    data = ordersList
    return data


### MODIFY STATUS ###
@app.patch("/patchstatus/")
def patch_status(
    statusData: PatchStatus,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_order_status(db=db, id=statusData.id, status=statusData.status)


### MODIFY ORDER ###
@app.patch("/patchorder/")
def patch_status(
    orderData: PatchOrder,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_order_details(db=db, order=orderData)


### DELETE ORDER ###
@app.delete("/deleteorder/")
def delete_order(
    order: DeleteAny,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    delete_order_details(db=db, id=order.id)


### MODIFY USER LOAD ###
@app.get("/modifyuserload/", response_model=list[LoadUser])
def get_modify_user_load(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    usersList = db.query(models.User).all()

    data = usersList
    return data


### MODIFY USER ###
@app.patch("/patchuser/")
def patch_user(
    userData: PatchUser,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_user_details(db=db, id=userData.id, full_name=userData.full_name)


### DELETE USER ###
@app.delete("/deleteuser/")
def delete_user(
    user: DeleteAny,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    delete_user_details(db=db, id=user.id)


### MODIFY CHEMICAL LOAD ###
@app.get("/modifychemicalload/", response_model=list[LoadChemical])
def get_modify_chemical_load(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    chemicalList = db.query(models.Chemical).all()

    data = chemicalList
    return data


### MODIFY CHEMICAL ###
@app.patch("/patchchemical/")
def patch_user(
    chemicalData: PatchChemical,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_chemical_details(db=db, chemical=chemicalData)


### DELETE CHEIMCAL ###
@app.delete("/deletechemical/")
def delete_chemical(
    chemical: DeleteAny,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    delete_chemical_details(db=db, id=chemical.id)


### MODIFY SUPPLIER LOAD ###
@app.get("/modifysupplierload/", response_model=list[LoadSupplier])
def get_modify_supplier_load(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    supplierList = db.query(models.Supplier).all()

    data = supplierList
    return data


### MODIFY SUPPLIER ###
@app.patch("/patchsupplier/")
def patch_supplier(
    supplierData: PatchSupplier,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_supplier_details(
        db=db, id=supplierData.id, supplierName=supplierData.supplierName
    )


### DELETE SUPPLIER ###
@app.delete("/deletesupplier/")
def delete_supplier(
    supplier: DeleteAny,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    delete_supplier_details(db=db, id=supplier.id)


### ADD CSV FILE ###
@app.post("/csv/")
async def import_csv(
    csvData: CSVGlobal,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    userDataList = csvData.userDataList
    chemicalList = csvData.chemicalList
    supplierList = csvData.supplierList
    orderList = csvData.orderList
    for user in userDataList:
        db_user = (
            db.query(models.User).filter(models.User.username == user.username).first()
        )
        if not db_user:
            print(user)
            add_new_user(db=db, user=user)

    for chemical in chemicalList:
        db_chemical = (
            db.query(models.Chemical)
            .filter(models.Chemical.CAS == chemical.CAS)
            .first()
        )
        if not db_chemical:
            db_chemical = add_new_chemical(db=db, chemical=chemical)
        for order in orderList:
            if order.chemical == db_chemical.CAS:
                order.chemical = db_chemical.id

    for supplier in supplierList:
        db_supplier = (
            db.query(models.Supplier)
            .filter(models.Supplier.supplierName == supplier.supplierName)
            .first()
        )
        if not db_supplier:
            db_supplier = add_new_supplier(db=db, supplier=supplier)
        for order in orderList:
            if order.supplier == db_supplier.supplierName:
                order.supplier = db_supplier.id

    for order in orderList:
        db_order = models.Order(
            user_id=order.user,
            chemical_id=order.chemical,
            supplier_id=order.supplier,
            amount=order.amount,
            status=order.status,
            amountUnit=order.amountUnit,
            supplierPN=order.supplierPN,
        )
        db.add(db_order)
        db.commit()
