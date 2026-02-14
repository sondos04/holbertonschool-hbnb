from app.extensions import db
from app.models.base_model import BaseModel


class Amenity(BaseModel):
    __tablename__ = "amenities"

    name = db.Column(db.String(50), nullable=False, unique=True)
##
##    places = db.relationship(
##        "Place",
##        secondary=place_amenity,
##        back_populates="amenities"
##    )
##
##    def to_dict(self):
##        return {
##            "id": self.id,
##            "name": self.name,
##            "created_at": self.created_at.isoformat() if self.created_at else None,
##            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
##        }
##
