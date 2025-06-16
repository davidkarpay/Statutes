import os
import sqlite3
import pytest
from unittest import mock
from bs4 import BeautifulSoup
from Statutes_at_5 import main


def fake_fetch_html(url, *args, **kwargs):
    """Return deterministic HTML content based on the requested URL."""
    if "Mode=View%20Statutes" in url:
        html = (
            '<table id="maintable">'
            '<a href="index.cfm?App_mode=Display_Index&Title_Request=TITLE I">'
            'TITLE I</a></table>'
        )
    elif "App_mode=Display_Index" in url and "Title_Request=TITLE I" in url:
        html = (
            '<a href="index.cfm?App_mode=Display_Statute&URL=Chapter1/ContentsIndex.html&StatuteYear=2023">'
            'Chapter 1</a>'
        )
    elif "ContentsIndex.html" in url:
        html = (
            '<a href="index.cfm?App_mode=Display_Statute&URL=Chapter1/Sections/0001.01.html">'
            '1.01</a>'
        )
    elif "Sections/0001.01.html" in url:
        html = (
            '<h2>1.01 Statute Title</h2>'
            '<table id="maintable"><p>(1) Statute text.</p></table>'
        )
    else:
        return None, None
    soup = BeautifulSoup(html, "html.parser")
    return soup, html.encode()

def test_resumability(tmp_path):
    db_file = tmp_path / "test_statutes.db"
    # Set up config.ini for test
    with open("config.ini", "w") as f:
        f.write(f"""[DEFAULT]
db_file = {db_file}
rate_limit_seconds = 0
user_agent = test-agent
index_url = http://www.leg.state.fl.us/Statutes/index.cfm?Mode=View%20Statutes&Submenu=1&Tab=statutes
""")
    # Patch required_titles and fetch_html so the test does not hit the network
    with mock.patch("Statutes_at_5.required_titles", ["TITLE I"]), \
         mock.patch("Statutes_at_5.fetch_html", side_effect=fake_fetch_html):
        main()
        # Simulate interruption: mark one statute as incomplete
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("UPDATE Statutes SET completed=0 WHERE id=(SELECT id FROM Statutes LIMIT 1)")
        conn.commit()
        conn.close()
        # Run main() again (should resume and complete the incomplete statute)
        main()
        # Check all statutes are completed
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Statutes WHERE completed=0")
        incomplete = cur.fetchone()[0]
        conn.close()
        assert incomplete == 0, "All statutes should be marked as completed after resuming."

if __name__ == "__main__":
    pytest.main([__file__])
