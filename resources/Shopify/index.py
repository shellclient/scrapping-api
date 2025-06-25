import requests
from bs4 import BeautifulSoup as soup


class ShopifyProducts:
    def __init__(self, SHOP_NAME, API_KEY):
        self.SHOP_NAME = SHOP_NAME
        self.API_KEY = API_KEY
        self.API_VERSION = None


    def get_products(self) -> list:
        """
        Obtiene una lista de productos de Shopify.
        """
        API_VERSION = self.get_latest_version()

        url = f'https://{self.SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/products.json?limit=250'
        
        product_list = []
        
        response = requests.get(url, headers={
            "X-Shopify-Access-Token": f"{self.API_KEY}",
            "Content-Type": "application/json",
        })

        if response.status_code == 200:
            products = response.json().get('products', [])
            for product in products:
                if product['status'] == 'active':
                    product_list.append({
                        "id": product['id'],
                        "title": product['title'],
                        "description": soup(product['body_html'], "html.parser").get_text(strip=True),
                        "options": [
                            {
                                "name": option["name"],
                                "values": option["values"]
                            } for option in product.get('options', [])
                        ],

                        "variants": [
                            {
                                "id": variant['id'],
                                "title": variant['title'],
                                "price": variant['price'],
                                "inventory_quantity": variant['inventory_quantity']
                            } for variant in product.get('variants', [])
                        ],

                        "images": [
                            {
                                "src": image['src']
                            } for image in product.get('images', [])
                        ],

                        "image": f"{product['image']['src']}" if product.get('image') else None,
                    })

            return product_list

        else:
            return {
                "status": False,
                "message": f"{response.status_code} - {response.text}"
            }


    def _graphql_request(self, version: str, query: str, variables: dict = None) -> dict:
        """Hace una petición GraphQL al endpoint /graphql.json con la versión indicada."""
        
        url = f"https://{self.SHOP_NAME}.myshopify.com/admin/api/{version}/graphql.json"
        
        headers = {
            "X-Shopify-Access-Token": self.API_KEY,
            "Content-Type": "application/json"
        }
        payload = {"query": query}
        
        if variables is not None:
            payload["variables"] = variables
        
        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        return resp.json()


    def get_latest_version(self) -> str:
        """
        Consulta publicApiVersions y devuelve el handle de la última versión estable.
        """
    

        # Para invocar la consulta, podemos usar cualquier versión válida; usamos "2025-01" o la que tengas codificada si ya existe.
        # Sin embargo, si la tienda EOL alguna versión, conviene usar una que sepamos vigente.
        # Aquí asumimos que "2025-01" aún funciona; si no, podrías intentar con una versión anterior soportada.
        fallback_version = "2025-01"
        query = '''
        {
          publicApiVersions {
            handle
            supported
          }
        }
        '''
        
        data = self._graphql_request(fallback_version, query)
        versions = data.get("data", {}).get("publicApiVersions", [])
        
        # Filtrar solo soportadas y descartar "unstable"
        stable = [v["handle"] for v in versions if v.get(
            "supported") and v.get("handle") != "unstable"]
        
        if not stable:
            raise RuntimeError("No se encontraron versiones estables en publicApiVersions")
        
        # Orden lexicográfico funciona para "YYYY-MM"
        stable_sorted = sorted(stable)
        latest = stable_sorted[-1]
        self.api_version = latest
        
        return latest

