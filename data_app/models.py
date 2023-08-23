from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Enum,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    full_name = Column(String)

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    location = relationship(
        "Location", back_populates="user", cascade="all, delete-orphan"
    )


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    locationName = Column(String)

    user_id = Column(Integer, ForeignKey("profiles.id"))
    user = relationship("User", back_populates="location")

    orders = relationship("Order", back_populates="location")


class Chemical(Base):
    __tablename__ = "chemicals"

    id = Column(Integer, primary_key=True, index=True)
    CAS = Column(String, unique=True)
    chemicalName = Column(String, nullable=True)
    MW = Column(String, nullable=True)
    MP = Column(String, nullable=True)
    BP = Column(String, nullable=True)
    density = Column(String, nullable=True)
    smile = Column(String, nullable=True)
    inchi = Column(String, nullable=True)

    orders = relationship(
        "Order", back_populates="chemical", cascade="all, delete-orphan"
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    supplierName = Column(String)

    orders = relationship(
        "Order", back_populates="supplier", cascade="all, delete-orphan"
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("profiles.id"))
    user = relationship("User", back_populates="orders")

    chemical_id = Column(Integer, ForeignKey("chemicals.id"))
    chemical = relationship("Chemical", back_populates="orders")

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    supplier = relationship("Supplier", back_populates="orders")

    location_id = Column(
        Integer, ForeignKey("locations.id"), nullable=True, default=None
    )
    location = relationship("Location", back_populates="orders")

    status = Column(Enum("submitted", "ordered", "received"), default="submitted")

    amount = Column(Integer)
    amountUnit = Column(Enum("mg", "mL", "g", "L"))
    isConsumed = Column(Boolean, default=False)
    orderDate = Column(DateTime, server_default=func.now())
    supplierPN = Column(String, nullable=True)
