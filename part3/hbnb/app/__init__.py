from flask import Flask
from flask_restx import Api
from flask_cors import CORS

from app.extensions import db, bcrypt, jwt

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # CORS Configuration - السماح لكل الأصول
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Create API
    api = Api(
        app,
        version="1.0",
        title="HBnB API",
        description="HBnB Application API",
        doc="/api/v1/"
    )
    
    # Import and register namespaces
    from app.api.v1.users import api as users_ns
    from app.api.v1.auth import api as auth_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    
    api.add_namespace(users_ns, path="/api/v1/users")
    api.add_namespace(auth_ns, path="/api/v1/auth")
    api.add_namespace(amenities_ns, path="/api/v1/amenities")
    api.add_namespace(places_ns, path="/api/v1/places")
    api.add_namespace(reviews_ns, path="/api/v1/reviews")
    
    return app
