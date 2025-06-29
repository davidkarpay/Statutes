import sqlite3

class FlStatutesPipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect("florida_statutes.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                statute_number TEXT,
                title TEXT,
                text TEXT
            )
        """)
        self.connection.commit()

    def process_item(self, item, spider):
        self.cursor.execute("""
            INSERT INTO statutes (url, statute_number, title, text) VALUES (?, ?, ?, ?)
        """, (item['url'], item['statute_number'], item['title'], item['text']))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.connection.close()
