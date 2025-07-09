import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from ..items import ArticleItem

class ProTVSpider(scrapy.Spider):
    name = 'protv'
    start_urls = ['https://stirileprotv.ro/stiri/'] # Example starting URL

    custom_settings = {
        'ROBOTSTXT_OBEY': False, # Be careful with this, check robots.txt
        'DOWNLOAD_DELAY': 2, # Be polite, don't hammer the server
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
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
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # Ensure the path to your ChromeDriver is correct
        service = Service('/path/to/your/chromedriver') # <--- IMPORTANT: Update this path
        self.driver = webdriver.Chrome(service=service, options=chrome_options)


    def parse(self, response):
        self.driver.get(response.url)
        # Selenium can be used here to interact with the page,
        # e.g., click "Load More" buttons or wait for content to load
        # For example, let's wait for a specific element to be present
        # self.driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article.news-item')))

        # After any Selenium actions, get the page source and parse with Scrapy Selector
        body = self.driver.page_source
        selector = Selector(text=body)

        # Example: Find news article links (you'll need to inspect the actual website)
        for article_link in selector.css('a.article-link::attr(href)').getall(): # This CSS selector is hypothetical
            yield response.follow(article_link, self.parse_article)

        # Handle pagination if necessary
        next_page = selector.css('a.next-page::attr(href)').get() # Hypothetical next page selector
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        self.driver.get(response.url)
        body = self.driver.page_source
        selector = Selector(text=body)

        item = ArticleItem()
        item['title'] = selector.css('h1.article-title::text').get()
        item['source'] = 'Stirile ProTV'
        # You'll need logic to determine category based on URL or breadcrumbs
        item['category'] = 'N/A' # Placeholder
        item['author'] = selector.css('.article-author::text').get()
        item['link'] = response.url
        # Keywords might be in meta tags or a dedicated section
        item['keywords'] = selector.css('meta[name="keywords"]::attr(content)').get()
        item['short_description'] = selector.css('meta[name="description"]::attr(content)').get()

        yield item

    def closed(self, reason):
        self.driver.quit()