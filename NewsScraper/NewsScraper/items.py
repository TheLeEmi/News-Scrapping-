# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    author = scrapy.Field()
    link = scrapy.Field()
    keywords = scrapy.Field()
    short_description = scrapy.Field()