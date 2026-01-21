from sqlalchemy import Column, String
from app.models.base_model import Base, BaseModel


class Amenity(Base, BaseModel):
    __tablename__ = "amenities"

    name = Column(String(50), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
