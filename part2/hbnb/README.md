# HBnB Project

## Project Structure

### Directory Overview
- **app/**: Contains the main application logic.
- **api/**: Handles API endpoints and request/response logic.
- **models/**: Defines the core data models.
- **services/**: Implements the Facade pattern to coordinate business logic.
- **persistence/**: Provides an in-memory repository for data storage.
- **run.py**: Used to start the application.
- **config.py**: Stores configuration settings.
- **requirements.txt**: Lists required Python packages.

---

## Running the Project

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Run the Application
```bash
python run.py
```

---

## Business Logic Layer

This layer implements the core entities of the HBnB system and defines how they interact.

Implemented Classes

### User

- Represents an application user.
- Attributes include name, email, and admin privileges.

### Place

- Represents a property listing owned by a user.
- Includes location, price, and available amenities.

### Review

- Represents a user’s review of a place.
- Contains review text and a rating from 1 to 5.

### Amenity

- Represents additional features available in a place (e.g., Wi-Fi, Parking).

---

## Common Features

- All entities inherit from BaseModel, which provides:
- Unique UUID generation (id)
- Timestamp management (created_at, updated_at)
- save() method to track updates

---

## Relationships

- A User can own multiple Places.
- A Place can have multiple Reviews and multiple Amenities.
- A Review is associated with both a User and a Place.
- Each class includes attribute validation to ensure data integrity.
