import scrapy
from selenium import webdriver
# Changed from ChromeService to FirefoxService
from selenium.webdriver.firefox.service import Service as FirefoxService
# Changed from ChromeOptions to FirefoxOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from scrapy.selector import Selector
from ..items import ArticleItem

class ProTVSpider(scrapy.Spider):
    name = 'protv'
    start_urls = ['https://stirileprotv.ro/stiri/'] # Example starting URL

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0', # Updated User-Agent for Firefox
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
        firefox_options.add_argument("--headless")


        
        gecko_driver_path = 'C:\practica 2025\News-Scrapping-\NewsScraper\geckodriver-v0.36.0-win-aarch64/geckodriver.exe' # Example path for GeckoDriver

        service = FirefoxService(gecko_driver_path)
        self.driver = webdriver.Firefox(service=service, options=firefox_options)


    def parse(self, response):
        self.driver.get(response.url)
    
        body = self.driver.page_source
        selector = Selector(text=body)

        
        for article_link in selector.css('a.article-link::attr(href)').getall(): 
            yield response.follow(article_link, self.parse_article)

        
        next_page = selector.css('a.next-page::attr(href)').get() 
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
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