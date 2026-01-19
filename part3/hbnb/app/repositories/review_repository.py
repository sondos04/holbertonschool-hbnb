from app.repositories.sqlalchemy_repository import SQLAlchemyRepository
from app.models.review import Review

class ReviewRepository(SQLAlchemyRepository):
	def __init__(self, session):
		super().__init__(session, Review)
	def get_by_user_and_place(self, user_id, place_id):
		return(
		self.session.query(Review)
		.filter(Review.user_id == user_id, Review.place_id == place_id)
		.first()
		)
