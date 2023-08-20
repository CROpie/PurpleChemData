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
from .schemas.load import LoadSupplier, LoadLocationsAndOrdersLists
from .schemas.query import QueryOrder
from .schemas.inventory import PatchOrder, OutPatchOrder
from .schemas.orderchemical import Chemical

from .functions.auth import validate_current_user
from .functions.orderchemical import (
    get_chemical_by_CAS,
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
)
from .functions.admin import (
    add_new_user,
    check_duplicate_user,
    add_new_supplier,
    check_duplicate_supplier,
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
    orderData: PatchOrder,
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
@app.post("/addfirstuser/")
def add_first_user(
    user: NewUser,
    db: Session = Depends(get_db),
):
    add_new_user(db=db, user=user)


### CREATE A NEW USER ###
@app.post("/adduser/")
def add_user(
    new_user: NewUser,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    check_duplicate_user(db, username=new_user.username)

    add_new_user(db=db, user=new_user)


### ADD A SUPPLIER ###
@app.post("/addsupplier/")
def add_supplier(
    supplierData: NewSupplier,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    check_duplicate_supplier(db=db, supplierName=supplierData.supplierName)

    add_new_supplier(db=db, supplier=supplierData)
