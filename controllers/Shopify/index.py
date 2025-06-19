from flask_restful import Resource, request
from resources.Shopify.index import ShopifyProducts

class Shopify(Resource):

    def post(self): 
        data = request.get_json()
        shop_name = data["SHOP_NAME"]
        api_key = data["API_KEY"]

        wcsport = ShopifyProducts(shop_name, api_key)

        if shop_name and api_key:            
            result = wcsport.get_products()
            return {
                'result': result
            }

        else:
            return {
                'status': False,
                'message': 'You must provide all arguments'
            }