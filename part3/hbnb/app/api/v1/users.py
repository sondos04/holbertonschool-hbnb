# app/api/v1/users.py

from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.facade import facade
from app.extensions import db

api = Namespace("users", description="User operations")

user_model = api.model("User", {
    "email": fields.String(required=True),
    "password": fields.String(required=True),
    "first_name": fields.String,
    "last_name": fields.String,
})

update_user_model = api.model("UpdateUser", {
    "email": fields.String,
    "password": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
})

user_response_model = api.model("UserResponse", {
    "id": fields.String,
    "email": fields.String,
    "first_name": fields.String,
    "last_name": fields.String,
    "is_admin": fields.Boolean,
})


def require_admin():
    claims = get_jwt()
    if not claims.get("is_admin", False):
        api.abort(403, "Admin privileges required")



@api.route("/signup")
class Signup(Resource):
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    def post(self):
        """تسجيل مستخدم جديد - بدون الحاجة لـ token"""
        data = api.payload or {}
        try:
            user = facade.create_user(
                email=data["email"],
                password=data["password"],
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
            )
            db.session.commit()   
            print(f"DEBUG: Created user: {user.id}")  
            return user, 201
        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, f"Error: {str(e)}")


@api.route("/")
class Users(Resource):
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    @jwt_required()
    def post(self):
        require_admin()
        data = api.payload or {}
        try:
            user = facade.create_user(
                email=data["email"],
                password=data["password"],
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
            )
            return user, 201
        except ValueError as e:
            api.abort(400, str(e))

    @api.marshal_list_with(user_response_model)
    @jwt_required()
    def get(self):
        require_admin()
        return facade.user_repo.get_all(), 200


@api.route("/<string:user_id>")
class User(Resource):
    @api.marshal_with(user_response_model)
    def get(self, user_id):
        user = facade.user_repo.get_by_id(user_id)
        if not user:
            api.abort(404, "User not found")
        return user, 200

    @api.expect(update_user_model, validate=True)
    @api.marshal_with(user_response_model)
    @jwt_required()
    def put(self, user_id):
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)
        current_user_id = get_jwt_identity()

        if not is_admin and current_user_id != user_id:
            api.abort(403, "Unauthorized action")

        user = facade.user_repo.get_by_id(user_id)
        if not user:
            api.abort(404, "User not found")

        data = api.payload or {}

        if not is_admin and (("email" in data and data["email"]) or ("password" in data and data["password"])):
            api.abort(400, "You cannot modify email or password")

        if "first_name" in data and data["first_name"] is not None:
            user.first_name = data["first_name"]
        if "last_name" in data and data["last_name"] is not None:
            user.last_name = data["last_name"]

        if is_admin:
            if "email" in data and data["email"]:
                existing = facade.user_repo.get_by_email(data["email"])
                if existing and existing.id != user.id:
                    api.abort(400, "Email already exists")
                user.email = data["email"]

            if "password" in data and data["password"]:
                user.set_password(data["password"])

        facade.user_repo.update()
        return user, 200
