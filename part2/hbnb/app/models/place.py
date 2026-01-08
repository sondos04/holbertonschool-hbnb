from app.models.BaseModel import BaseModel

class Place(BaseModel):
    def __init__(self, title, owner_id, description="", price_per_night=0):
        super().__init__()
        self.title = title
        self.owner_id = owner_id
        self.description = description
        self.price_per_night = price_per_night
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "title": self.title,
            "owner_id": self.owner_id,
            "description": self.description,
            "price_per_night": self.price_per_night
        })
        return data
