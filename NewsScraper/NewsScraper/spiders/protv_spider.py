import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from scrapy.selector import Selector
from ..items import ArticleItem

class ProTVSpider(scrapy.Spider):
    name = 'protv'
    start_urls = [r'https://stirileprotv.ro/stiri/international/trump-i-a-trimis-o-scrisoare-maiei-sandu-anuntand-un-tarif-vamal-de-25-pentru-produsele-din-r-moldova-reactia-chisinaului.html'] # Example starting URL

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'FEEDS': {
            'articles.json': {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            },
        },
        'ITEM_PIPELINES': {
            'NewsScraper.pipelines.MsSQLPipeline': 300,
        },
    }

    def __init__(self, *args, **kwargs):
        super(ProTVSpider, self).__init__(*args, **kwargs)

        firefox_options = FirefoxOptions()
        #firefox_options.add_argument("--headless")

        # <--- IMPORTANT: Add this line to specify Firefox browser binary location --->
        # Replace this with the actual path to your firefox.exe
        firefox_binary_path = 'C:/Program Files/Mozilla Firefox/firefox.exe' # Example path
        firefox_options.binary_location = firefox_binary_path


        # Ensure this path is accurate to where you extracted geckodriver.exe
        gecko_driver_path = 'C:/practica 2025/News-Scrapping-/NewsScraper/geckodriver-v0.36.0-win64/geckodriver.exe' # Example path

        service = FirefoxService(gecko_driver_path)
        self.driver = webdriver.Firefox(service=service, options=firefox_options)


    def parse(self, response):
        # ... (rest of your parse method) ...
        self.driver.get(response.url)
        body = self.driver.page_source
        selector = Selector(text=body)

        for article_link in selector.css('a.article-link::attr(href)').getall():
            yield response.follow(article_link, self.parse_article)

        next_page = selector.css('a.next-page::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        # ... (rest of your parse_article method) ...
        self.driver.get(response.url)
        body = self.driver.page_source
        selector = Selector(text=body)

        item = ArticleItem()
        item['title'] = selector.css('h1.article-title::text').get()
        item['source'] = 'Stirile ProTV'
        item['category'] = 'N/A'
        item['author'] = selector.css('.article-author::text').get()
        item['link'] = response.url
        item['keywords'] = selector.css('meta[name="keywords"]::attr(content)').get()
        item['short_description'] = selector.css('meta[name="description"]::attr(content)').get()

        yield item

    def closed(self, reason):
        self.driver.quit()