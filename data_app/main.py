from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    OAuth2PasswordBearer,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from fastapi.responses import JSONResponse

from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import Annotated

from jose import JWTError, jwt

from dotenv import load_dotenv
import os

from . import models, schemas
from .database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


http_bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Allowing access from localhost frontend
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


### ENV ###

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")


### AUTHENTICATE A USER ###
# Returns the user if found in the database


async def validate_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = int(payload.get("sub"))
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    return user


###


## From the token, can retrieve the username and sent back their details
@app.get("/currentuser/", response_model=schemas.User)
async def return_current_user_info(
    current_user: Annotated[models.User, Depends(validate_current_user)]
):
    return current_user


@app.get("/allusers/", response_model=dict[str, list[schemas.User]])
async def return_all_users(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    if not current_user:
        return JSONResponse(content={"data": [], "error": "Validation failed."})
    usersList = db.query(models.User).all()
    return {"data": usersList}


### CREATE A NEW USER ###


def create_new_user(db: Session, user: schemas.User):
    db_user = models.User(username=user.username, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


@app.post("/users/", response_model=schemas.User)
def create_user(
    new_user: schemas.User,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    print("user: ", new_user)
    db_user = get_user_by_username(db, username=new_user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return create_new_user(db=db, user=new_user)


## Need a function to create the admin / first user


@app.post("/firstuser/", response_model=schemas.User)
def create_user(
    user: schemas.User,
    db: Session = Depends(get_db),
):
    return create_new_user(db=db, user=user)


### ADD A NEW CHEMICAL ###


def add_new_chemical(db: Session, chemical: schemas.Chemical):
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
    return db_chemical.id


def get_chemical_by_CAS(db: Session, CAS: str):
    chemical = db.query(models.Chemical).filter(models.Chemical.CAS == CAS).first()
    if chemical:
        return chemical.id


# check if present in the DB already, if not, add it.
# returns the chemical id to be used with placing an order
@app.post("/addchemical/", response_model=schemas.ChemicalResponse)
def add_chemical(
    chemicalData: schemas.Chemical,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    chemical_id = get_chemical_by_CAS(db=db, CAS=chemicalData.CAS)

    if not chemical_id:
        chemical_id = add_new_chemical(db=db, chemical=chemicalData)

    return {"data": chemical_id, "error": None}


### ADD A SUPPLIER ###


def add_new_supplier(db: Session, supplier: schemas.Supplier):
    db_supplier = models.Supplier(
        supplierName=supplier.supplierName,
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier.id


def get_supplier_by_name(db: Session, supplierName: str):
    supplier = (
        db.query(models.Supplier)
        .filter(models.Supplier.supplierName == supplierName)
        .first()
    )
    if supplier:
        return supplier.id


@app.post("/addsupplier/", response_model=schemas.SupplierResponse)
def add_supplier(
    supplierData: schemas.Supplier,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    supplier_id = get_supplier_by_name(db=db, supplierName=supplierData.supplierName)

    if not current_user:
        return {"error": "Failed authentication."}

    if supplier_id:
        return {"error": f"{supplierData.supplierName} is already in the database."}

    supplier_id = add_new_supplier(db=db, supplier=supplierData)

    return {"data": supplier_id, "error": None}


@app.get("/getsuppliers/", response_model=schemas.GetSuppliersResponse)
async def get_all_suppliers(
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    if not current_user:
        return {"error": "Failed authentication."}

    suppliersList = db.query(models.Supplier).all()
    return {"data": suppliersList}


### PLACE AN ORDER ###


def place_new_order(db: Session, user_id: int, order: schemas.Order):
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


@app.post("/placeorder/", response_model=schemas.OrderResponse)
def place_order(
    orderData: schemas.Order,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    if not current_user:
        return {"error": "Failed authentication."}

    db_order = place_new_order(db=db, user_id=current_user.id, order=orderData)

    return {"data": db_order, "error": None}


### ADD A LOCATION ###


def add_new_location(db: Session, locationName: str, user_id: int):
    db_location = models.Location(locationName=locationName, user_id=user_id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_location_by_name_and_user(db: Session, locationName: str, user_id: int):
    location = (
        db.query(models.Location)
        .filter(
            and_(
                models.Location.locationName == locationName,
                models.Location.user_id == user_id,
            )
        )
        .first()
    )
    return location


@app.post("/addlocation/", response_model=schemas.LocationResponse)
def add_location(
    locationData: schemas.Location,
    current_user: Annotated[models.User, Depends(validate_current_user)],
    db: Session = Depends(get_db),
):
    if not current_user:
        return {"error": "Failed authentication."}

    location = get_location_by_name_and_user(
        db=db, locationName=locationData.locationName, user_id=current_user.id
    )

    if location:
        return {
            "error": f"{location.locationName} is already in your list of locations."
        }

    location = add_new_location(
        db=db, locationName=locationData.locationName, user_id=current_user.id
    )

    return {"data": location, "error": None}


# @app.get("/getsuppliers/", response_model=schemas.GetSuppliersResponse)
# async def get_all_suppliers(
#     current_user: Annotated[models.User, Depends(validate_current_user)],
#     db: Session = Depends(get_db),
# ):
#     if not current_user:
#         return {"error": "Failed authentication."}

#     suppliersList = db.query(models.Supplier).all()
#     return {"data": suppliersList}
