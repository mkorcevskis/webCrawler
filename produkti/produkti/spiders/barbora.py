import scrapy
import json
from scrapy.item import Item, Field


class Product(Item):
    name = Field()
    image = Field()
    price = Field()
    link = Field()


class BarboraSpider(scrapy.Spider):
    name = "barbora"
    allowed_domains = ["barbora.lv"]
    products = []
    MAX_PRODUCT_COUNT = 5

    def __init__(self, _product_name="", *args, **kwargs):
        super(BarboraSpider, self).__init__(*args, **kwargs)
        self.export_file_name = "export_{}_{}.txt".format(self.name, _product_name)
        self.product_to_find = _product_name
        if len(_product_name.split()) > 1:
            _product_name = _product_name.replace(" ", "%20")
        self.start_urls = ["https://barbora.lv/meklet?order=priceAsc&q={}".format(_product_name)]

# cd prodTest
# scrapy crawl barbora -a _product_name="<NAME>"

    def parse(self, response):
        with open(self.export_file_name, "w") as f:
            for i, iter_product in enumerate(response.css('div.b-product-wrap-img')):
                i = i + 1
                product = Product()
                product['name'] = iter_product.css('span[itemprop="name"]::text').get()
                product['image'] = iter_product.css('img[itemprop="image"]::attr(src)').get()
                euros = iter_product.css('span.b-product-price-current-number::attr(content)').get()
                product_price = euros if euros else "NaN"
                product['price'] = product_price
                product['link'] = "https://" + self.allowed_domains[0] + iter_product.css('a.b-product-title::attr(href)').get()
                self.products.append(product)
                #
                json.dump({
                    'num': i,
                    'name': iter_product.css('span[itemprop="name"]::text').get(),
                    'image': iter_product.css('img[itemprop="image"]::attr(src)').get(),
                    'price': product_price,
                    'link': "https://" + self.allowed_domains[0] + iter_product.css('a.b-product-title::attr(href)').get()
                }, f, indent=4)
                f.write("\n")
                #
                # if i == self.MAX_PRODUCT_COUNT:
                #     break
        # file has been closed
        print("-------------------------")
        print("BEFORE FILTERING = " + str(len(self.products)))
        self.products = [i for i in self.products if any(item in [j.upper() for j in self.product_to_find.split()] for item in [k.upper() for k in i['name'].split()]) and not i['price'].isalpha()]
        if len(self.products) > 0:
            print("AFTER FILTERING = " + str(len(self.products)))
            _summa = 0
            for i in self.products:
                _summa += float(i['price'])
                print(i)
            _average = _summa / len(self.products)
            print("AVERAGE OF {} = {:.2f} EUR".format(self.product_to_find, _average))
            print("MEDIAN OF {} = {} EUR".format(self.product_to_find, self.products[round(len(self.products) / 2)]['price']))
            # print(self.products[round(len(self.products) / 2)])
        else:
            print(self.products)
            print("No such product found!")
        print("-------------------------")
