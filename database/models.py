import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Text, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from database.engine import Base
import enum

class OrderStatus(enum.Enum):
    PENDING = "Kutilyapti"
    ACCEPTED = "Tasdiqlandi"
    REJECTED = "Rad etildi"
    DELIVERED = "Yetkazib berildi"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)  # Telegram ID
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)  # Ombordagi soni
    image_id = Column(String, nullable=True)  # Telegramdagi rasmning file_id si
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    category = relationship("Category", back_populates="products")

class CartItem(Base):
    __tablename__ = 'cart_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    
    user = relationship("User")
    product = relationship("Product")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total_price = Column(Float, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    delivery_type = Column(String, nullable=False) # Olib ketish yoki Yetkazib berish
    payment_type = Column(String, nullable=False) # Naqd, Click, Payme
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False) # Sotib olingan paytdagi narx
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
