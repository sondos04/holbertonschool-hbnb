from app.models.BaseModel import BaseModel
from app.models.user import User
from app.models.place import Place


class Review(BaseModel):
    """Represents a review in the HBnB"""

    def __init__(self, text, rating, place, user):
        super().__init__()

        # text
        if not isinstance(text, str):
            raise TypeError("text must be a string.")
        text = text.strip()
        if not text:
            raise ValueError("review text is required.")

        # rating
        if not isinstance(rating, int):
            raise TypeError("rating must be an integer.")
        if not (1 <= rating <= 5):
            raise ValueError("rating must be between 1 and 5.")

        # place
        if not isinstance(place, Place):
            raise TypeError("place must be a Place instance.")

        # --- user ---
        if not isinstance(user, User):
            raise TypeError("user must be a User instance.")

        self.text = text
        self.rating = rating
        self.place = place
        self.user = user

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "rating": self.rating,
            "user_id": self.user.id,
            "place_id": self.place.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
