import scrapy
import json
import os
import re
from datetime import datetime
from hashlib import sha1

class StatutesRecursiveSpider(scrapy.Spider):
    name = "statutes_recursive_spider"
    allowed_domains = ["leg.state.fl.us"]

    custom_settings = {
        'RETRY_TIMES': 3,
        'DOWNLOAD_TIMEOUT': 15,
        'DOWNLOAD_DELAY': 1.5,  # Added download delay
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toc = {}
        self.db_path = os.path.join(os.path.dirname(__file__), "..", "..", "florida_statutes.db")
        self.init_db()

    def init_db(self):
        import sqlite3
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_id INTEGER,
                name TEXT,
                FOREIGN KEY(title_id) REFERENCES Titles(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Statutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER,
                statute_number TEXT,
                title TEXT,
                url TEXT,
                UNIQUE(chapter_id, statute_number),
                FOREIGN KEY(chapter_id) REFERENCES Chapters(id)
            )
        """)
        # Create StatuteHashes table for version control
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS StatuteHashes (
                id INTEGER PRIMARY KEY,
                statute_id INTEGER,
                hash TEXT UNIQUE,
                timestamp TEXT,
                FOREIGN KEY(statute_id) REFERENCES Statutes(id)
            )
        """)
        # Create StatuteText table for storing full statute text
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS StatuteText (
                statute_id INTEGER PRIMARY KEY,
                text TEXT,
                FOREIGN KEY(statute_id) REFERENCES Statutes(id)
            )
        """)

        # Add timestamp column to StatuteHashes table
        try:
            self.cursor.execute("""
                ALTER TABLE StatuteHashes ADD COLUMN timestamp TEXT
            """)
        except sqlite3.OperationalError:
            # Column might already exist, ignore error
            pass

        # Add indexes to speed up lookups
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_title_id ON Chapters(title_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_statutes_chapter_id ON Statutes(chapter_id)")
        self.conn.commit()

    def start_requests(self):
        json_path = os.path.join(os.path.dirname(__file__), "..", "..", "titles.json")
        with open(json_path, "r") as f:
            titles = json.load(f)
        for entry in titles:
            yield scrapy.Request(entry["url"], callback=self.parse_title, errback=self.handle_error)

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.request.url}")

    def parse_title(self, response):
        self.logger.info(f"Parsing title page: {response.url}")
        links = response.css("a::attr(href)").getall()
        title_name = response.css("title::text").get()  # Extract title name
        self.toc[title_name] = {}

        # Insert title into database
        self.cursor.execute("INSERT OR IGNORE INTO Titles (name) VALUES (?)", (title_name,))
        self.conn.commit()
        title_id = self.cursor.execute("SELECT id FROM Titles WHERE name = ?", (title_name,)).fetchone()[0]

        for href in links:
            if "ContentsIndex.html" in href:
                full_url = response.urljoin(href)
                self.logger.info(f"Following chapter index: {full_url}")
                yield response.follow(full_url, callback=self.parse_chapter, meta={"title_name": title_name, "title_id": title_id})

    def parse_chapter(self, response):
        self.logger.info(f"Parsing chapter index: {response.url}")
        links = response.css("a::attr(href)").getall()
        title_name = response.meta["title_name"]
        title_id = response.meta["title_id"]
        chapter_name = None

        # Extracting chapter name
        header_text = response.css("h2::text").get()
        if header_text:
            match = re.search(r'chapter\s+([\dA-Z\-.]+)', header_text, re.IGNORECASE)
            if match:
                chapter_name = f"Chapter {match.group(1)}"

        if not chapter_name:
            self.logger.warning(f"Failed to extract chapter name from: {response.url}")
            return

        self.toc[title_name][chapter_name] = []

        # Insert chapter into database
        self.cursor.execute("INSERT OR IGNORE INTO Chapters (title_id, name) VALUES (?, ?)", (title_id, chapter_name))
        self.conn.commit()
        self.logger.debug(f"Looking up chapter in DB: title_id={title_id}, name='{chapter_name}'")

        result = self.cursor.execute(
            "SELECT id FROM Chapters WHERE title_id = ? AND name = ?",
            (title_id, chapter_name)
        ).fetchone()

        if result is None:
            self.logger.warning(f"Chapter not found in DB: title_id={title_id}, name={chapter_name}. Inserting missing chapter.")
            self.cursor.execute("INSERT INTO Chapters (title_id, name) VALUES (?, ?)", (title_id, chapter_name))
            self.conn.commit()
            chapter_id = self.cursor.execute("SELECT id FROM Chapters WHERE title_id = ? AND name = ?", (title_id, chapter_name)).fetchone()[0]
        else:
            chapter_id = result[0]

        self.logger.info(f"Found {len(links)} links in chapter page")
        # Add progress logging for chapters
        total_chapters = len(links)
        for index, href in enumerate(links, start=1):
            self.logger.info(f"Processing chapter {index} of {total_chapters}: {href}")
            if "Sections" in href and href.endswith(".html"):
                full_url = response.urljoin(href)
                self.logger.info(f"Following statute link: {full_url}")
                yield response.follow(full_url, callback=self.parse_statute, meta={"title_name": title_name, "chapter_name": chapter_name, "chapter_id": chapter_id})

    def parse_statute(self, response):
        self.logger.info(f"Parsing statute page: {response.url}")

        statute_number = response.css("span.SectionNumber::text").get()
        statute_title = response.css("span.CatchlineText::text").get()
        body_parts = response.css("div.Section *::text").getall()
        # Format statute text for better readability
        text = "\n".join(part.strip() for part in body_parts if part.strip())

        if not statute_number:
            self.logger.warning(f"Missing SectionNumber on: {response.url}")
        else:
            self.logger.info(f"Scraped statute {statute_number} — {statute_title}")

        title_name = response.meta.get("title_name")
        chapter_name = response.meta.get("chapter_name")
        chapter_id = response.meta.get("chapter_id")
        self.toc[title_name][chapter_name].append({
            "statute_number": statute_number,
            "title": statute_title,
            "url": response.url,
        })

        # Insert statute into database
        self.cursor.execute("INSERT OR IGNORE INTO Statutes (chapter_id, statute_number, title, url) VALUES (?, ?, ?, ?)", (chapter_id, statute_number, statute_title, response.url))
        self.conn.commit()

        # Generate hash for statute text and insert into StatuteHashes
        statute_hash = sha1(text.encode("utf-8")).hexdigest()
        statute_id = self.cursor.execute("SELECT id FROM Statutes WHERE chapter_id = ? AND statute_number = ?", (chapter_id, statute_number)).fetchone()[0]
        self.cursor.execute("INSERT OR IGNORE INTO StatuteHashes (statute_id, hash, timestamp) VALUES (?, ?, ?)", (statute_id, statute_hash, datetime.now().isoformat()))
        self.conn.commit()

        # Insert or replace full statute text into StatuteText table
        self.cursor.execute("""
            INSERT OR REPLACE INTO StatuteText (statute_id, text)
            VALUES (?, ?)
        """, (statute_id, text))

        # Log or save invalid statutes for review
        if not statute_number or not statute_title:
            self.logger.warning(f"Invalid statute data: statute_number={statute_number}, title={statute_title}, url={response.url}")
            with open("invalid_statutes.csv", "a") as f:
                f.write(f"{datetime.now().isoformat()},{response.url},{statute_number},{statute_title}\n")

        yield {
            "url": response.url,
            "statute_number": statute_number,
            "title": statute_title,
            "text": text,
            "parent_title": title_name,
            "parent_chapter": chapter_name,
        }

    def closed(self, reason):
        for title, chapters in self.toc.items():
            for chapter, statutes in chapters.items():
                self.logger.info(f"Final count for {title} — {chapter}: {len(statutes)} statutes")
        # Save TOC
        toc_path = os.path.join(os.path.dirname(__file__), "..", "..", "toc.json")
        with open(toc_path, "w") as f:
            json.dump(self.toc, f, indent=4)
        self.logger.info(f"Exported TOC to {toc_path}")
        self.conn.close()
