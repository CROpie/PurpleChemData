from fastapi import Depends, FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from typing import Annotated

from . import models
from .database import SessionLocal, engine

from .functions.auth import validate_current_user, validate_current_admin
from .functions.user import check_duplicate_user, add_new_user, patch_user_details
from .functions.chemical import (
    add_new_chemical,
    patch_chemical_details,
    remove_chemical,
)
from .functions.supplier import (
    check_duplicate_supplier,
    add_new_supplier,
    patch_supplier_details,
    remove_supplier,
)
from .functions.order import (
    get_orders_list,
    get_orders_list_by_query,
    add_new_order,
    patch_order_status,
    patch_order_details,
    remove_order,
)
from .functions.location import (
    get_locations_list,
    check_duplicate_location,
    add_new_location,
    remove_location,
)
from .functions.inventory2 import (
    patch_inventory_amount_location,
    patch_inventory_status,
)

from .schemas import (
    User,
    ChemOrderIn,
    Chemical,
    SupplierIn,
    Supplier,
    Order,
    LocationIn,
    Location,
    Inventory,
    InventoryPatchIn,
    InventoryPatch,
    QueryOrder,
)
from .csvschema import CSVGlobal

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

### GET: LOAD ###
# Admin #


@app.get("/userslist/", response_model=list[User])
def get_users(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    usersList = db.query(models.User).all()
    data = usersList
    return data


@app.get("/chemicalslist/", response_model=list[Chemical])
def get_chemicals(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    chemicalsList = db.query(models.Chemical).all()
    data = chemicalsList
    return data


@app.get("/orderslist/", response_model=list[Order])
def get_orders(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    ordersList = get_orders_list(db, user_id="all")
    data = ordersList
    return data


# User #
@app.get("/supplierslist/", response_model=list[Supplier])
def get_suppliers(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    suppliersList = db.query(models.Supplier).all()
    data = suppliersList
    return data


@app.get("/inventory/", response_model=Inventory)
async def get_inventory_lists(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    locationsList = get_locations_list(db=db, user_id=current_user.id)
    ordersList = get_orders_list(db=db, user_id=current_user.id)

    data = {"locationsList": locationsList, "ordersList": ordersList}
    return data


### GET: QUERY ###
# User #
@app.get("/chemicalquery/", response_model=Chemical)
def get_chemical(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
    query: str = Query(None),
    type: str = Query(None),
):
    if type == "CAS":
        chemical = (
            db.query(models.Chemical).filter(models.Chemical.CAS == query).first()
        )

    if type == "chemicalName":
        chemical = (
            db.query(models.Chemical)
            .filter(models.Chemical.chemicalName == query)
            .first()
        )

    if not chemical:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Not in the database.",
        )

    data = chemical
    return data


## rather than sending back all data of each order, just sends the essential
@app.get("/ordersquery/", response_model=list[QueryOrder])
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


### POST ###
# Seed #
@app.post("/seeddataadmin/")
def add_first_user(
    user: User,
    db: Session = Depends(get_db),
):
    add_new_user(db=db, user=user)


# Admin #
@app.post("/user/")
def add_user(
    new_user: User,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    check_duplicate_user(db, username=new_user.username)

    add_new_user(db=db, user=new_user)


@app.post("/supplier/")
def add_supplier(
    supplierData: SupplierIn,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    check_duplicate_supplier(db=db, supplierName=supplierData.supplierName)

    add_new_supplier(db=db, supplier=supplierData)


# User #


@app.post("/order/")
def add_order(
    chemOrderData: ChemOrderIn,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    ## Add the chemical to the database if not already present
    ## Get the chemical id, use it with orderData to add the order to the database

    chemicalData = chemOrderData.chemicalData
    orderData = chemOrderData.orderData

    chemical = chemical = (
        db.query(models.Chemical)
        .filter(models.Chemical.CAS == chemicalData.CAS)
        .first()
    )

    if not chemical:
        chemical = add_new_chemical(db=db, chemical=chemicalData)

    orderData.chemical_id = chemical.id

    add_new_order(db=db, user_id=current_user.id, order=orderData)


@app.post("/location/", response_model=Location)
def add_location(
    locationData: LocationIn,
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


### PATCH ###
# Admin #
@app.patch("/user/")
def patch_user(
    user: User,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_user_details(db=db, user=user)


@app.patch("/chemical/")
def patch_chemical(
    chemical: Chemical,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_chemical_details(db=db, chemical=chemical)


@app.patch("/supplier/")
def patch_supplier(
    supplier: Supplier,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_supplier_details(db=db, supplier=supplier)


@app.patch("/order/")
def patch_order(
    order: Order,
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
):
    patch_order_details(db=db, order=order)


@app.patch("/orderstatus/")
def patch_status(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
    order_id: int = Query(None),
    status: str = Query(None),
):
    patch_order_status(db=db, id=order_id, status=status)


# User #
@app.patch("/inventorystatus/")
def modify_inventory_status(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
    order_id: str = Query(None),
):
    patch_inventory_status(db=db, order_id=order_id)


@app.patch("/inventory/", response_model=InventoryPatch)
def modify_inventory_amount_location(
    orderData: InventoryPatchIn,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    patched_order = patch_inventory_amount_location(db=db, order=orderData)
    data = patched_order
    return data


### DELETE ###
# Admin #

# @app.delete("/user/")


@app.delete("/supplier/")
def delete_supplier(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
    supplier_id: int = Query(None),
):
    remove_supplier(db=db, id=supplier_id)


@app.delete("/chemical/")
def delete_chemical(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
    chemical_id: int = Query(None),
):
    remove_chemical(db=db, id=chemical_id)


@app.delete("/order/")
def delete_order(
    current_user: Annotated[models.User, Depends(validate_current_admin)],
    db: Session = Depends(get_db),
    order_id: int = Query(None),
):
    remove_order(db=db, id=order_id)


# User #
@app.delete("/location/")
def delete_location(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
    location_id: int = Query(None),
):
    remove_location(db=db, user_id=current_user.id, location_id=location_id)


### IMPORT CSV ###


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
