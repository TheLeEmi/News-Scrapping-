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
        spider.logger.info("MsSQLPipeline: Attempting to connect to SQL Server...")
        try:
            self.conn = pymssql.connect(
                server=self.db_settings['SERVER'],
                user=self.db_settings['USER'],
                password=self.db_settings['PASSWORD'],
                database=self.db_settings['DATABASE']
            )
            self.cursor = self.conn.cursor()
            spider.logger.info("MsSQLPipeline: Connected to SQL Server database.")
        except Exception as e:
            spider.logger.error(f"MsSQLPipeline: Error connecting to SQL Server: {e}")
            self.conn = None # Ensure conn is None if connection fails

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        spider.logger.info("MsSQLPipeline: Disconnected from SQL Server database.")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        spider.logger.info(f"MsSQLPipeline: Processing item: {adapter.get('title')}")

        if not self.conn:
            spider.logger.warning("MsSQLPipeline: No database connection, skipping item.")
            return item # Return item so it's not dropped by Scrapy by default

        try:
            # Log the data before insertion
            spider.logger.debug(f"MsSQLPipeline: Inserting data: "
                                f"Title: {adapter.get('title')}, Source: {adapter.get('source')}, "
                                f"Category: {adapter.get('category')}, Author: {adapter.get('author')}, "
                                f"Link: {adapter.get('link')}, Keywords: {adapter.get('keywords')}, "
                                f"Description: {adapter.get('short_description')}")

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
            spider.logger.info(f"MsSQLPipeline: Article '{adapter.get('title')}' saved to DB.")
        except Exception as e:
            self.conn.rollback() # Rollback on error
            spider.logger.error(f"MsSQLPipeline: Failed to save item to DB: '{adapter.get('title')}' - Error: {e}")
        return item