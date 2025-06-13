from bs4 import BeautifulSoup as soup
import requests
import random


class OneFive:
    def __init__(self, url=None):
        self.url = url
        self.sess = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; moto g(9) power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/253.2.513328941 Mobile/20A362 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Mozilla/5.0 (iPhone 13, CPU iPhone OS 16_3.1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, Gecko) CriOS/91.0.4472.80 Mobile/15E148 Safari/604.1'
        ]
        self.headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.product_list = []

    def getRandomAliveProxy(self):
        '''Get a random alive proxy from ProxyScrape'''

        proxy_list = requests.get(
            'https://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&protocol=http&proxy_format=ipport&format=json').json()

        rand = random.choice(range(0, proxy_list['total_records']))
        if proxy_list['proxies'][rand]['alive']:
            return proxy_list['proxies'][rand]['proxy']

    def get_products(self):
        response = self.sess.get(f'{self.url}', headers=self.headers, proxies={
            'http': self.getRandomAliveProxy()})

        if response.status_code == 200:
            s = soup(response.text, 'html.parser')
            products = s.find(
                'ul', id='product-grid').findChildren('li', class_='grid__item')

            product_array = []

            base_url = self.url.split('.com.co')[0] + '.com.co'

            print("Fetching...")

            for product in products:
                name_tag = product.find('h3', class_='card__heading')
                name = name_tag.get_text(strip=True) if name_tag else 'No name'

                a_tag = product.find('h3', class_='card__heading').find(
                    'a') if product.find('h3', class_='card__heading') else None
                product_link = base_url + \
                    a_tag['href'][3:] if a_tag else 'No link'

                product_array.append({
                    'name': name,
                    'product_link': product_link
                })

            product_list = self.get_details_from_products(
                product_array) if product_array else 'No products found'

            return {
                'status': 'success',
                'data': product_list
            }

        else:
            return {
                'status': 'error',
                'message': 'Failed to get products',
                'status_code': response.status_code,
            }

    def get_details_from_products(self, product_list):
        for product in product_list:
            response = self.sess.get(product['product_link'], headers=self.headers, proxies={
                'http': self.getRandomAliveProxy()})

            if response.status_code == 200:
                s = soup(response.text, 'html.parser')
                colors = []
                img_urls = []
                sizes = []

                data = s.find(
                    'variant-selects', id='variant-selects-template--23910007308597__main')

                if data:
                    fieldsets = data.find_all('fieldset')

                    for fs in fieldsets:
                        legend = fs.find('legend').get_text(strip=True).lower()

                        color_inputs = s.find_all("input", attrs={"name": lambda v: v and v.lower().startswith("color")})
                        colors = []

                        for inp in color_inputs:
                            if inp.has_attr("value"):
                                val = inp["value"].strip()
                                if val:
                                    colors.append(val)

   
                        if 'talla' in legend:
                            size_inputs = fs.find_all(
                                'input', attrs={'name': lambda v: v and v.startswith('Talla')})
                            sizes = [tag['value'].strip()
                                     for tag in size_inputs if tag.get('value')]

                description_div = s.find(
                    'div', class_='product__description rte quick-add-hidden')
                
                price_tag = s.find('span', class_='money')
                price = price_tag.get_text(
                    strip=True) if price_tag else 'No price'

                if description_div:
                    description_text = description_div.get_text(
                        separator=' ', strip=True)
                else:
                    description_text = 'No description'

                carousel_ul = s.find("ul", id=lambda x: x and x.startswith("Slider-Thumbnails"))

                if carousel_ul:  
                    for li in carousel_ul.find_all("li"):
                        img = li.find("img")
                        if img and img.get("src"):
                            img_urls.append(f"https://{img['src'][2:]}")

 
                product['price'] = price 
                product['colors'] = colors if colors else 'No colors available'
                product['sizes'] = sizes if sizes else 'No sizes available'
                product['img_url'] = img_urls
                product['description'] = description_text

            else:
                product['description'] = 'Failed to fetch details'

        return product_list


# s = OneFive("https://www.onefive.com.co/collections/avada-best-sellers")
# print(s.get_products())
