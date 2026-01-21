from app.models.amenity import Amenity
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


class AmenityRepository(SQLAlchemyRepository):
    def __init__(self, session):
        super().__init__(session, Amenity)

    def get_by_name(self, name):
        """Get amenity by name"""
        return self.session.query(Amenity).filter_by(name=name).first()
