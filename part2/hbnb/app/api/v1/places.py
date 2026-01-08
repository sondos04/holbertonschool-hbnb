from flask_restx import Resource, Namespace, fields
from app.services.facade import facade  # ✅ نفس facade المشترك

api = Namespace('places', description='Place operations')

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Place title'),
    'owner_id': fields.String(required=True, description='Owner ID'),
    'description': fields.String(description='Place description'),
    'price_per_night': fields.Float(description='Price per night')
})

@api.route('/')
class Places(Resource):
    @api.expect(place_model)
    def post(self):
        """Create a new place"""
        try:
            place = facade.create_place(api.payload)
            return place.to_dict(), 201
        except ValueError as e:
            api.abort(400, str(e))
    
    def get(self):
        """Get all places"""
        places = facade.get_all_places()
        return [place.to_dict() for place in places]
