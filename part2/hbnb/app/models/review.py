from app.models.BaseModel import BaseModel

class Review(BaseModel):
    def __init__(self, text, user_id, place_id, rating=0):
        super().__init__()
        self.text = text
        self.user_id = user_id
        self.place_id = place_id
        self.rating = rating
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "text": self.text,
            "user_id": self.user_id,
            "place_id": self.place_id,
            "rating": self.rating
        })
        return data
