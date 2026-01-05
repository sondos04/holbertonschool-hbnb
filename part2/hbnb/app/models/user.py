import re
from app.models.BaseModel import BaseModel

class User(BaseModel):
    """Represents a user in the HBnB"""

    def __init__(self, first_name: str, last_name: str, email: str, is_admin: bool = False):
        super().__init__()

        # Validation: first_name
        if not isinstance(first_name, str):
            raise TypeError("first_name must be a string.")
        first_name = first_name.strip()
        if not first_name:
            raise ValueError("first_name is required.")
        if len(first_name) > 50:
            raise ValueError("first_name must be at most 50 characters.")

        # Validation: last_name
        if not isinstance(last_name, str):
            raise TypeError("last_name must be a string.")
        last_name = last_name.strip()
        if not last_name:
            raise ValueError("last_name is required.")
        if len(last_name) > 50:
            raise ValueError("last_name must be at most 50 characters.")

        # Validation: email
        if not isinstance(email, str):
            raise TypeError("email must be a string.")
        email = email.strip()
        if not email:
            raise ValueError("email is required.")
        if len(email) > 254:
            raise ValueError("email is too long.")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("Invalid email format.")

        # Validation: is_admin 
        if not isinstance(is_admin, bool):
            raise TypeError("is_admin must be a boolean.")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email.lower()
        self.is_admin = is_admin

    def to_dict(self):
        """Return a dictionary representation of the user."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
