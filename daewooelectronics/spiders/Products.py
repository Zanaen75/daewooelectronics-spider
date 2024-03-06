import scrapy
import pdb
from urllib.parse import urlparse
from daewooelectronics.items import Manual, ManualLoader


class DaewooelectronicsSpider(scrapy.Spider):
    name = "Products"
    allowed_domains = ["daewooelectronics.es"]
    start_urls = [
        'https://daewooelectronics.es/shop/',
    ]
    product_urls = []

    def parse(self, response):
        # Extracting text of the second last pagination item
        last_pagination_item = response.css('nav.woocommerce-pagination ul.page-numbers li:nth-last-child(2) a::text').extract_first()

        # Converting last_pagination_item to integer
        last_pagination_item = int(last_pagination_item)

        # Generating pagination links
        pagination_links = [f"https://daewooelectronics.es/shop/page/{i}/" for i in range(1, last_pagination_item + 1)]

        # Yielding each pagination link
        for link in pagination_links:
            yield scrapy.Request(url=link, callback=self.parse_products)

    def parse_products(self, response):
        # Extracting product URLs from each product item on the page
        product_urls = response.css('ul.products li.product a::attr(href)').extract()

        # Update the class variable to store all product URLs
        self.product_urls.extend(product_urls)

        # Yielding each product URL
        for url in product_urls:
            # Check if the URL is valid
            if url.startswith('https://'):
                yield scrapy.Request(url=url, callback=self.parse_product_details)

    def parse_product_details(self, response):
        # Extracting text from the class "product_title entry-title"
        product_url = response.url.split('.')
        if len(product_url) >= 2:
            top_level_domain = '.'.join(product_url[-2:])
        product_title = response.css('.product_title.entry-title::text').get()
        product_model = response.css('h1.product_title::text').get().strip()
        ean_elements = response.css('div.pdetail-short-description ul li:contains("EAN")')
        ean_number = "None"  # Initialize eas_value outside the if-else block
        if ean_elements:
            for ean_element in ean_elements:
                eas_value = ean_element.get()
                ean_number = eas_value.split(' ')[1]
                print("EAN:", ean_number)
        else:
            print("Nono")
        product_brand = "Daewoo"
        product_lang = "es"
        product_manual_links = response.css('div.supportFilesZone div:nth-last-child(2) a::attr(href)').getall()
        product_thumb = response.css('figure.woocommerce-product-gallery__wrapper a::attr(href)').get()
        product_url = response.url
        parsed_url = urlparse(response.url)
        product_source = parsed_url.netloc
       


        print("ean_number", ean_number)
        # pdb.set_trace()       
        
        
        loader = ManualLoader(item=Manual(), response=response)
        loader.add_value('model', product_model)
        loader.add_value('model_2', " ")
        loader.add_value('brand', product_brand)
        loader.add_value('product', product_title)
        loader.add_value('product_parent', " ")
        loader.add_value('product_lang', product_lang)
        loader.add_value('file_urls', product_manual_links)
        loader.add_value('eans', ean_number)
        loader.add_value('files', product_manual_links)
        loader.add_value('type', "Manuales de usuario")
        loader.add_value('url', product_url)
        loader.add_value('thumbs', product_thumb)
        loader.add_value('source', product_source)

        yield loader.load_item()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DaewooelectronicsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        # Show the combined length of all product URLs
        print("Combined length of product URLs:", len(self.product_urls))