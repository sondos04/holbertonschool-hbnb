from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.review_repository import ReviewRepository 
from app.repositories.amenity_repository import AmenityRepository

from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

class HBnBFacade:
    def __init__(self):
        self.session = SessionLocal()
        self.user_repo = UserRepository(self.session)
        self.place_repo = PlaceRepository(self.session)
        self.review_repo = ReviewRepository(self.session)
