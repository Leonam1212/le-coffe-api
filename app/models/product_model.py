from dataclasses import dataclass

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.configs.database import db
from app.models.feedback_model import FeedbackModel
from app.models.region_model import RegionModel


@dataclass
class ProductModel(db.Model):
    product_id: int
    name: str
    price: float
    description: str
    category: str
    feedbacks: list[FeedbackModel]
    region: RegionModel
    
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    category = Column(String)
    latitude = Column(String)
    longitude = Column(String)

    region_id = Column(Integer, ForeignKey("regions.id"))

    region = relationship("RegionModel", back_populates="products", uselist=False)
    feedbacks = relationship("FeedbackModel", back_populates="product", cascade="all, delete")