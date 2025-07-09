# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymssql
from itemadapter import ItemAdapter

class MsSQLPipeline:
    def __init__(self, db_settings):
        self.db_settings = db_settings
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict('MSSQL_SETTINGS')
        return cls(db_settings)

    def open_spider(self, spider):
        try:
            self.conn = pymssql.connect(
                server=self.db_settings['SERVER'],
                user=self.db_settings['USER'],
                password=self.db_settings['PASSWORD'],
                database=self.db_settings['DATABASE']
            )
            self.cursor = self.conn.cursor()
            spider.logger.info("Connected to SQL Server database.")
        except Exception as e:
            spider.logger.error(f"Error connecting to SQL Server: {e}")
            self.conn = None

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        spider.logger.info("Disconnected from SQL Server database.")

    def process_item(self, item, spider):
        if not self.conn:
            spider.logger.warning("No database connection, skipping item.")
            return item

        adapter = ItemAdapter(item)
        try:
            self.cursor.execute(
                """
                INSERT INTO Articles (Title, Source, Category, Author, Link, Keywords, ShortDescription)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    adapter.get('title'),
                    adapter.get('source'),
                    adapter.get('category'),
                    adapter.get('author'),
                    adapter.get('link'),
                    adapter.get('keywords'),
                    adapter.get('short_description')
                )
            )
            self.conn.commit()
            spider.logger.info(f"Article '{adapter.get('title')}' saved to DB.")
        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"Failed to save item to DB: {adapter.get('title')} - {e}")
        return item