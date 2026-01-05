from app.models.review import Review
from app.models.place import Place
from app.models.user import User

def test_review():
    user = User("sondos", "alrubaish", "sondos@example.com")
    place = Place("apartment", "Small and cozy", 230, 24.5, 46.6, user)

    review = Review("Amazing experience!", 5, place, user)

    assert review.text == "Amazing experience!"
    assert review.rating == 5
    assert review.place == place
    assert review.user == user

    print(" Review test passed!")

if __name__ == "__main__":
    test_review()
