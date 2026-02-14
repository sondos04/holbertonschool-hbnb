#!/usr/bin/env python3
import os
from app import create_app
from config import DevelopmentConfig
from app.extensions import db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from werkzeug.security import generate_password_hash

app = create_app(DevelopmentConfig)

with app.app_context():
    print("🗑️  Dropping ALL tables...")
    db.drop_all()
    
    print("📦 Creating fresh tables...")
    db.create_all()
    
    print("\n👤 Creating users...")
    
    # Admin
    admin = User(
        email='admin@hbnb.com',
        password=generate_password_hash('admin123'),
        first_name='Admin',
        last_name='User',
        is_admin=True
    )
    db.session.add(admin)
    
    # Sara
    sara = User(
        email='sara@hbnb.com',
        password=generate_password_hash('sara123'),
        first_name='Sara',
        last_name='Ahmed',
        is_admin=False
    )
    db.session.add(sara)
    
    db.session.commit()
    print("✅ Users created")
    
    print("\n🏷️  Creating amenities...")
    wifi = Amenity(name='WiFi')
    pool = Amenity(name='Pool')
    parking = Amenity(name='Parking')
    
    db.session.add_all([wifi, pool, parking])
    db.session.commit()
    print("✅ Amenities created")
    
    print("\n🏠 Creating places...")
    
    place1 = Place(
        title='Luxury Resort',
        description='Beautiful resort',
        price_per_night=1200,
        latitude=24.7136,
        longitude=46.6753,
        owner_id=admin.id
    )
    place1.amenities.extend([wifi, pool, parking])
    
    place2 = Place(
        title='City Hotel',
        description='Modern hotel',
        price_per_night=900,
        latitude=24.7242,
        longitude=46.6385,
        owner_id=admin.id
    )
    place2.amenities.extend([wifi, parking])
    
    db.session.add_all([place1, place2])
    db.session.commit()
    print("✅ Places created")
    
    print("\n⭐ Creating reviews...")
    review1 = Review(
        place_id=place1.id,
        user_id=sara.id,
        rating=5,
        text='مكان رائع جداً!'
    )
    db.session.add(review1)
    db.session.commit()
    print("✅ Reviews created")
    
    print("\n" + "="*50)
    print("✅ DONE!")
    print("="*50)
    print("\n📧 Accounts:")
    print("   admin@hbnb.com / admin123")
    print("   sara@hbnb.com  / sara123")
    print("\n✅ Database is ready!")
