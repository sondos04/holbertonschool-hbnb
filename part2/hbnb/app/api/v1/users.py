from flask_restx import Resource, Namespace, fields
from app.services.facade import facade  # ✅ استيراد الـ facade المشترك

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name')
})

@api.route('/')
class Users(Resource):
    @api.expect(user_model)
    def post(self):
        """Create a new user"""
        try:
            user = facade.create_user(api.payload)
            return user.to_dict(), 201
        except ValueError as e:
            api.abort(400, str(e))
    
    def get(self):
        """Get all users"""
        users = facade.get_all_users()
        return [user.to_dict() for user in users]
