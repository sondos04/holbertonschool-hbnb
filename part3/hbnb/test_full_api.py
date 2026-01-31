import json
import unittest

from app import create_app
from config import DevelopmentConfig
from app.extensions import db

from app.models.user import User
from app.models.place import Place, place_amenity
from app.models.review import Review
from app.models.amenity import Amenity


def _headers(token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


class HBnBAllCasesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        
        class TestConfig(DevelopmentConfig):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            JWT_SECRET_KEY = getattr(DevelopmentConfig, "JWT_SECRET_KEY", "jwt-super-secret-key")
            SECRET_KEY = getattr(DevelopmentConfig, "SECRET_KEY", "super-secret-key")

        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        
        with self.app.app_context():
            
            db.session.execute(place_amenity.delete())
            
            db.session.query(Review).delete()
            db.session.query(Place).delete()
            db.session.query(Amenity).delete()
            db.session.query(User).delete()
            db.session.commit()

            
            admin = User(email="admin@example.com", first_name="Admin", last_name="User", is_admin=True)
            admin.set_password("adminpass")
            db.session.add(admin)

            user = User(email="user@example.com", first_name="Regular", last_name="User", is_admin=False)
            user.set_password("userpass")
            db.session.add(user)

            db.session.commit()

            self.admin_id = admin.id
            self.user_id = user.id

        
        self.admin_token = self._login("admin@example.com", "adminpass")
        self.user_token = self._login("user@example.com", "userpass")

    
    
    
    def _login(self, email, password):
        r = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"email": email, "password": password}),
            headers=_headers(),
        )
        self.assertEqual(r.status_code, 200, msg=r.get_data(as_text=True))
        data = r.get_json() or {}
        self.assertIn("access_token", data)
        return data["access_token"]

    def _create_place_as_user(self, token, title="Test Place", description="Nice", price=100.0):
        r = self.client.post(
            "/api/v1/places/",
            data=json.dumps({"title": title, "description": description, "price_per_night": price}),
            headers=_headers(token),
        )
        self.assertEqual(r.status_code, 201, msg=r.get_data(as_text=True))
        return r.get_json()

    def _create_review_as_user(self, token, place_id, text="Great", rating=5):
        r = self.client.post(
            "/api/v1/reviews/",
            data=json.dumps({"text": text, "place_id": place_id, "rating": rating}),
            headers=_headers(token),
        )
        return r

    def _create_amenity_as_admin(self, name="Wifi"):
        r = self.client.post(
            "/api/v1/amenities/",
            data=json.dumps({"name": name}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r.status_code, 201, msg=r.get_data(as_text=True))
        return r.get_json()

    def _assert_unauthorized_token(self, r):
        
        self.assertIn(r.status_code, (401, 422), msg=r.get_data(as_text=True))

    
    def test_auth_invalid_credentials(self):
        r = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"email": "admin@example.com", "password": "wrong"}),
            headers=_headers(),
        )
        self.assertEqual(r.status_code, 401)

    def test_auth_missing_fields_returns_4xx(self):
        
        r1 = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"email": "admin@example.com"}),
            headers=_headers(),
        )
        self.assertIn(r1.status_code, (400, 422), msg=r1.get_data(as_text=True))

        
        r2 = self.client.post("/api/v1/auth/login", data=json.dumps({}), headers=_headers())
        self.assertIn(r2.status_code, (400, 422), msg=r2.get_data(as_text=True))

    def test_protected_endpoints_invalid_token(self):
        bad = "Bearer not-a-real-jwt"
        r1 = self.client.get("/api/v1/users/", headers={"Authorization": bad})
        self._assert_unauthorized_token(r1)

        r2 = self.client.post(
            "/api/v1/places/",
            data=json.dumps({"title": "X", "description": "Y", "price_per_night": 10}),
            headers={"Content-Type": "application/json", "Authorization": bad},
        )
        self._assert_unauthorized_token(r2)

   
    def test_users_create_requires_auth(self):
        r = self.client.post(
            "/api/v1/users/",
            data=json.dumps({"email": "x@x.com", "password": "1234", "first_name": "X", "last_name": "Y"}),
            headers=_headers(),
        )
        self.assertEqual(r.status_code, 401)

    def test_users_regular_cannot_list(self):
        r = self.client.get("/api/v1/users/", headers=_headers(self.user_token))
        self.assertEqual(r.status_code, 403)

    def test_users_admin_can_list(self):
        r = self.client.get("/api/v1/users/", headers=_headers(self.admin_token))
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

    def test_users_admin_create_duplicate_email(self):
        
        r1 = self.client.post(
            "/api/v1/users/",
            data=json.dumps({"email": "dup@example.com", "password": "1111", "first_name": "A", "last_name": "B"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r1.status_code, 201, msg=r1.get_data(as_text=True))

        
        r2 = self.client.post(
            "/api/v1/users/",
            data=json.dumps({"email": "dup@example.com", "password": "2222"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r2.status_code, 400)

    def test_users_get_nonexistent_404(self):
        r = self.client.get("/api/v1/users/does-not-exist", headers=_headers())
        self.assertEqual(r.status_code, 404)

    def test_users_get_existing_200(self):
        r = self.client.get(f"/api/v1/users/{self.user_id}", headers=_headers())
        self.assertEqual(r.status_code, 200, msg=r.get_data(as_text=True))
        body = r.get_json() or {}
        self.assertEqual(body.get("id"), self.user_id)
        self.assertEqual(body.get("email"), "user@example.com")

    def test_users_put_regular_cannot_edit_other_user(self):
        r = self.client.put(
            f"/api/v1/users/{self.admin_id}",
            data=json.dumps({"first_name": "Hacked"}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r.status_code, 403)

    def test_users_put_regular_can_only_edit_self_names(self):
        
        r1 = self.client.put(
            f"/api/v1/users/{self.user_id}",
            data=json.dumps({"first_name": "New", "last_name": "Name"}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r1.status_code, 200, msg=r1.get_data(as_text=True))
        body = r1.get_json() or {}
        self.assertEqual(body.get("first_name"), "New")
        self.assertEqual(body.get("last_name"), "Name")

        
        r2 = self.client.put(
            f"/api/v1/users/{self.user_id}",
            data=json.dumps({"email": "changed@example.com", "password": "newpass"}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r2.status_code, 400, msg=r2.get_data(as_text=True))

    def test_users_admin_put_duplicate_email_400(self):
        
        r1 = self.client.post(
            "/api/v1/users/",
            data=json.dumps({"email": "u2@example.com", "password": "p2", "first_name": "U2", "last_name": "U2"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r1.status_code, 201, msg=r1.get_data(as_text=True))
        u2_id = (r1.get_json() or {}).get("id")
        self.assertTrue(u2_id)

        
        r2 = self.client.put(
            f"/api/v1/users/{u2_id}",
            data=json.dumps({"email": "user@example.com"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r2.status_code, 400, msg=r2.get_data(as_text=True))

    
    def test_places_public_list_ok(self):
        r = self.client.get("/api/v1/places/", headers=_headers())
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIsInstance(data, list)

    def test_places_create_requires_auth(self):
        r = self.client.post(
            "/api/v1/places/",
            data=json.dumps({"title": "NoAuth", "description": "x", "price_per_night": 10}),
            headers=_headers(),
        )
        self.assertEqual(r.status_code, 401)

    def test_places_create_missing_title_4xx(self):
        r1 = self.client.post(
            "/api/v1/places/",
            data=json.dumps({"description": "x", "price_per_night": 10}),
            headers=_headers(self.user_token),
        )
        self.assertIn(r1.status_code, (400, 422), msg=r1.get_data(as_text=True))

        r2 = self.client.post(
            "/api/v1/places/",
            data=json.dumps({"title": "   ", "description": "x", "price_per_night": 10}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r2.status_code, 400, msg=r2.get_data(as_text=True))

    def test_places_create_owner_forced_from_token(self):
        created = self._create_place_as_user(self.user_token, title="OwnerForced", price=55)
        self.assertEqual(created.get("title"), "OwnerForced")
        self.assertEqual(created.get("owner_id"), self.user_id)

    def test_places_get_nonexistent_404(self):
        r = self.client.get("/api/v1/places/nope", headers=_headers())
        self.assertEqual(r.status_code, 404)

    def test_places_update_owner_only(self):
        created = self._create_place_as_user(self.user_token, title="Editable", price=10)
        place_id = created["id"]

        
        r_admin = self.client.put(
            f"/api/v1/places/{place_id}",
            data=json.dumps({"title": "AdminEdit"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r_admin.status_code, 200, msg=r_admin.get_data(as_text=True))

        created2 = self._create_place_as_user(self.user_token, title="OwnerOnly", price=20)
        place2_id = created2["id"]

        with self.app.app_context():
            u2 = User(email="user2@example.com", first_name="U2", last_name="U2", is_admin=False)
            u2.set_password("user2pass")
            db.session.add(u2)
            db.session.commit()

        u2_token = self._login("user2@example.com", "user2pass")

        r_forbidden = self.client.put(
            f"/api/v1/places/{place2_id}",
            data=json.dumps({"title": "Nope"}),
            headers=_headers(u2_token),
        )
        self.assertEqual(r_forbidden.status_code, 403)

        
        r_owner = self.client.put(
            f"/api/v1/places/{place2_id}",
            data=json.dumps({"title": "OwnerEdited"}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r_owner.status_code, 200, msg=r_owner.get_data(as_text=True))
        self.assertEqual((r_owner.get_json() or {}).get("title"), "OwnerEdited")

    def test_places_delete_owner_or_admin_and_then_404(self):
        created = self._create_place_as_user(self.user_token, title="ToDelete", price=33)
        place_id = created["id"]

        
        with self.app.app_context():
            u3 = User(email="user3@example.com", first_name="U3", last_name="U3", is_admin=False)
            u3.set_password("user3pass")
            db.session.add(u3)
            db.session.commit()
        u3_token = self._login("user3@example.com", "user3pass")

        r_forbidden = self.client.delete(f"/api/v1/places/{place_id}", headers=_headers(u3_token))
        self.assertEqual(r_forbidden.status_code, 403)

        
        r_admin = self.client.delete(f"/api/v1/places/{place_id}", headers=_headers(self.admin_token))
        self.assertEqual(r_admin.status_code, 200, msg=r_admin.get_data(as_text=True))

        
        r_get = self.client.get(f"/api/v1/places/{place_id}", headers=_headers())
        self.assertEqual(r_get.status_code, 404)

    
    def test_reviews_create_requires_auth(self):
        r = self.client.post(
            "/api/v1/reviews/",
            data=json.dumps({"text": "x", "place_id": "y", "rating": 5}),
            headers=_headers(),
        )
        self.assertEqual(r.status_code, 401)

    def test_reviews_place_not_found_404(self):
        
        r = self.client.post(
            "/api/v1/reviews/",
            data=json.dumps({"text": "X", "place_id": "no-such-place", "rating": 5}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r.status_code, 404, msg=r.get_data(as_text=True))

    def test_reviews_missing_text_4xx(self):
        place = self._create_place_as_user(self.user_token, title="T1", price=10)
        
        with self.app.app_context():
            u2 = User(email="rev1@example.com", first_name="R", last_name="R", is_admin=False)
            u2.set_password("revpass")
            db.session.add(u2)
            db.session.commit()
        rev_token = self._login("rev1@example.com", "revpass")

        r = self.client.post(
            "/api/v1/reviews/",
            data=json.dumps({"place_id": place["id"], "rating": 5}),
            headers=_headers(rev_token),
        )
        self.assertIn(r.status_code, (400, 422), msg=r.get_data(as_text=True))

    def test_reviews_invalid_rating_400(self):
        place = self._create_place_as_user(self.user_token, title="Rated", price=10)
        
        with self.app.app_context():
            u2 = User(email="rev@example.com", first_name="R", last_name="R", is_admin=False)
            u2.set_password("revpass")
            db.session.add(u2)
            db.session.commit()
        rev_token = self._login("rev@example.com", "revpass")

        r = self._create_review_as_user(rev_token, place["id"], text="BadRating", rating=999)
        self.assertEqual(r.status_code, 400)

    def test_reviews_cannot_review_own_place_and_cannot_duplicate(self):
        place = self._create_place_as_user(self.user_token, title="MyPlace", price=10)

        r1 = self._create_review_as_user(self.user_token, place["id"], text="Self", rating=5)
        self.assertEqual(r1.status_code, 400)

        
        with self.app.app_context():
            u2 = User(email="reviewer@example.com", first_name="Rev", last_name="One", is_admin=False)
            u2.set_password("reviewerpass")
            db.session.add(u2)
            db.session.commit()
        reviewer_token = self._login("reviewer@example.com", "reviewerpass")

        
        r2 = self._create_review_as_user(reviewer_token, place["id"], text="Nice", rating=5)
        self.assertEqual(r2.status_code, 201, msg=r2.get_data(as_text=True))
        review_id = (r2.get_json() or {}).get("id")
        self.assertTrue(review_id)

        
        r3 = self._create_review_as_user(reviewer_token, place["id"], text="Again", rating=4)
        self.assertEqual(r3.status_code, 400)

    def test_reviews_update_invalid_rating_400(self):
        place = self._create_place_as_user(self.user_token, title="PlaceForReview", price=10)

        
        with self.app.app_context():
            u2 = User(email="updrev2@example.com", first_name="Up", last_name="Rev", is_admin=False)
            u2.set_password("updrevpass")
            db.session.add(u2)
            db.session.commit()
        reviewer_token = self._login("updrev2@example.com", "updrevpass")

        
        r_create = self._create_review_as_user(reviewer_token, place["id"], text="Initial", rating=4)
        self.assertEqual(r_create.status_code, 201, msg=r_create.get_data(as_text=True))
        review_id = (r_create.get_json() or {}).get("id")

        
        r_bad = self.client.put(
            f"/api/v1/reviews/{review_id}",
            data=json.dumps({"rating": 0}),
            headers=_headers(reviewer_token),
        )
        self.assertIn(r_bad.status_code, (400, 422), msg=r_bad.get_data(as_text=True))

    def test_reviews_update_delete_owner_only_or_admin_and_then_404(self):
        place = self._create_place_as_user(self.user_token, title="PlaceForReview", price=10)

        
        with self.app.app_context():
            u2 = User(email="updrev@example.com", first_name="Up", last_name="Rev", is_admin=False)
            u2.set_password("updrevpass")
            db.session.add(u2)
            db.session.commit()
        reviewer_token = self._login("updrev@example.com", "updrevpass")

        
        r_create = self._create_review_as_user(reviewer_token, place["id"], text="Initial", rating=4)
        self.assertEqual(r_create.status_code, 201, msg=r_create.get_data(as_text=True))
        review_id = (r_create.get_json() or {}).get("id")

        
        r_forbidden = self.client.put(
            f"/api/v1/reviews/{review_id}",
            data=json.dumps({"text": "Hack"}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r_forbidden.status_code, 403)

        
        r_ok = self.client.put(
            f"/api/v1/reviews/{review_id}",
            data=json.dumps({"text": "Updated", "rating": 5}),
            headers=_headers(reviewer_token),
        )
        self.assertEqual(r_ok.status_code, 200, msg=r_ok.get_data(as_text=True))

        r_del = self.client.delete(f"/api/v1/reviews/{review_id}", headers=_headers(self.admin_token))
        self.assertEqual(r_del.status_code, 200, msg=r_del.get_data(as_text=True))

        r_get = self.client.get(f"/api/v1/reviews/{review_id}", headers=_headers())
        self.assertEqual(r_get.status_code, 404)

    
    def test_amenities_public_get_ok(self):
        r = self.client.get("/api/v1/amenities/", headers=_headers())
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.get_json(), list)

    def test_amenities_get_nonexistent_404(self):
        r = self.client.get("/api/v1/amenities/nope", headers=_headers())
        self.assertEqual(r.status_code, 404)

    def test_amenities_admin_only_create_update(self):
        
        r_forbidden = self.client.post(
            "/api/v1/amenities/",
            data=json.dumps({"name": "Pool"}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r_forbidden.status_code, 403)

        amenity = self._create_amenity_as_admin("Pool")
        amenity_id = amenity["id"]

        r_forbidden2 = self.client.put(
            f"/api/v1/amenities/{amenity_id}",
            data=json.dumps({"name": "Pool2"}),
            headers=_headers(self.user_token),
        )
        self.assertEqual(r_forbidden2.status_code, 403)

        r_ok = self.client.put(
            f"/api/v1/amenities/{amenity_id}",
            data=json.dumps({"name": "Pool2"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r_ok.status_code, 200, msg=r_ok.get_data(as_text=True))
        self.assertEqual((r_ok.get_json() or {}).get("name"), "Pool2")

    def test_amenities_duplicate_name_400(self):
        a1 = self._create_amenity_as_admin("Wifi")
        self.assertTrue(a1.get("id"))

        r = self.client.post(
            "/api/v1/amenities/",
            data=json.dumps({"name": "Wifi"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r.status_code, 400, msg=r.get_data(as_text=True))

    def test_amenities_update_to_existing_name_400(self):
        a1 = self._create_amenity_as_admin("Wifi")
        a2 = self._create_amenity_as_admin("Parking")

        r = self.client.put(
            f"/api/v1/amenities/{a2['id']}",
            data=json.dumps({"name": "Wifi"}),
            headers=_headers(self.admin_token),
        )
        self.assertEqual(r.status_code, 400, msg=r.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
