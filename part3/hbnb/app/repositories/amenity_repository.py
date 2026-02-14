from app.extensions import db
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository
from app.models.amenity import Amenity


class AmenityRepository(SQLAlchemyRepository):
    def init(self):
        super().init(Amenity)

    def get_by_name(self, name):
        return self.model.query.filter_by(name=name).first()
