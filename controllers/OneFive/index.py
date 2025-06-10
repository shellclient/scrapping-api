from flask_restful import Resource, request
from resources.OneFive.index import OneFive

class OneFiveScrapper(Resource):

    def post(self): 
        data = request.get_json()
        url = data["url"]

        onefive = OneFive(url)

        if url:            
            result = onefive.get_products()
            return {
                'result': result
            }

        else:
            return {
                'status': False,
                'message': 'You must provide all arguments'
            }